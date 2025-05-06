"""In-memory storage context for testing purposes."""

from typing import Dict

from app.storage.models import (
    DailyScoreItem,
    DailyScoreKey,
    UserMetadataItem,
    UserMetadataKey,
)


class InMemoryStorageContext:
    """In-memory storage context used for testing storage implementations.

    This context maintains shared state across different in-memory storage
    implementations, simulating a real database where different storage components
    may interact with the same underlying data.
    """

    def __init__(self) -> None:
        """Initialize the in-memory storage context."""
        # Map from user_id to UserMetadataItem
        self.users: Dict[UserMetadataKey, UserMetadataItem] = {}

        # Map from ScoreKey to DailyScoreItem
        self.scores: Dict[DailyScoreKey, DailyScoreItem] = {}

    def clear(self) -> None:
        """Clear all data in the storage context."""
        self.users.clear()
        self.scores.clear()
