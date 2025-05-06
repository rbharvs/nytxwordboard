import enum
from datetime import datetime, timezone
from typing import Literal

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

    resource_type: str = Field(..., description="Type of resource not found")
    resource_id: str = Field(..., description="ID of resource not found")


class StorageOperationDetails(DetailsBase):
    """Details for storage operation errors."""

    operation: str = Field(description="Storage operation that failed")
    resource_type: str = Field(..., description="Type of resource being operated on")
    raw_error: str = Field(..., description="Raw error details if available")


class ApplicationError(BaseModel):
    """Base model for application errors."""

    code: ErrorCode
    message: str
    details: DetailsBase
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    service_name: str

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
    )


class StorageError(ApplicationError): ...


class NotFoundStorageError(StorageError):
    """Error indicating a requested resource was not found."""

    code: Literal[ErrorCode.NOT_FOUND] = ErrorCode.NOT_FOUND
    message: str = Field(default="Requested entity was not found in storage.")
    details: NotFoundDetails


class InternalStorageError(StorageError):
    """Error indicating an internal storage error occurred."""

    code: Literal[ErrorCode.INTERNAL] = ErrorCode.INTERNAL
    message: str = Field(default="Internal storage error occurred.")


class UnavailableStorageError(StorageError):
    """Error indicating storage is unavailable."""

    code: Literal[ErrorCode.UNAVAILABLE] = ErrorCode.UNAVAILABLE
    message: str = Field(default="Storage is currently unavailable.")


class InvalidArgumentStorageError(StorageError):
    """Error indicating invalid arguments were provided to a storage operation."""

    code: Literal[ErrorCode.INVALID_ARGUMENT] = ErrorCode.INVALID_ARGUMENT
    message: str = Field(default="Invalid argument provided to storage operation.")
