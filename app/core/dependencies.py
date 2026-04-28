"""
app/core/dependencies.py
-------------------------
FastAPI dependencies for authentication and authorisation.

What is a FastAPI dependency?
------------------------------
It's a function you declare in an endpoint's parameter list using Depends().
FastAPI calls it automatically before running your endpoint.

  @router.get("/me")
  async def get_me(current_user = Depends(get_current_user)):
      return current_user

Flow for a protected request:
  1. Client sends:  Authorization: Bearer <jwt_token>
  2. get_current_user() extracts and decodes the token
  3. Looks up the user in MongoDB
  4. Returns the user dict → your endpoint receives it as current_user
  5. If anything fails → 401 Unauthorized is raised automatically
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.database.connection import users_collection

# This tells FastAPI where the login endpoint is so Swagger UI
# can show an "Authorize" button. The URL must match your login route.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency: decode the JWT from the Authorization header,
    fetch the user from MongoDB, and return the user document.

    Raises 401 if the token is missing, invalid, expired, or the
    user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Step 1: Decode and verify the JWT
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Step 2: Extract the user ID stored in the "sub" (subject) claim
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Step 3: Look up the user in MongoDB
    from bson import ObjectId
    try:
        user = await users_collection().find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    # Step 4: Make sure the account is still active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    return user


async def get_current_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependency: same as get_current_user but also checks is_admin.
    Use this on any endpoint that only admins should reach.

    Usage:
        @router.post("/admin/products")
        async def create_product(admin = Depends(get_current_admin)):
            ...
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user
