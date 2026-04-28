"""
app/database/connection.py
--------------------------
Async MongoDB connection managed through Motor.

Motor is the official async driver for MongoDB. It wraps PyMongo
under the hood but uses asyncio so it plays nicely with FastAPI's
async request handlers without blocking the event loop.

Lifecycle
---------
connect_db()    → called in app startup event
close_db()      → called in app shutdown event
get_database()  → FastAPI dependency that yields the db handle
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level client — one connection pool shared across the entire app
_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """
    Open the Motor connection pool.
    Called once when FastAPI starts up (see main.py lifespan).
    """
    global _client
    logger.info("Connecting to MongoDB at %s …", settings.MONGODB_URL)
    _client = AsyncIOMotorClient(settings.MONGODB_URL)

    # Ping the server to confirm the connection is alive
    await _client.admin.command("ping")
    logger.info("✅  MongoDB connected — database: '%s'", settings.MONGODB_DB_NAME)


async def close_db() -> None:
    """
    Close the Motor connection pool.
    Called once when FastAPI shuts down (see main.py lifespan).
    """
    global _client
    if _client is not None:
        _client.close()
        logger.info("MongoDB connection closed.")


def get_client() -> AsyncIOMotorClient:
    """Return the raw Motor client (use sparingly)."""
    if _client is None:
        raise RuntimeError("Database client is not initialised. Was connect_db() called?")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the application database handle.

    Usage as a FastAPI dependency
    ------------------------------
    from app.database.connection import get_database

    @router.get("/example")
    async def example(db: AsyncIOMotorDatabase = Depends(get_database)):
        doc = await db["some_collection"].find_one({})
        ...
    """
    return get_client()[settings.MONGODB_DB_NAME]


# ── Collection helpers (add more as needed each week) ──────────────────────────
# Accessing a collection through these thin wrappers keeps collection names
# in one place and makes refactoring easier.

def users_collection():
    return get_database()["users"]


def products_collection():
    return get_database()["products"]


def categories_collection():
    return get_database()["categories"]


def carts_collection():
    return get_database()["carts"]


def orders_collection():
    return get_database()["orders"]


def reviews_collection():
    return get_database()["reviews"]
