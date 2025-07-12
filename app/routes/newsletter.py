from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import secrets

from app.database import get_db
from app.middleware import get_feature_settings
from app.models.newsletter import NewsletterSubscriber, NewsletterCampaign
from app.schemas.newsletter import (
    NewsletterSubscriberCreate, NewsletterSubscriberUpdate, NewsletterSubscriberResponse,
    NewsletterSubscriptionRequest, NewsletterUnsubscribeRequest,
    NewsletterCampaignCreate, NewsletterCampaignUpdate, NewsletterCampaignResponse,
    NewsletterStats
)
from app.auth import get_current_admin_user

router = APIRouter(prefix="/api/newsletter", tags=["電子報"])


def check_newsletter_enabled():
    features = get_feature_settings()
    if not features.get("newsletter_enabled", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="電子報功能未啟用")


@router.get("/", response_model=List[NewsletterSubscriberResponse])
@router.get("", response_model=List[NewsletterSubscriberResponse])  # 添加不帶尾隨斜線的路由別名
async def get_subscribers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """取得電子報訂閱者列表（管理員專用）"""
    query = db.query(NewsletterSubscriber)
    
    if is_active is not None:
        query = query.filter(NewsletterSubscriber.is_active == is_active)
    
    if search:
        query = query.filter(
            NewsletterSubscriber.email.contains(search) |
            NewsletterSubscriber.name.contains(search)
        )
    
    subscribers = query.offset(skip).limit(limit).all()
    return subscribers


@router.post("/", response_model=NewsletterSubscriberResponse)
@router.post("", response_model=NewsletterSubscriberResponse)  # 添加不帶尾隨斜線的路由別名
async def create_subscriber(
    subscriber_data: NewsletterSubscriberCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """創建電子報訂閱者（管理員專用）"""
    # 檢查是否已存在
    existing = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == subscriber_data.email
    ).first()
    
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=400, 
                detail="該電子郵件已訂閱電子報"
            )
        else:
            # 重新啟用訂閱
            existing.is_active = True
            existing.unsubscribed_at = None
            existing.source = subscriber_data.source
            if subscriber_data.name:
                existing.name = subscriber_data.name
            if subscriber_data.tags:
                existing.tags = subscriber_data.tags
            
            db.commit()
            db.refresh(existing)
            return existing
    
    # 創建新訂閱者
    unsubscribe_token = secrets.token_urlsafe(32)
    subscriber = NewsletterSubscriber(
        **subscriber_data.dict(),
        unsubscribe_token=unsubscribe_token
    )
    
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


@router.post("/subscribe")
async def subscribe(
    subscription: NewsletterSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """前端電子報訂閱"""
    # 檢查是否已存在
    existing = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == subscription.email
    ).first()
    
    if existing:
        if existing.is_active:
            return {"message": "您已經訂閱了我們的電子報"}
        else:
            # 重新啟用訂閱
            existing.is_active = True
            existing.unsubscribed_at = None
            existing.subscribed_at = datetime.utcnow()
            if subscription.name:
                existing.name = subscription.name
            
            db.commit()
            return {"message": "感謝您重新訂閱我們的電子報"}
    
    # 創建新訂閱者
    unsubscribe_token = secrets.token_urlsafe(32)
    subscriber = NewsletterSubscriber(
        email=subscription.email,
        name=subscription.name,
        source="website",
        unsubscribe_token=unsubscribe_token
    )
    
    db.add(subscriber)
    db.commit()
    
    return {"message": "感謝您訂閱我們的電子報"}


@router.post("/unsubscribe")
async def unsubscribe(
    unsubscribe_data: NewsletterUnsubscribeRequest,
    db: Session = Depends(get_db)
):
    """取消電子報訂閱"""
    query = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == unsubscribe_data.email
    )
    
    # 如果提供了 token，也要驗證
    if unsubscribe_data.token:
        query = query.filter(
            NewsletterSubscriber.unsubscribe_token == unsubscribe_data.token
        )
    
    subscriber = query.first()
    
    if not subscriber:
        raise HTTPException(
            status_code=404,
            detail="找不到該電子郵件的訂閱記錄"
        )
    
    if not subscriber.is_active:
        return {"message": "您已經取消訂閱"}
    
    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "已成功取消訂閱"}


@router.get("/campaigns", response_model=List[NewsletterCampaignResponse])
async def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """取得電子報活動列表（管理員專用）"""
    query = db.query(NewsletterCampaign)
    
    if status:
        query = query.filter(NewsletterCampaign.status == status)
    
    campaigns = query.order_by(NewsletterCampaign.created_at.desc()).offset(skip).limit(limit).all()
    return campaigns


