# NYT Crossword Leaderboard

A serverless application that tracks and displays New York Times Crossword puzzle completion times, built with Python, FastAPI, and AWS Serverless technologies.

## Overview

This application fetches user statistics from the New York Times Crossword API, stores the data in DynamoDB, and provides API endpoints to retrieve daily leaderboards.

## Architecture

- **AWS Serverless Architecture**: Lambda, DynamoDB, API Gateway
- **FastAPI**: Web framework with automatic OpenAPI documentation
- **Mangum**: AWS Lambda integration for FastAPI
- **Python 3.12**: Runtime environment
- **Docker**: Containerized deployment

## Core Components

### DynamoDB Table
- Single-table design with a Global Secondary Index for efficient date-based leaderboard queries
- Stores user metadata and daily puzzle scores

### Lambda Functions
1. **API Function**: Serves leaderboard data via FastAPI endpoints
2. **Update Function**: Fetches user data from NYT's API and updates the database

## Local Development

### Prerequisites
- Python 3.12
- [uv](https://github.com/astral-sh/uv) for dependency management
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Docker](https://www.docker.com/products/docker-desktop)

### Setup
1. Install development dependencies:
   ```bash
   uv sync --dev
   ```

1. Run the API locally:
   ```bash
   uv run fastapi dev src/app/entrypoints/asgi.py
   ```

### Linting and Formatting
```bash
uv run ruff check --fix
uv run ruff format
```

### Testing
```bash
uv run pytest
```

## Deployment

The application is deployed using AWS SAM.

### Build and Deploy
```bash
sam build
sam deploy
```

If you don't have a samconfig.toml file yet, run the guided deploy command for initial setup:
```bash
sam deploy --guided
```

### Environment Variables
- `APP_ENVIRONMENT`: Environment name (e.g., 'Dev', 'Prod')
- `DYNAMODB_TABLE_NAME`: DynamoDB table name
- `DYNAMODB_GSI_NAME`: Name of the Global Secondary Index
- `DEFAULT_LEADERBOARD_LIMIT`: Maximum leaderboard entries to return

## API Endpoints

### Health Check
```
GET /health
```

### Get Leaderboard for a Date
```
GET /api/leaderboard/{date}?limit=100
```
- `date`: Date in YYYY-MM-DD format
- `limit`: Maximum number of entries to return (1-500, default: 100)

## License

[MIT License](LICENSE.txt)
