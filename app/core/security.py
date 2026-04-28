"""
app/core/security.py
--------------------
Security utilities: password hashing and JWT helpers.
Full implementation is covered in Week 2; stubs are provided
here so imports work from day one.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
# bcrypt is the recommended algorithm — it is intentionally slow to resist
# brute-force attacks.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of *plain_password*. Never store plain text."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches *hashed_password*."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT helpers ───────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Encode *data* into a signed JWT string.

    Parameters
    ----------
    data:          Payload to embed (typically {"sub": user_id}).
    expires_delta: How long the token should be valid.
                   Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from config.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT string.

    Returns the payload dict on success, or None if the token
    is invalid / expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
