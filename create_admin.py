"""
create_admin.py
---------------
Run this once from the project root to create your first admin account.

Usage:
    python create_admin.py

Why a separate script?
  The /auth/register endpoint always creates regular users (is_admin=False).
  Admins need to be created manually or through a secure back-channel.
  This script sets is_admin=True directly in the database.
"""

import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import hash_password


async def create_admin():
    print("=== Admin User Creator ===\n")

    email = input("Admin email: ").strip()
    username = input("Username: ").strip().lower()
    full_name = input("Full name: ").strip()
    password = input("Password (min 6 chars): ").strip()

    if len(password) < 6:
        print("Password too short!")
        return

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    users = db["users"]

    # Check duplicates
    if await users.find_one({"email": email}):
        print(f"A user with email '{email}' already exists.")
        client.close()
        return

    if await users.find_one({"username": username}):
        print(f"Username '{username}' is already taken.")
        client.close()
        return

    admin_doc = {
        "email": email,
        "username": username,
        "hashed_password": hash_password(password),
        "full_name": full_name,
        "is_active": True,
        "is_admin": True,           # ← the important flag
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await users.insert_one(admin_doc)
    client.close()

    print(f"\nAdmin user created successfully!")
    print(f"  ID       : {result.inserted_id}")
    print(f"  Email    : {email}")
    print(f"  Username : {username}")
    print(f"\nYou can now log in at POST /api/v1/auth/login")


if __name__ == "__main__":
    asyncio.run(create_admin())
