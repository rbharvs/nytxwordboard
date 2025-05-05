import enum
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ErrorCode(str, enum.Enum):
    """Canonical error codes based on Abseil error codes."""

    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    FAILED_PRECONDITION = "FAILED_PRECONDITION"
    ABORTED = "ABORTED"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    UNIMPLEMENTED = "UNIMPLEMENTED"
    INTERNAL = "INTERNAL"
    UNAVAILABLE = "UNAVAILABLE"
    DATA_LOSS = "DATA_LOSS"
    UNAUTHENTICATED = "UNAUTHENTICATED"


class DetailsBase(BaseModel):
    """Base class for structured error details."""

    model_config = ConfigDict(extra="forbid")


class NotFoundDetails(DetailsBase):
    """Details for NotFoundError."""

    resource_type: Optional[str] = Field(None, description="Type of resource not found")
    resource_id: Optional[str] = Field(None, description="ID of resource not found")


class ApplicationError(BaseModel):
    """Base model for application errors."""

    code: ErrorCode
    message: str
    details: Optional[DetailsBase] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    service_name: Optional[str] = None

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
    )


class NotFoundError(ApplicationError):
    """Error indicating a requested resource was not found."""

    code: Literal[ErrorCode.NOT_FOUND] = ErrorCode.NOT_FOUND
    message: str = Field(default="Requested entity was not found.")
    details: Optional[NotFoundDetails] = None
