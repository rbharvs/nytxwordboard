"""Models for user storage operations."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field
from returns.result import Result

from app.core.error import StorageError
from app.storage.models import DailyScoreItem, UserMetadataItem, UserMetadataKey


class GetUserMetadataQuery(BaseModel):
    """Query parameters for getting user metadata."""

    user_id: UserMetadataKey = Field(
        description="ID of the user to retrieve metadata for"
    )

    model_config = ConfigDict(frozen=True)


class GetUserMetadataReply(BaseModel):
    """Response data for get_user_metadata operation."""

    item: UserMetadataItem = Field(description="User metadata")

    model_config = ConfigDict(frozen=True)


type GetUserMetadataResult = Result[GetUserMetadataReply, StorageError]


class SaveDailyScoreQuery(BaseModel):
    """Query parameters for saving a daily score."""

    item: DailyScoreItem = Field(description="Daily score to save")

    model_config = ConfigDict(frozen=True)


class SaveDailyScoreReply(BaseModel):
    """Response data for save_daily_score operation."""

    pass


type SaveDailyScoreResult = Result[SaveDailyScoreReply, StorageError]


class SaveUserMetadataQuery(BaseModel):
    """Query parameters for saving user metadata."""

    item: UserMetadataItem = Field(description="User metadata to save")

    model_config = ConfigDict(frozen=True)


class SaveUserMetadataReply(BaseModel):
    """Response data for save_user_metadata operation."""

    pass


type SaveUserMetadataResult = Result[SaveUserMetadataReply, StorageError]


class GetAllUserIdsQuery(BaseModel):
    """Query parameters for getting all user IDs."""

    pass


class GetAllUserIdsReply(BaseModel):
    """Response data for get_all_user_ids operation."""

    user_ids: List[UserMetadataKey] = Field(description="List of all user IDs")

    model_config = ConfigDict(frozen=True)


type GetAllUserIdsResult = Result[GetAllUserIdsReply, StorageError]
