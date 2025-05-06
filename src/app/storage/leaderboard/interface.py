"""Leaderboard storage interface definition."""

from typing import Protocol

from app.storage.leaderboard.models import (
    GetDailyLeaderboardQuery,
    GetDailyLeaderboardResult,
)


class LeaderboardStorage(Protocol):
    """Interface for leaderboard data storage operations."""

    def get_daily_leaderboard(
        self, query: GetDailyLeaderboardQuery
    ) -> GetDailyLeaderboardResult:
        """Get daily leaderboard.

        Args:
            query: Parameters for the query

        Returns:
            Result containing leaderboard data if successful, or one of these errors:
                - UnavailableStorageError: If the backing storage is temporarily unavailable
                - InternalStorageError: If another implementation-dependent error occurs
        """
        ...
