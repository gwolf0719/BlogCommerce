from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.middleware import get_feature_settings
from app.models.newsletter import NewsletterSubscriber
from app.schemas.newsletter import (
    NewsletterSubscriptionRequest,
    NewsletterUnsubscribeRequest,
    NewsletterSubscriberResponse,
)

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


def check_newsletter_enabled():
    features = get_feature_settings()
    if not features.get("newsletter_enabled", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="電子報功能未啟用")


@router.post("/subscribe", response_model=NewsletterSubscriberResponse)
async def subscribe(
    payload: NewsletterSubscriptionRequest,
    db: Session = Depends(get_db),
):
    """訂閱電子報"""
    check_newsletter_enabled()

    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == payload.email
    ).first()

    if subscriber:
        if subscriber.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="此電子郵件已訂閱")
        subscriber.is_active = True
        subscriber.name = payload.name
        subscriber.subscribed_at = datetime.utcnow()
        subscriber.unsubscribed_at = None
    else:
        subscriber = NewsletterSubscriber(
            email=payload.email,
            name=payload.name,
            source=payload.source or "website",
            tags=payload.tags,
            is_active=True,
        )
        db.add(subscriber)

    db.commit()
    db.refresh(subscriber)
    return subscriber


@router.post("/unsubscribe")
async def unsubscribe(
    payload: NewsletterUnsubscribeRequest,
    db: Session = Depends(get_db),
):
    """取消訂閱電子報"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == payload.email
    ).first()

    if not subscriber or not subscriber.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="訂閱記錄不存在")

    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    db.commit()
    return {"message": "已取消訂閱"}
