import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from .config import get_settings
from .models import DailyScoreItem, LeaderboardEntry, UserMetadataItem

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Initialize DynamoDB resources
dynamodb_client = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(settings.DYNAMODB_TABLE_NAME)

# Helpers for DynamoDB type conversions
deserializer = TypeDeserializer()
serializer = TypeSerializer()


def dynamodb_to_python(dynamodb_item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a DynamoDB item to a Python dictionary."""
    if not dynamodb_item:
        return {}
    return {k: deserializer.deserialize(v) for k, v in dynamodb_item.items()}


def python_to_dynamodb(python_item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Python dictionary to a DynamoDB item."""
    if not python_item:
        return {}
    return {k: serializer.serialize(v) for k, v in python_item.items()}


async def get_daily_leaderboard(date: str, limit: int = 100) -> List[LeaderboardEntry]:
    """
    Queries the GSI to get the top N scores for a specific date.

    Args:
        date: The date in YYYY-MM-DD format
        limit: Maximum number of results to return (default: 100)

    Returns:
        A list of LeaderboardEntry objects sorted by score (lowest first)
    """
    gsi_pk = f"DATE#{date}"
    logger.info(f"Querying leaderboard for date: {date} (GSI PK: {gsi_pk})")

    try:
        # Query the GSI for the given date
        response = dynamodb_client.query(
            TableName=settings.DYNAMODB_TABLE_NAME,
            IndexName=settings.DYNAMODB_GSI_NAME,
            KeyConditionExpression="gsi1_pk = :pk",
            ExpressionAttributeValues={":pk": {"S": gsi_pk}},
            # Lower scores are better (less time), so use ascending sort
            ScanIndexForward=True,
            Limit=limit,
        )

        items = response.get("Items", [])
        leaderboard_entries: List[LeaderboardEntry] = []
        rank = 1

        for item in items:
            # Convert DynamoDB types to Python types
            deserialized_item = dynamodb_to_python(item)

            user_id = deserialized_item.get("userId")
            score = deserialized_item.get("gsi1_sk")  # Score is the GSI Sort Key
            item_date = deserialized_item.get("date")

            if user_id and score is not None and item_date:
                # Convert Decimal to int if it's a whole number
                if isinstance(score, Decimal):
                    score_value = int(score) if score % 1 == 0 else float(score)
                else:
                    score_value = int(score) if isinstance(score, int) else score

                leaderboard_entries.append(
                    LeaderboardEntry(
                        rank=rank,
                        userId=str(user_id),
                        score=int(score_value),
                        date=str(item_date),
                    )
                )
                rank += 1
            else:
                logger.warning(
                    f"Skipping item due to missing data: {deserialized_item}"
                )

        logger.info(f"Found {len(leaderboard_entries)} entries for {date}")
        return leaderboard_entries

    except Exception as e:
        logger.error(f"Error querying leaderboard for {date}: {e}")
        # In a production scenario, consider re-raising a custom exception
        return []


async def get_user_metadata(user_id: str) -> Optional[UserMetadataItem]:
    """
    Fetches user metadata from DynamoDB.

    Args:
        user_id: The user ID to fetch

    Returns:
        UserMetadataItem if found, None otherwise
    """
    try:
        response = table.get_item(Key={"PK": f"USER#{user_id}", "SK": "METADATA"})

        item = response.get("Item")
        if not item:
            return None

        # Convert from DynamoDB format to Pydantic model
        return UserMetadataItem(
            userId=str(item.get("userId", "")),
            last_fetched_timestamp=int(item.get("last_fetched_timestamp", 0)),
            puzzles_attempted=int(item.get("puzzles_attempted", 0)),
            puzzles_solved=int(item.get("puzzles_solved", 0)),
            solve_rate=float(item.get("solve_rate", 0.0)),
            current_streak=int(item.get("current_streak", 0)),
        )

    except Exception as e:
        logger.error(f"Error getting user metadata for {user_id}: {e}")
        return None


async def save_daily_score(score_item: DailyScoreItem) -> bool:
    """
    Saves a user's daily score to DynamoDB.

    Args:
        score_item: DailyScoreItem with user's score data

    Returns:
        True if successful, False if an error occurred
    """
    try:
        # Create the item to be saved using Pydantic model
        item = {
            "PK": f"USER#{score_item.user_id}",
            "SK": f"SCORE#{score_item.date}",
            "type": "DAILY_SCORE",
            "userId": score_item.user_id,
            "date": score_item.date,
            "score": score_item.score,
            "gsi1_pk": f"DATE#{score_item.date}",
            "gsi1_sk": score_item.score,
        }

        # Save to DynamoDB
        table.put_item(Item=item)
        logger.info(
            f"Saved score for user {score_item.user_id} on {score_item.date}: {score_item.score}"
        )
        return True

    except Exception as e:
        logger.error(
            f"Error saving score for user {score_item.user_id} on {score_item.date}: {e}"
        )
        return False


async def update_user_metadata(metadata_item: UserMetadataItem) -> bool:
    """
    Updates a user's metadata in DynamoDB using the Pydantic model.

    Args:
        metadata_item: UserMetadataItem with user metadata

    Returns:
        True if successful, False if an error occurred
    """
    try:
        # Convert model to dictionary and create the item
        metadata_dict = metadata_item.model_dump(by_alias=True)

        # Convert solve_rate to Decimal for DynamoDB compatibility
        if "solve_rate" in metadata_dict:
            metadata_dict["solve_rate"] = Decimal(str(metadata_dict["solve_rate"]))

        # Create the DynamoDB item
        item = {
            "PK": f"USER#{metadata_item.user_id}",
            "SK": "METADATA",
            "type": "USER_METADATA",
            **metadata_dict,
        }

        # Save to DynamoDB
        table.put_item(Item=item)
        logger.info(f"Updated metadata for user {metadata_item.user_id}")
        return True

    except Exception as e:
        logger.error(f"Error updating metadata for user {metadata_item.user_id}: {e}")
        return False


async def create_user_if_not_exists(metadata_item: UserMetadataItem) -> bool:
    """
    Creates a new user if one doesn't already exist.

    Args:
        metadata_item: UserMetadataItem with user metadata

    Returns:
        True if user was created or already exists, False if an error occurred
    """
    try:
        # Convert model to dictionary and create the item
        metadata_dict = metadata_item.model_dump(by_alias=True)

        # Convert solve_rate to Decimal for DynamoDB compatibility
        if "solve_rate" in metadata_dict:
            metadata_dict["solve_rate"] = Decimal(str(metadata_dict["solve_rate"]))

        # Create the DynamoDB item
        item = {
            "PK": f"USER#{metadata_item.user_id}",
            "SK": "METADATA",
            "type": "USER_METADATA",
            **metadata_dict,
        }

        # Use condition expression to avoid overwriting existing user
        table.put_item(Item=item, ConditionExpression="attribute_not_exists(PK)")
        logger.info(f"Created new user {metadata_item.user_id}")
        return True

    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            # User already exists, which is fine
            logger.info(f"User {metadata_item.user_id} already exists")
            return True
        else:
            logger.error(f"Error creating user {metadata_item.user_id}: {e}")
            return False


async def get_all_user_ids() -> List[str]:
    """
    Retrieves all user IDs from the DynamoDB table.

    Returns:
        List of user IDs
    """
    user_ids = []
    try:
        # Query for all items with PK starting with USER#
        response = dynamodb_client.scan(
            TableName=settings.DYNAMODB_TABLE_NAME,
            FilterExpression="begins_with(PK, :prefix) AND SK = :metadata",
            ExpressionAttributeValues={
                ":prefix": {"S": "USER#"},
                ":metadata": {"S": "METADATA"},
            },
            ProjectionExpression="userId",
        )

        # Extract user IDs from results
        items = response.get("Items", [])
        for item in items:
            user_id = dynamodb_to_python(item).get("userId")
            if user_id:
                user_ids.append(str(user_id))

        logger.info(f"Retrieved {len(user_ids)} user IDs from database")
        return user_ids

    except Exception as e:
        logger.error(f"Error retrieving user IDs: {e}")
        return []
