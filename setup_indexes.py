"""
setup_indexes.py
----------------
Creates MongoDB indexes for all collections.
Run this once after setting up the project.

    python setup_indexes.py

Why indexes?
  - Unique indexes on email/username prevent duplicates even if
    two requests arrive at the same millisecond (race condition).
  - Regular indexes on frequently-queried fields make lookups fast.
    Without an index, MongoDB scans every document — slow at scale.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from app.core.config import settings


async def create_indexes():
    print("Creating MongoDB indexes...")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    # ── Users collection ──────────────────────────────────────
    users = db["users"]
    await users.create_index([("email", ASCENDING)], unique=True)
    await users.create_index([("username", ASCENDING)], unique=True)
    print("  users: email (unique), username (unique)")

    # ── Products collection (Week 3) ──────────────────────────
    products = db["products"]
    await products.create_index([("sku", ASCENDING)], unique=True, sparse=True)
    await products.create_index([("category", ASCENDING)])
    await products.create_index([("name", ASCENDING)])
    await products.create_index([("is_active", ASCENDING)])
    print("  products: sku (unique), category, name, is_active")

    # ── Orders collection (Week 6) ────────────────────────────
    orders = db["orders"]
    await orders.create_index([("user_id", ASCENDING)])
    await orders.create_index([("status", ASCENDING)])
    print("  orders: user_id, status")

    # ── Reviews collection (Week 7) ───────────────────────────
    reviews = db["reviews"]
    await reviews.create_index([("product_id", ASCENDING)])
    await reviews.create_index([("user_id", ASCENDING)])
    print("  reviews: product_id, user_id")

    client.close()
    print("\nAll indexes created successfully!")


if __name__ == "__main__":
    asyncio.run(create_indexes())
