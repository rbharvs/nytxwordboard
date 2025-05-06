"""User storage interface definition."""

from typing import Protocol

from app.storage.users.models import (
    GetAllUserIdsQuery,
    GetAllUserIdsResult,
    GetUserMetadataQuery,
    GetUserMetadataResult,
    SaveDailyScoreQuery,
    SaveDailyScoreResult,
    SaveUserMetadataQuery,
    SaveUserMetadataResult,
)


class UserStorage(Protocol):
    """Interface for user data storage operations."""

    def get_user_metadata(self, query: GetUserMetadataQuery) -> GetUserMetadataResult:
        """Get user metadata.

        Args:
            query: Parameters for the query

        Returns:
            Result containing user metadata if successful, or one of these errors:
                - NotFoundStorageError: If the user ID isn't found
                - UnavailableStorageError: If the backing storage is temporarily unavailable
                - InternalStorageError: If another implementation-dependent error occurs
        """
        ...

    def save_daily_score(self, query: SaveDailyScoreQuery) -> SaveDailyScoreResult:
        """Save a daily score for a user.

        Args:
            query: Daily score information to save

        Returns:
            Result indicating success, or one of these errors:
                - NotFoundStorageError: If the user ID doesn't exist and is required
                - UnavailableStorageError: If the backing storage is temporarily unavailable
                - InternalStorageError: If another implementation-dependent error occurs
        """
        ...

    def save_user_metadata(
        self, query: SaveUserMetadataQuery
    ) -> SaveUserMetadataResult:
        """Save user metadata.

        Args:
            query: User metadata to save

        Returns:
            Result indicating success, or one of these errors:
                - UnavailableStorageError: If the backing storage is temporarily unavailable
                - InternalStorageError: If another implementation-dependent error occurs
        """
        ...

    def get_all_user_ids(self, query: GetAllUserIdsQuery) -> GetAllUserIdsResult:
        """Get all user IDs.

        Args:
            query: Parameters for the query

        Returns:
            Result containing list of all user IDs if successful, or one of these errors:
                - UnavailableStorageError: If the backing storage is temporarily unavailable
                - InternalStorageError: If another implementation-dependent error occurs
        """
        ...
