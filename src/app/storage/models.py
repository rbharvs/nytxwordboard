"""Core models for storage layer."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

type UserMetadataKey = Annotated[
    str,
    Field(
        description="User identifier matching the required pattern.",
        pattern=r"^[1-9]\d*",
        min_length=1,
        max_length=12,
    ),
]

type Date = Annotated[
    str,
    Field(
        description="Date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    ),
]


class UserMetadataItem(BaseModel):
    """User metadata stored in the database."""

    user_id: UserMetadataKey = Field(
        ...,
        description="User identifier",
    )
    last_fetched_timestamp: int = Field(
        ...,
        description="Unix timestamp when user data was last fetched",
        ge=0,
    )
    puzzles_attempted: int = Field(
        ...,
        description="Number of puzzles attempted by user",
        ge=0,
    )
    puzzles_solved: int = Field(
        ...,
        description="Number of puzzles successfully solved by user",
        ge=0,
    )
    current_streak: int = Field(
        ...,
        description="Current streak of consecutive daily puzzles solved",
        ge=0,
    )

    model_config = ConfigDict(frozen=True)

    @property
    def key(self) -> UserMetadataKey:
        """Get the storage key for this item.

        Returns:
            The user ID which serves as the storage key
        """
        return self.user_id


class DailyScoreKey(BaseModel):
    """Composite key for daily scores."""

    user_id: UserMetadataKey = Field(description="ID of the user")
    date: Date = Field(
        description="Date of the puzzle in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    model_config = ConfigDict(frozen=True)


class DailyScoreItem(BaseModel):
    """Daily score record stored in the database."""

    user_id: UserMetadataKey = Field(..., description="User identifier")
    date: Date = Field(..., description="Date of the puzzle in YYYY-MM-DD format")
    score: int = Field(..., description="User's score/time for the puzzle")

    model_config = ConfigDict(frozen=True)

    @property
    def key(self) -> DailyScoreKey:
        """Get the storage key for this item.

        Returns:
            A ScoreKey composed of the user_id and date
        """
        return DailyScoreKey(user_id=self.user_id, date=self.date)
