"""
Authentication API endpoints.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, get_password_hash, verify_password
from ..database import get_db
from ..models.user import User, UserSession
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login with username and password.

    Returns JWT access token on success.
    """
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Verify password
    if not user.hashed_password or not verify_password(
        login_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create access token
    expire_minutes = 60 * 24 * 7 if login_data.remember_me else 60 * 24  # 7 days or 1 day
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
        expires_delta=timedelta(minutes=expire_minutes),
    )

    # Update last login time
    user.last_login_at = datetime.utcnow()

    # Create session record
    session = UserSession(
        user_id=user.id,
        access_token=access_token,
        expires_at=datetime.utcnow() + timedelta(minutes=expire_minutes),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(session)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=access_token,
        expires_in=expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=UserResponse)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    Note: In production, you might want to disable public registration
    and only allow admin-created accounts.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == register_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    if register_data.email:
        existing_email = db.query(User).filter(User.email == register_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Create new user
    hashed_password = get_password_hash(register_data.password)
    new_user = User(
        username=register_data.username,
        email=register_data.email,
        full_name=register_data.full_name,
        hashed_password=hashed_password,
        role="user",  # Default role
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.

    Requires: Authorization header with Bearer token
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout current user.

    In a more sophisticated implementation, you would invalidate
    the token on the server side by removing it from the sessions table.
    """
    # TODO: Implement token blacklist or session removal
    return {"message": "Successfully logged out"}
