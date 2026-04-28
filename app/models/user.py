"""
app/models/user.py
------------------
User document model for MongoDB.

In MongoDB there are no strict schemas enforced at the DB level,
so we define the structure here in Python so the rest of the
app knows exactly what fields exist on a user document.

Key idea:
  - We NEVER store plain-text passwords — only the hashed version.
  - is_admin flag controls access to admin-only endpoints (Week 3+).
  - We use Python dicts for MongoDB docs (not ORM objects like Django).
"""

from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId


class UserModel:
    """
    Represents a user document in the 'users' MongoDB collection.

    This is NOT a Pydantic model — it's a plain Python class that
    describes the shape of data stored in MongoDB.
    Pydantic schemas (in schemas/user.py) handle request/response validation.
    """

    def __init__(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: str,
        is_active: bool = True,
        is_admin: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[ObjectId] = None,
    ):
        self._id = _id or ObjectId()
        self.email = email
        self.username = username
        self.hashed_password = hashed_password   # NEVER store plain text
        self.full_name = full_name
        self.is_active = is_active
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Convert to a MongoDB-ready dictionary."""
        return {
            "_id": self._id,
            "email": self.email,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "UserModel":
        """Rebuild a UserModel from a MongoDB document."""
        return UserModel(
            _id=data.get("_id"),
            email=data["email"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            full_name=data["full_name"],
            is_active=data.get("is_active", True),
            is_admin=data.get("is_admin", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
