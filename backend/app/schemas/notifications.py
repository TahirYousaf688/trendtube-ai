"""Notification schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    data: Dict[str, Any]
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    notification_ids: Optional[list[int]] = None  # None = mark all as read

