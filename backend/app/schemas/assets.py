"""Asset schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    asset_type: str
    storage_key: str
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[float] = None
    provider: str
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_public: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AssetUploadResponse(BaseModel):
    id: int
    storage_key: str
    url: str
    upload_url: Optional[str] = None  # For presigned S3 uploads


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int


class AssetUpdateRequest(BaseModel):
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

