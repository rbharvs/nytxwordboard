"""Tests for in-memory leaderboard storage implementation."""

from typing import Generator

import pytest
from returns.result import Success

from app.storage.leaderboard.memory import InMemoryLeaderboardStorage
from app.storage.leaderboard.models import GetDailyLeaderboardQuery
from app.storage.memory_context import InMemoryStorageContext
from app.storage.models import DailyScoreItem
from app.storage.users.memory import InMemoryUserStorage
from app.storage.users.models import SaveDailyScoreQuery


@pytest.fixture
def memory_context() -> Generator[InMemoryStorageContext, None, None]:
    """Create a fresh in-memory storage context for each test."""
    context = InMemoryStorageContext()
    yield context
    context.clear()


@pytest.fixture
def user_storage(memory_context: InMemoryStorageContext) -> InMemoryUserStorage:
    """Create an in-memory user storage instance with the shared context."""
    return InMemoryUserStorage(memory_context)


@pytest.fixture
def leaderboard_storage(
    memory_context: InMemoryStorageContext,
) -> InMemoryLeaderboardStorage:
    """Create an in-memory leaderboard storage instance with the shared context."""
    return InMemoryLeaderboardStorage(memory_context)


def test_get_daily_leaderboard_empty(
    leaderboard_storage: InMemoryLeaderboardStorage,
) -> None:
    """Test that getting a leaderboard with no entries returns an empty list."""
    query = GetDailyLeaderboardQuery(date="2023-01-01")
    result = leaderboard_storage.get_daily_leaderboard(query)

    assert isinstance(result, Success)
    reply = result.unwrap()
    assert reply.date == "2023-01-01"
    assert reply.entries == []
    assert reply.total_count == 0


def test_get_daily_leaderboard_with_scores(
    user_storage: InMemoryUserStorage,
    leaderboard_storage: InMemoryLeaderboardStorage,
) -> None:
    """Test that getting a leaderboard with scores returns the correct data."""
    # Prepare test data - add scores using the user_storage
    date = "2023-01-01"
    test_scores = [
        DailyScoreItem(user_id="123", date=date, score=120),
        DailyScoreItem(user_id="456", date=date, score=90),
        DailyScoreItem(user_id="789", date=date, score=180),
    ]

    for score_item in test_scores:
        query = SaveDailyScoreQuery(item=score_item)
        user_storage.save_daily_score(query)

    # Execute the query
    leaderboard_query = GetDailyLeaderboardQuery(date=date)
    result = leaderboard_storage.get_daily_leaderboard(leaderboard_query)

    # Verify the result
    assert isinstance(result, Success)
    reply = result.unwrap()
    assert reply.date == date
    assert len(reply.entries) == 3
    assert reply.total_count == 3

    # Verify the leaderboard entries are sorted by score (lowest first)
    assert reply.entries[0].user_id == "456"  # score 90
    assert reply.entries[0].rank == 1
    assert reply.entries[0].score == 90

    assert reply.entries[1].user_id == "123"  # score 120
    assert reply.entries[1].rank == 2
    assert reply.entries[1].score == 120

    assert reply.entries[2].user_id == "789"  # score 180
    assert reply.entries[2].rank == 3
    assert reply.entries[2].score == 180


def test_get_daily_leaderboard_limit(
    user_storage: InMemoryUserStorage,
    leaderboard_storage: InMemoryLeaderboardStorage,
) -> None:
    """Test that limit parameter correctly restricts the number of results."""
    # Prepare test data - add 5 scores
    date = "2023-01-01"
    test_scores = [
        DailyScoreItem(user_id="1", date=date, score=100),
        DailyScoreItem(user_id="2", date=date, score=200),
        DailyScoreItem(user_id="3", date=date, score=300),
        DailyScoreItem(user_id="4", date=date, score=400),
        DailyScoreItem(user_id="5", date=date, score=500),
    ]

    for score_item in test_scores:
        query = SaveDailyScoreQuery(item=score_item)
        user_storage.save_daily_score(query)

    # Execute the query with limit=3
    leaderboard_query = GetDailyLeaderboardQuery(date=date, limit=3)
    result = leaderboard_storage.get_daily_leaderboard(leaderboard_query)

    # Verify only top 3 results are returned
    assert isinstance(result, Success)
    reply = result.unwrap()
    assert len(reply.entries) == 3
    assert reply.total_count == 3
    assert reply.entries[0].user_id == "1"  # score 100
    assert reply.entries[1].user_id == "2"  # score 200
    assert reply.entries[2].user_id == "3"  # score 300


def test_get_daily_leaderboard_multiple_dates(
    user_storage: InMemoryUserStorage,
    leaderboard_storage: InMemoryLeaderboardStorage,
) -> None:
    """Test that leaderboards for different dates are separate."""
    # Prepare test data for two different dates
    date1 = "2023-01-01"
    date2 = "2023-01-02"

    # Add scores for date1
    for user_id, score in [("1", 100), ("2", 200)]:
        user_storage.save_daily_score(
            SaveDailyScoreQuery(
                item=DailyScoreItem(user_id=user_id, date=date1, score=score)
            )
        )

    # Add scores for date2
    for user_id, score in [("1", 150), ("3", 250)]:
        user_storage.save_daily_score(
            SaveDailyScoreQuery(
                item=DailyScoreItem(user_id=user_id, date=date2, score=score)
            )
        )

    # Get leaderboard for date1
    query1 = GetDailyLeaderboardQuery(date=date1)
    result1 = leaderboard_storage.get_daily_leaderboard(query1)
    reply1 = result1.unwrap()

    # Get leaderboard for date2
    query2 = GetDailyLeaderboardQuery(date=date2)
    result2 = leaderboard_storage.get_daily_leaderboard(query2)
    reply2 = result2.unwrap()

    # Verify date1 leaderboard
    assert len(reply1.entries) == 2
    assert reply1.entries[0].user_id == "1"
    assert reply1.entries[0].score == 100
    assert reply1.entries[1].user_id == "2"
    assert reply1.entries[1].score == 200

    # Verify date2 leaderboard
    assert len(reply2.entries) == 2
    assert reply2.entries[0].user_id == "1"
    assert reply2.entries[0].score == 150
    assert reply2.entries[1].user_id == "3"
    assert reply2.entries[1].score == 250
