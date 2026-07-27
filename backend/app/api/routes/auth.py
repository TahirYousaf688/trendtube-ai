"""Authentication routes: register, login, OAuth, refresh, logout."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.domain import OAuthAccount, RefreshToken, User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    OAuthCallbackRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check existing email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Check existing username
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    # Create user
    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role="member",
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store refresh token
    db.add(RefreshToken(user_id=user.id, token_hash=get_password_hash(refresh_token), expires_at=datetime.now(timezone.utc)))
    db.commit()

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store refresh token
    db.add(RefreshToken(user_id=user.id, token_hash=get_password_hash(refresh_token), expires_at=datetime.now(timezone.utc)))
    db.commit()

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh an expired access token using a refresh token."""
    # Decode refresh token without verification first to get user id
    payload_data = decode_token(payload.refresh_token)
    if not payload_data or payload_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = int(payload_data["sub"])

    # Verify refresh token exists and is not revoked
    stored_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False,  # noqa: E712
    ).all()

    valid_token = None
    for stored in stored_tokens:
        if verify_password(payload.refresh_token, stored.token_hash):
            valid_token = stored
            break

    if not valid_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found or revoked")

    # Revoke old refresh token
    valid_token.is_revoked = True
    db.commit()

    # Generate new tokens
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store new refresh token
    db.add(RefreshToken(user_id=user.id, token_hash=get_password_hash(new_refresh_token), expires_at=datetime.now(timezone.utc)))
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revoke all refresh tokens for the current user."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False,  # noqa: E712
    ).update({"is_revoked": True})
    db.commit()
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserResponse.model_validate(current_user)


@router.get("/google/login")
def google_login():
    """Initiate Google OAuth login."""
    from authlib.integrations.starlette_client import OAuth

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params=None,
        access_token_url="https://oauth2.googleapis.com/token",
        access_token_params=None,
        client_kwargs={"scope": "openid email profile"},
    )
    redirect_uri = settings.google_redirect_uri
    return oauth.google.authorize_redirect(redirect_uri)


@router.post("/google/callback", response_model=AuthResponse)
def google_callback(payload: OAuthCallbackRequest, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    # In production, exchange code for tokens using authlib
    # For now, mock the OAuth flow
    from app.core.security import create_access_token, create_refresh_token

    # Mock Google user info
    google_email = "google_user@example.com"
    google_name = "Google User"

    # Find or create user
    user = db.query(User).filter(User.email == google_email).first()
    if not user:
        user = User(
            email=google_email,
            username=f"google_{google_email.split('@')[0]}",
            full_name=google_name,
            password_hash=get_password_hash("oauth_placeholder"),
            role="member",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create OAuth account link
        oauth_account = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id="google_12345",
            access_token="mock_access_token",
        )
        db.add(oauth_account)
        db.commit()

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        ),
    )

