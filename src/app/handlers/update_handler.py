import asyncio
import json
import logging
from typing import Any, Dict, List

from app.core import database, external_api

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def process_user(user_id: str) -> Dict[str, Any]:
    """
    Process a single user: fetch their data and update database.

    Args:
        user_id: User ID to process

    Returns:
        Dictionary with processing results
    """
    logger.info(f"Processing user {user_id}")
    result = {
        "userId": user_id,
        "success": False,
        "scores_updated": 0,
        "metadata_updated": False,
        "error": None,
    }

    try:
        # Fetch user data from NYT API
        success, stats_data = await external_api.fetch_user_stats(user_id)

        if not success or not stats_data:
            result["error"] = "Failed to fetch user data from API"
            return result

        # Extract user metadata
        metadata = external_api.extract_user_metadata(stats_data, user_id)
        if not metadata:
            result["error"] = "Failed to extract user metadata"
            return result

        # Extract daily scores
        score_items = external_api.extract_daily_scores(stats_data, user_id)
        if not score_items:
            logger.warning(f"No scores found for user {user_id}")

        # Update metadata in database
        metadata_success = await database.update_user_metadata(metadata)
        result["metadata_updated"] = metadata_success

        # Update scores in database
        scores_updated = 0
        for score_item in score_items:
            if await database.save_daily_score(score_item):
                scores_updated += 1

        result["scores_updated"] = scores_updated
        result["success"] = metadata_success and scores_updated == len(score_items)

        return result

    except Exception as e:
        logger.error(f"Error processing user {user_id}: {e}")
        result["error"] = str(e)
        return result


async def process_users(user_ids: List[str]) -> Dict[str, Any]:
    """
    Process multiple users concurrently.

    Args:
        user_ids: List of user IDs to process

    Returns:
        Dictionary with processing results
    """
    logger.info(f"Processing {len(user_ids)} users")

    # Process users concurrently
    tasks = [process_user(user_id) for user_id in user_ids]
    results = await asyncio.gather(*tasks)

    # Summarize results
    success_count = sum(1 for r in results if r["success"])
    scores_updated = sum(r["scores_updated"] for r in results)

    return {
        "total_users": len(user_ids),
        "successful_users": success_count,
        "failed_users": len(user_ids) - success_count,
        "total_scores_updated": scores_updated,
        "user_results": results,
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function for processing user data updates.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context

    Returns:
        Result dictionary
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Always fetch all users from the database
    logger.info("Fetching all users from database")
    user_ids = asyncio.run(database.get_all_user_ids())
    
    if not user_ids:
        logger.warning("No users found in database")
        return {
            "statusCode": 200, 
            "body": json.dumps({
                "message": "No users found in database",
                "total_users": 0
            })
        }

    # Run the async processing
    results = asyncio.run(process_users(user_ids))

    logger.info(f"Completed processing {len(user_ids)} users")
    return {"statusCode": 200, "body": json.dumps(results)}
