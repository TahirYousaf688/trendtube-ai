"""Billing and subscription routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import BillingPlan, Coupon, Invoice, Subscription, User
from app.schemas.billing import (
    BillingPlanListResponse,
    BillingPlanResponse,
    ChangePlanRequest,
    CouponApplyRequest,
    CouponResponse,
    CreateSubscriptionRequest,
    InvoiceListResponse,
    InvoiceResponse,
    StripePaymentIntentResponse,
    SubscriptionResponse,
)

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans", response_model=BillingPlanListResponse)
def list_plans(db: Session = Depends(get_db)):
    """List all available billing plans."""
    plans = db.query(BillingPlan).filter(BillingPlan.is_active == True).order_by(BillingPlan.sort_order).all()  # noqa: E712
    return BillingPlanListResponse(items=[BillingPlanResponse.model_validate(p) for p in plans])


@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's subscription."""
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing", "past_due"]),
    ).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found")
    return SubscriptionResponse(
        id=sub.id,
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        plan_name=sub.plan.name if sub.plan else "Unknown",
        status=sub.status.value if hasattr(sub.status, 'value') else sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        trial_end=sub.trial_end,
        created_at=sub.created_at,
    )


@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new subscription."""
    plan = db.query(BillingPlan).filter(BillingPlan.id == payload.plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    # Cancel any existing active subscription
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"]),
    ).all()
    for sub in existing:
        sub.status = "canceled"

    from datetime import datetime, timezone, timedelta

    subscription = Subscription(
        user_id=current_user.id,
        plan_id=payload.plan_id,
        status="active",
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        plan_name=plan.name,
        status="active",
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        trial_end=subscription.trial_end,
        created_at=subscription.created_at,
    )


@router.post("/change-plan", response_model=SubscriptionResponse)
def change_plan(
    payload: ChangePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change subscription plan."""
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"]),
    ).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription")

    plan = db.query(BillingPlan).filter(BillingPlan.id == payload.new_plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    sub.plan_id = payload.new_plan_id
    db.commit()
    db.refresh(sub)

    return SubscriptionResponse(
        id=sub.id,
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        plan_name=plan.name,
        status=sub.status.value if hasattr(sub.status, 'value') else sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        trial_end=sub.trial_end,
        created_at=sub.created_at,
    )


@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel current subscription."""
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing", "past_due"]),
    ).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription")

    sub.status = "canceled"
    db.commit()
    return {"message": "Subscription canceled successfully"}


@router.get("/invoices", response_model=InvoiceListResponse)
def list_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List invoices for current user."""
    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id)
        .order_by(Invoice.created_at.desc())
        .all()
    )
    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(i) for i in invoices],
        total=len(invoices),
    )


@router.post("/create-payment-intent", response_model=StripePaymentIntentResponse)
def create_payment_intent(current_user: User = Depends(get_current_user)):
    """Create a Stripe payment intent."""
    # In production, use Stripe API
    return StripePaymentIntentResponse(
        client_secret="pi_mock_secret",
        payment_intent_id="pi_mock_12345",
        amount=2900,
        currency="usd",
    )


@router.post("/validate-coupon", response_model=CouponResponse)
def validate_coupon(
    payload: CouponApplyRequest,
    db: Session = Depends(get_db),
):
    """Validate and apply a coupon code."""
    from datetime import datetime, timezone

    coupon = db.query(Coupon).filter(Coupon.code == payload.code.upper()).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid coupon code")
    if not coupon.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon is no longer active")
    if coupon.expires_at and coupon.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon has expired")
    if coupon.max_uses > 0 and coupon.current_uses >= coupon.max_uses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon usage limit reached")

    return CouponResponse(
        code=coupon.code,
        discount_percent=float(coupon.discount_percent),
        discount_amount=float(coupon.discount_amount),
        is_valid=True,
    )

