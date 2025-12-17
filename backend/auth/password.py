"""
Password hashing and verification.

Note: Using SHA-256 for simplicity. In production, use bcrypt or argon2.
"""
import hashlib


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return get_password_hash(plain_password) == hashed_password


def get_password_hash(password: str) -> str:
    """
    Hash a password for storing.

    Args:
        password: Plain text password

    Returns:
        Hashed password string (SHA-256 hex digest)
    """
    return hashlib.sha256(password.encode()).hexdigest()