@router.post("/campaigns", response_model=NewsletterCampaignResponse)
async def create_campaign(
    campaign_data: NewsletterCampaignCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """創建電子報活動（管理員專用）"""
    campaign = NewsletterCampaign(**campaign_data.dict())
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=NewsletterCampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """取得特定電子報活動（管理員專用）"""
    campaign = db.query(NewsletterCampaign).filter(
        NewsletterCampaign.id == campaign_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="電子報活動不存在")
    
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=NewsletterCampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: NewsletterCampaignUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """更新電子報活動（管理員專用）"""
    campaign = db.query(NewsletterCampaign).filter(
        NewsletterCampaign.id == campaign_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="電子報活動不存在")
    
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """刪除電子報活動（管理員專用）"""
    campaign = db.query(NewsletterCampaign).filter(
        NewsletterCampaign.id == campaign_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="電子報活動不存在")
    
    if campaign.status in ["sending", "sent"]:
        raise HTTPException(
            status_code=400,
            detail="無法刪除已發送或正在發送的活動"
        )
    
    db.delete(campaign)
    db.commit()
    
    return {"message": "電子報活動已刪除"}


@router.get("/stats", response_model=NewsletterStats)
async def get_newsletter_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """取得電子報統計資料（管理員專用）"""
    # 訂閱者統計
    total_subscribers = db.query(func.count(NewsletterSubscriber.id)).scalar()
    active_subscribers = db.query(func.count(NewsletterSubscriber.id)).filter(
        NewsletterSubscriber.is_active == True
    ).scalar()
    inactive_subscribers = total_subscribers - active_subscribers
    
    # 活動統計
    total_campaigns = db.query(func.count(NewsletterCampaign.id)).scalar()
    sent_campaigns = db.query(func.count(NewsletterCampaign.id)).filter(
        NewsletterCampaign.status == "sent"
    ).scalar()
    draft_campaigns = db.query(func.count(NewsletterCampaign.id)).filter(
        NewsletterCampaign.status == "draft"
    ).scalar()
    
    # 郵件統計
    campaign_stats = db.query(
        func.sum(NewsletterCampaign.delivered_count),
        func.sum(NewsletterCampaign.opened_count),
        func.sum(NewsletterCampaign.clicked_count)
    ).filter(NewsletterCampaign.status == "sent").first()
    
    total_emails_sent = campaign_stats[0] or 0
    total_opens = campaign_stats[1] or 0
    total_clicks = campaign_stats[2] or 0
    
    # 計算平均開信率和點擊率
    average_open_rate = (total_opens / total_emails_sent * 100) if total_emails_sent > 0 else 0
    average_click_rate = (total_clicks / total_emails_sent * 100) if total_emails_sent > 0 else 0
    
    return NewsletterStats(
        total_subscribers=total_subscribers or 0,
        active_subscribers=active_subscribers or 0,
        inactive_subscribers=inactive_subscribers or 0,
        total_campaigns=total_campaigns or 0,
        sent_campaigns=sent_campaigns or 0,
        draft_campaigns=draft_campaigns or 0,
        total_emails_sent=total_emails_sent,
        total_opens=total_opens,
        total_clicks=total_clicks,
        average_open_rate=round(average_open_rate, 2),
        average_click_rate=round(average_click_rate, 2)
    )


@router.get("/{subscriber_id}", response_model=NewsletterSubscriberResponse)
async def get_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """取得特定訂閱者（管理員專用）"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="訂閱者不存在")
    
    return subscriber


@router.put("/{subscriber_id}", response_model=NewsletterSubscriberResponse)
async def update_subscriber(
    subscriber_id: int,
    subscriber_data: NewsletterSubscriberUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """更新訂閱者（管理員專用）"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="訂閱者不存在")
    
    update_data = subscriber_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscriber, field, value)
    
    # 如果停用訂閱，設置取消訂閱時間
    if not subscriber_data.is_active and subscriber.is_active:
        subscriber.unsubscribed_at = datetime.utcnow()
    elif subscriber_data.is_active and not subscriber.is_active:
        subscriber.unsubscribed_at = None
        subscriber.subscribed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subscriber)
    
    return subscriber


@router.delete("/{subscriber_id}")
async def delete_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """刪除訂閱者（管理員專用）"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="訂閱者不存在")
    
    db.delete(subscriber)
    db.commit()
    
    return {"message": "訂閱者已刪除"}
