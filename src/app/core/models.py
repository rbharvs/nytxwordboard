from typing import List

from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard."""

    rank: int = Field(..., description="Position in the leaderboard ranking")
    user_id: str = Field(..., description="User identifier", alias="userId")
    score: int = Field(..., description="User's score/time for the puzzle")
    date: str = Field(..., description="Date of the puzzle in YYYY-MM-DD format")

    model_config = {"populate_by_name": True}


class DailyLeaderboardResponse(BaseModel):
    """Response model for a daily leaderboard query."""

    date: str = Field(..., description="Date of the leaderboard in YYYY-MM-DD format")
    entries: List[LeaderboardEntry] = Field(
        default_factory=list, description="List of users ranked by score"
    )
    total_count: int = Field(
        ..., description="Total number of entries in the leaderboard"
    )
