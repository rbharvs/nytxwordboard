"""In-memory implementation of user storage."""

from returns.result import Failure, Success

from app.core.error import NotFoundDetails, NotFoundStorageError
from app.storage.memory_context import InMemoryStorageContext
from app.storage.models import UserMetadataItem
from app.storage.users.interface import UserStorage
from app.storage.users.models import (
    GetAllUserIdsQuery,
    GetAllUserIdsReply,
    GetAllUserIdsResult,
    GetUserMetadataQuery,
    GetUserMetadataReply,
    GetUserMetadataResult,
    SaveDailyScoreQuery,
    SaveDailyScoreReply,
    SaveDailyScoreResult,
    SaveUserMetadataQuery,
    SaveUserMetadataReply,
    SaveUserMetadataResult,
)


class InMemoryUserStorage(UserStorage):
    """In-memory implementation of user storage for testing purposes."""

    def __init__(self, context: InMemoryStorageContext) -> None:
        """Initialize the in-memory user storage.

        Args:
            context: Shared in-memory storage context
        """
        self.context = context

    def get_user_metadata(self, query: GetUserMetadataQuery) -> GetUserMetadataResult:
        """Get user metadata from in-memory storage."""
        if query.user_id not in self.context.users:
            return Failure(
                NotFoundStorageError(
                    details=NotFoundDetails(
                        resource_type=UserMetadataItem.__name__,
                        resource_id=query.user_id,
                    ),
                    service_name=self.__class__.__name__,
                )
            )
        metadata = self.context.users[query.user_id]
        return Success(GetUserMetadataReply(item=metadata))

    def save_daily_score(self, query: SaveDailyScoreQuery) -> SaveDailyScoreResult:
        """Save a daily score to in-memory storage."""
        self.context.scores[query.item.key] = query.item
        return Success(SaveDailyScoreReply())

    def save_user_metadata(
        self, query: SaveUserMetadataQuery
    ) -> SaveUserMetadataResult:
        """Save user metadata to in-memory storage."""
        self.context.users[query.item.key] = query.item
        return Success(SaveUserMetadataReply())

    def get_all_user_ids(self, query: GetAllUserIdsQuery) -> GetAllUserIdsResult:
        """Get all user IDs from in-memory storage."""
        user_ids = list(self.context.users.keys())
        return Success(GetAllUserIdsReply(user_ids=user_ids))
