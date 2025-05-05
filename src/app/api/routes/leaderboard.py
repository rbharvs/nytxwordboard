import logging

from fastapi import APIRouter, HTTPException, Path, Query

from app.core import database
from app.core.models import DailyLeaderboardResponse

# Create router
router = APIRouter()

# Date format validation regex
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


@router.get(
    "/leaderboard/{date}",
    response_model=DailyLeaderboardResponse,
    summary="Get leaderboard for a specific date",
)
async def get_leaderboard_for_date(
    date: str = Path(..., description="Date in YYYY-MM-DD format", regex=DATE_PATTERN),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of results to return"
    ),
):
    """
    Retrieve the leaderboard for a specific date.

    - **date**: The date in YYYY-MM-DD format
    - **limit**: Maximum number of results to return (default: 100, max: 500)

    Returns a sorted list of users ranked by their score (lowest first) for the given date.
    """
    try:
        # Query the database
        entries = await database.get_daily_leaderboard(date, limit)

        # Return the response
        return DailyLeaderboardResponse(
            date=date, entries=entries, total_count=len(entries)
        )

    except Exception as e:
        # Log the exception
        logging.error(f"Error retrieving leaderboard for {date}: {e}")

        # Return a 500 error
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving the leaderboard.",
        )
