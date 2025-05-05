from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import leaderboard

# Create FastAPI application
app = FastAPI(
    title="NYT Crossword Leaderboard API",
    description="API for retrieving NYT Crossword puzzle leaderboards and user stats",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])


# Add health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
