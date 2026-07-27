"""Webhook routes for external service integrations."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.domain import Invoice, Subscription, User

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.json()
    event_type = payload.get("type", "")

    logger.info(f"Received Stripe webhook: {event_type}")

    if event_type == "customer.subscription.updated":
        # Update subscription status
        subscription_id = payload.get("data", {}).get("object", {}).get("id")
        status_event = payload.get("data", {}).get("object", {}).get("status")
        if subscription_id:
            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            if sub:
                sub.status = status_event
                db.commit()

    elif event_type == "invoice.paid":
        # Mark invoice as paid
        invoice_id = payload.get("data", {}).get("object", {}).get("id")
        if invoice_id:
            invoice = db.query(Invoice).filter(
                Invoice.stripe_invoice_id == invoice_id
            ).first()
            if invoice:
                from datetime import datetime, timezone
                invoice.status = "paid"
                invoice.paid_at = datetime.now(timezone.utc)
                db.commit()

    return {"status": "ok"}


@router.post("/paypal")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PayPal webhook events."""
    payload = await request.json()
    event_type = payload.get("event_type", "")

    logger.info(f"Received PayPal webhook: {event_type}")

    if event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
        subscription_id = payload.get("resource", {}).get("id")
        if subscription_id:
            sub = db.query(Subscription).filter(
                Subscription.paypal_subscription_id == subscription_id
            ).first()
            if sub:
                sub.status = "past_due"
                db.commit()

    return {"status": "ok"}


@router.post("/youtube")
async def youtube_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle YouTube PubSubHubbub push notifications."""
    payload = await request.json()
    logger.info(f"Received YouTube webhook: {payload.get('kind', 'unknown')}")
    return {"status": "ok"}

