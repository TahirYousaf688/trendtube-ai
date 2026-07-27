"""Billing schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BillingPlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price_usd: float
    interval: str
    currency: str
    features: Dict[str, Any]
    limits: Dict[str, Any]
    is_active: bool
    sort_order: int

    class Config:
        from_attributes = True


class BillingPlanListResponse(BaseModel):
    items: list[BillingPlanResponse]


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    plan_name: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreateSubscriptionRequest(BaseModel):
    plan_id: int
    payment_method_id: str
    coupon_code: Optional[str] = None


class ChangePlanRequest(BaseModel):
    new_plan_id: int


class InvoiceResponse(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int


class StripePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str


class CouponResponse(BaseModel):
    code: str
    discount_percent: float
    discount_amount: float
    is_valid: bool

    class Config:
        from_attributes = True


class CouponApplyRequest(BaseModel):
    code: str
    plan_id: int

