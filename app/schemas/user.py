"""
app/schemas/user.py
-------------------
Pydantic schemas for user-related API requests and responses.

Why schemas are separate from models
-------------------------------------
- models/user.py  →  describes what's stored in MongoDB (includes hashed_password)
- schemas/user.py →  describes what travels over HTTP

We NEVER expose hashed_password in any response schema.
Pydantic validates incoming data automatically — wrong type or missing
required field = 422 error returned before your code even runs.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# ── Request schemas (what the client sends) ────────────────────────────────────

class UserRegister(BaseModel):
    """
    Body for POST /auth/register
    Pydantic will reject the request if any field is missing or wrong type.
    """
    email: EmailStr                          # validates it's a real email format
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)     # plain text — hashed before saving
    full_name: str = Field(min_length=1, max_length=100)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Only allow letters, numbers, and underscores in usernames."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.lower()   # store usernames as lowercase


class UserLogin(BaseModel):
    """Body for POST /auth/login"""
    email: EmailStr
    password: str


# ── Response schemas (what the server sends back) ──────────────────────────────

class UserResponse(BaseModel):
    """
    Safe user data returned to the client.
    Notice: NO hashed_password field here — it never leaves the server.
    """
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Returned after a successful login.
    access_token is the JWT string the client must send in future requests.
    token_type is always "bearer" — this is the HTTP standard.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic response for simple success messages."""
    message: str
