"""Common/shared Pydantic schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    service: str = Field(default="TrendTube AI")
    version: str = Field(default="1.0.0")


class PaginatedResponse(BaseModel):
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class ErrorResponse(BaseModel):
    error: str
    detail: str
    errors: Optional[List[Dict[str, Any]]] = None
