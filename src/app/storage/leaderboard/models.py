"""Models for leaderboard storage operations."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field
from returns.result import Result

from app.core.error import StorageError
from app.storage.models import Date, UserMetadataKey


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard."""

    rank: int = Field(
        ...,
        description="Position in the leaderboard ranking",
        ge=1,
    )
    user_id: UserMetadataKey = Field(..., description="User identifier")
    score: int = Field(
        ...,
        description="User's score/time for the puzzle in seconds",
        ge=0,
    )

    model_config = ConfigDict(frozen=True)


class GetDailyLeaderboardQuery(BaseModel):
    """Query parameters for getting a daily leaderboard."""

    date: Date = Field(..., description="Date in YYYY-MM-DD format")
    limit: int = Field(
        default=100, ge=1, le=500, description="Maximum number of results to return"
    )

    model_config = ConfigDict(frozen=True)


class GetDailyLeaderboardReply(BaseModel):
    """Response data for get_daily_leaderboard operation."""

    date: Date = Field(..., description="Date of the leaderboard in YYYY-MM-DD format")
    entries: List[LeaderboardEntry] = Field(
        default_factory=list, description="List of users ranked by score"
    )
    total_count: int = Field(
        ..., description="Total number of entries in the leaderboard", ge=0
    )

    model_config = ConfigDict(frozen=True)


type GetDailyLeaderboardResult = Result[GetDailyLeaderboardReply, StorageError]
