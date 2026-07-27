"""User management schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    is_onboarded: bool
    preferred_language: str
    timezone: str
    metadata: Dict[str, Any]
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserSettingsResponse(BaseModel):
    preferences: Dict[str, Any]
    notification_settings: Dict[str, Any]
    content_preferences: Dict[str, Any]

    class Config:
        from_attributes = True


class UserSettingsUpdateRequest(BaseModel):
    preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    content_preferences: Optional[Dict[str, Any]] = None


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    permissions: list[str] = []


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    permissions: list
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(APIKeyResponse):
    raw_key: str
    warning: str = "Save this key now. It will not be shown again."

