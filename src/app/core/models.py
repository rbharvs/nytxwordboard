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


class UserMetadataItem(BaseModel):
    """User metadata stored in DynamoDB."""

    user_id: str = Field(..., description="User identifier", alias="userId")
    last_fetched_timestamp: int = Field(
        ..., description="Unix timestamp when user data was last fetched"
    )
    puzzles_attempted: int = Field(
        ..., description="Number of puzzles attempted by user"
    )
    puzzles_solved: int = Field(
        ..., description="Number of puzzles successfully solved by user"
    )
    solve_rate: float = Field(
        ..., description="Ratio of solved puzzles to attempted puzzles"
    )
    current_streak: int = Field(
        ..., description="Current streak of consecutive daily puzzles solved"
    )

    model_config = {"populate_by_name": True}


class DailyScoreItem(BaseModel):
    """Daily score record stored in DynamoDB."""

    user_id: str = Field(..., description="User identifier", alias="userId")
    date: str = Field(..., description="Date of the puzzle in YYYY-MM-DD format")
    score: int = Field(..., description="User's score/time for the puzzle")

    model_config = {"populate_by_name": True}
