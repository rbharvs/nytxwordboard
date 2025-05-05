import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import httpx

from .config import get_settings
from .models import DailyScoreItem, UserMetadataItem

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()


async def fetch_user_stats(user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Fetches a user's statistics from the NYT Crossword API.

    Args:
        user_id: The user ID to fetch statistics for

    Returns:
        Tuple of (success, data) where success is a boolean and data is the parsed JSON or None
    """
    url = settings.NYT_API_URL_TEMPLATE.format(user_id)
    logger.info(f"Fetching stats for user {user_id} from {url}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()
            if data.get("status") != "OK":
                logger.warning(
                    f"API returned non-OK status for user {user_id}: {data.get('status')}"
                )
                return False, None

            return True, data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"User {user_id} not found (404)")
        else:
            logger.error(f"HTTP error fetching stats for user {user_id}: {e}")
        return False, None

    except httpx.RequestError as e:
        logger.error(f"Request error fetching stats for user {user_id}: {e}")
        return False, None

    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON response for user {user_id}")
        return False, None

    except Exception as e:
        logger.error(f"Unexpected error fetching stats for user {user_id}: {e}")
        return False, None


def extract_daily_scores(
    stats_data: Dict[str, Any], user_id: str
) -> list[DailyScoreItem]:
    """
    Extracts daily scores from the stats data response.

    Args:
        stats_data: The parsed JSON response from the API
        user_id: The user ID

    Returns:
        List of DailyScoreItem objects
    """
    score_items = []

    try:
        # Navigate through the nested JSON structure
        stats_by_day = (
            stats_data.get("results", {}).get("stats", {}).get("stats_by_day", [])
        )

        # Process each day's data
        for day_data in stats_by_day:
            # Skip days with no data
            if not day_data.get("latest_date") or not day_data.get("latest_time"):
                continue

            date = day_data.get("latest_date")
            score = day_data.get("latest_time")

            if date and score and score > 0:
                score_items.append(
                    DailyScoreItem(userId=user_id, date=date, score=score)
                )

    except Exception as e:
        logger.error(f"Error extracting daily scores: {e}")

    return score_items


def extract_user_metadata(
    stats_data: Dict[str, Any], user_id: str
) -> Optional[UserMetadataItem]:
    """
    Extracts metadata about the user from the stats data response.

    Args:
        stats_data: The parsed JSON response from the API
        user_id: The user ID

    Returns:
        UserMetadataItem object or None if extraction fails
    """
    try:
        stats = stats_data.get("results", {}).get("stats", {})
        streaks = stats_data.get("results", {}).get("streaks", {})

        metadata = UserMetadataItem(
            userId=user_id,
            last_fetched_timestamp=int(datetime.now().timestamp()),
            puzzles_attempted=stats.get("puzzles_attempted", 0),
            puzzles_solved=stats.get("puzzles_solved", 0),
            solve_rate=stats.get("solve_rate", 0.0),
            current_streak=streaks.get("current_streak", 0),
        )

        return metadata

    except Exception as e:
        logger.error(f"Error extracting user metadata for {user_id}: {e}")
        return None
