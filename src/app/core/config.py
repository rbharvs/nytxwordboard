import os
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""

    # DynamoDB settings
    DYNAMODB_TABLE_NAME: str = os.environ.get(
        "DYNAMODB_TABLE_NAME", "LeaderboardTable-Dev"
    )
    DYNAMODB_GSI_NAME: str = os.environ.get("DYNAMODB_GSI_NAME", "DateLeaderboardIndex")

    # NYT API settings
    NYT_API_URL_TEMPLATE: str = os.environ.get(
        "NYT_API_URL_TEMPLATE",
        "https://www.nytimes.com/svc/crosswords/v3/{}/stats-and-streaks.json",
    )

    # Application settings
    DEFAULT_LEADERBOARD_LIMIT: int = int(
        os.environ.get("DEFAULT_LEADERBOARD_LIMIT", "100")
    )
    APP_ENVIRONMENT: str = os.environ.get("APP_ENVIRONMENT", "development")


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()
