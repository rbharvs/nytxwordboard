"""In-memory implementation of leaderboard storage."""

from returns.result import Success

from app.storage.leaderboard.interface import LeaderboardStorage
from app.storage.leaderboard.models import (
    GetDailyLeaderboardQuery,
    GetDailyLeaderboardReply,
    GetDailyLeaderboardResult,
    LeaderboardEntry,
)
from app.storage.memory_context import InMemoryStorageContext


class InMemoryLeaderboardStorage(LeaderboardStorage):
    """In-memory implementation of leaderboard storage for testing purposes."""

    def __init__(self, context: InMemoryStorageContext) -> None:
        """Initialize the in-memory leaderboard storage.

        Args:
            context: Shared in-memory storage context
        """
        self.context = context

    def get_daily_leaderboard(
        self, query: GetDailyLeaderboardQuery
    ) -> GetDailyLeaderboardResult:
        """Get daily leaderboard from in-memory storage."""
        # Collect all scores for the given date
        date_scores = []
        for key, score_item in self.context.scores.items():
            if key.date == query.date:
                date_scores.append(score_item)

        # Sort scores (lower is better)
        sorted_scores = sorted(date_scores, key=lambda s: s.score)

        # Apply limit
        limited_scores = sorted_scores[: query.limit]

        # Format as leaderboard entries
        entries = []
        for rank, score_item in enumerate(limited_scores, start=1):
            entries.append(
                LeaderboardEntry(
                    rank=rank,
                    user_id=score_item.user_id,
                    score=score_item.score,
                )
            )

        # Return success result
        return Success(
            GetDailyLeaderboardReply(
                date=query.date, entries=entries, total_count=len(entries)
            )
        )
