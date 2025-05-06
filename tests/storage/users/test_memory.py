"""Tests for in-memory user storage implementation."""

from typing import Generator

import pytest
from returns.result import Failure, Success

from app.core.error import NotFoundStorageError
from app.storage.memory_context import InMemoryStorageContext
from app.storage.models import DailyScoreItem, DailyScoreKey, UserMetadataItem
from app.storage.users.memory import InMemoryUserStorage
from app.storage.users.models import (
    GetAllUserIdsQuery,
    GetUserMetadataQuery,
    SaveDailyScoreQuery,
    SaveUserMetadataQuery,
)


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


def test_get_user_metadata_not_found(user_storage: InMemoryUserStorage) -> None:
    """Test that getting non-existent user metadata returns a NotFoundError."""
    query = GetUserMetadataQuery(user_id="123456")
    result = user_storage.get_user_metadata(query)

    assert isinstance(result, Failure)
    error = result.failure()
    assert isinstance(error, NotFoundStorageError)
    assert error.details.resource_type == "UserMetadataItem"
    assert error.details.resource_id == "123456"


def test_get_user_metadata_success(
    user_storage: InMemoryUserStorage, memory_context: InMemoryStorageContext
) -> None:
    """Test that getting existing user metadata returns the correct data."""
    # Prepare test data
    user_id = "42"
    user_metadata = UserMetadataItem(
        user_id=user_id,
        last_fetched_timestamp=1630000000,
        puzzles_attempted=10,
        puzzles_solved=8,
        current_streak=3,
    )
    memory_context.users[user_id] = user_metadata

    # Execute the query
    query = GetUserMetadataQuery(user_id=user_id)
    result = user_storage.get_user_metadata(query)

    # Verify the result
    assert isinstance(result, Success)
    reply = result.unwrap()
    assert reply.item.user_id == user_id
    assert reply.item.last_fetched_timestamp == 1630000000
    assert reply.item.puzzles_attempted == 10
    assert reply.item.puzzles_solved == 8
    assert reply.item.current_streak == 3


def test_save_user_metadata(
    user_storage: InMemoryUserStorage, memory_context: InMemoryStorageContext
) -> None:
    """Test that saving user metadata works correctly."""
    # Prepare test data
    user_id = "123"
    user_metadata = UserMetadataItem(
        user_id=user_id,
        last_fetched_timestamp=1630000000,
        puzzles_attempted=10,
        puzzles_solved=8,
        current_streak=3,
    )

    # Execute the query
    query = SaveUserMetadataQuery(item=user_metadata)
    result = user_storage.save_user_metadata(query)

    # Verify the result
    assert isinstance(result, Success)

    # Verify the data was saved correctly
    assert user_id in memory_context.users
    saved_data = memory_context.users[user_id]
    assert isinstance(saved_data, UserMetadataItem)
    assert saved_data.user_id == user_id
    assert saved_data.last_fetched_timestamp == 1630000000
    assert saved_data.puzzles_attempted == 10
    assert saved_data.puzzles_solved == 8
    assert saved_data.current_streak == 3


def test_save_daily_score(
    user_storage: InMemoryUserStorage, memory_context: InMemoryStorageContext
) -> None:
    """Test that saving a daily score works correctly."""
    # Prepare test data
    user_id = "456"
    date = "2023-01-01"
    score = 120
    daily_score = DailyScoreItem(
        user_id=user_id,
        date=date,
        score=score,
    )

    # Execute the query
    query = SaveDailyScoreQuery(item=daily_score)
    result = user_storage.save_daily_score(query)

    # Verify the result
    assert isinstance(result, Success)

    # Create the expected key
    score_key = DailyScoreKey(user_id=user_id, date=date)

    # Verify the data was saved correctly
    assert score_key in memory_context.scores
    saved_score = memory_context.scores[score_key]
    assert isinstance(saved_score, DailyScoreItem)
    assert saved_score.user_id == user_id
    assert saved_score.date == date
    assert saved_score.score == score


def test_get_all_user_ids_empty(user_storage: InMemoryUserStorage) -> None:
    """Test that getting all user IDs from an empty store returns an empty list."""
    query = GetAllUserIdsQuery()
    result = user_storage.get_all_user_ids(query)

    assert isinstance(result, Success)
    reply = result.unwrap()
    assert reply.user_ids == []


def test_get_all_user_ids_with_data(
    user_storage: InMemoryUserStorage, memory_context: InMemoryStorageContext
) -> None:
    """Test that getting all user IDs returns the correct list of IDs."""
    # Prepare test data
    user_ids = ["1", "2", "3"]
    for user_id in user_ids:
        memory_context.users[user_id] = UserMetadataItem(
            user_id=user_id,
            last_fetched_timestamp=1630000000,
            puzzles_attempted=10,
            puzzles_solved=8,
            current_streak=3,
        )

    # Execute the query
    query = GetAllUserIdsQuery()
    result = user_storage.get_all_user_ids(query)

    # Verify the result
    assert isinstance(result, Success)
    reply = result.unwrap()
    assert set(reply.user_ids) == set(user_ids)
