"""
app/api/v1/auth.py
------------------
Authentication endpoints:

  POST /api/v1/auth/register  →  create a new user account
  POST /api/v1/auth/login     →  verify credentials, return JWT
  GET  /api/v1/auth/me        →  return the currently logged-in user

All the heavy lifting (hashing, token creation, DB queries) is done
in helper functions — the endpoint functions stay short and readable.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database.connection import users_collection
from app.schemas.user import (
    MessageResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter()


# ── Helper: convert a MongoDB user doc to UserResponse ────────────────────────

def _user_to_response(user: dict) -> UserResponse:
    """
    MongoDB stores the id as ObjectId under '_id'.
    Our response schema expects a plain string 'id'.
    This helper handles that conversion safely.
    """
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        full_name=user["full_name"],
        is_active=user.get("is_active", True),
        is_admin=user.get("is_admin", False),
        created_at=user.get("created_at", datetime.now(timezone.utc)),
    )


# ── POST /register ─────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(data: UserRegister):
    """
    1. Check email and username are not already taken.
    2. Hash the password (NEVER store plain text).
    3. Save the new user document to MongoDB.
    4. Return a success message (no token yet — user must log in).
    """
    db = users_collection()

    # Check for duplicate email
    if await db.find_one({"email": data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Check for duplicate username
    if await db.find_one({"username": data.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose another.",
        )

    # Build the user document
    new_user = {
        "email": data.email,
        "username": data.username,
        "hashed_password": hash_password(data.password),   # ← plain text never saved
        "full_name": data.full_name,
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    await db.insert_one(new_user)

    return MessageResponse(message="Account created successfully! You can now log in.")


# ── POST /login ────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT access token",
)
async def login(data: UserLogin):
    """
    1. Find the user by email.
    2. Verify the password against the stored hash.
    3. Create and return a signed JWT token + user info.

    The client must store this token and send it in the
    Authorization header on every future protected request:
        Authorization: Bearer <token>
    """
    db = users_collection()

    # Find user by email
    user = await db.find_one({"email": data.email})

    # Use the same generic error for both "user not found" and "wrong password"
    # — never tell the caller WHICH part was wrong (security best practice)
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
    )

    if user is None:
        raise auth_error

    # Verify password against bcrypt hash
    if not verify_password(data.password, user["hashed_password"]):
        raise auth_error

    # Check account is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    # Create JWT — "sub" (subject) stores the user's ID as a string
    access_token = create_access_token(data={"sub": str(user["_id"])})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_user_to_response(user),
    )


# ── GET /me ────────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently logged-in user's profile",
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint — requires a valid JWT in the Authorization header.

    get_current_user (the dependency) does all the token validation.
    By the time this function runs, current_user is already a verified
    MongoDB document.
    """
    return _user_to_response(current_user)


# ── GET /me/admin-test ─────────────────────────────────────────────────────────

@router.get(
    "/me/admin-test",
    summary="Test endpoint — only accessible by admin users",
)
async def admin_only_test(current_user: dict = Depends(get_current_user)):
    """
    Quick way to verify your admin flag is working.
    In Week 3 this pattern moves to the /admin router.
    """
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only.",
        )
    return {"message": f"Hello admin {current_user['username']}!"}
