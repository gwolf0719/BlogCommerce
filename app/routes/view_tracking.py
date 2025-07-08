from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.view_tracking_service import ViewTrackingService
from app.auth import get_current_user_optional
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List, Dict
from urllib.parse import urlparse, parse_qs


router = APIRouter(prefix="/api/views", tags=["view_tracking"])


class ViewTrackingRequest(BaseModel):
    content_type: str  # 'post' 或 'product'
    content_id: int
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    duration: Optional[int] = None  # 停留時間（秒）


@router.post("/track")
def track_view(
    request: Request,
    tracking_data: ViewTrackingRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """記錄瀏覽行為"""
    
    # 驗證內容類型
    if tracking_data.content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    # 獲取客戶端信息
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    session_id = request.session.get("session_id")
    
    # 如果沒有 session_id，創建一個
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
    
    # 解析 UTM 參數（如果在 referrer 中）
    if tracking_data.referrer and not tracking_data.utm_source:
        parsed_url = urlparse(tracking_data.referrer)
        query_params = parse_qs(parsed_url.query)
        tracking_data.utm_source = query_params.get('utm_source', [None])[0]
        tracking_data.utm_medium = query_params.get('utm_medium', [None])[0]
        tracking_data.utm_campaign = query_params.get('utm_campaign', [None])[0]
    
    # 記錄瀏覽
    view_log = ViewTrackingService.record_view(
        db=db,
        content_type=tracking_data.content_type,
        content_id=tracking_data.content_id,
        user_id=current_user.id if current_user else None,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=tracking_data.referrer,
        utm_source=tracking_data.utm_source,
        utm_medium=tracking_data.utm_medium,
        utm_campaign=tracking_data.utm_campaign
    )
    
    return {"success": True, "view_id": view_log.id}


@router.get("/popular/{content_type}")
def get_popular_content(
    content_type: str,
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """獲取熱門內容"""
    
    if content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    popular_items = ViewTrackingService.get_popular_content(
        db=db,
        content_type=content_type,
        days=days,
        limit=limit
    )
    
    return {"popular_items": popular_items}


@router.get("/trending/{content_type}")
def get_trending_content(
    content_type: str,
    hours: int = 24,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """獲取趨勢內容"""
    
    if content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    trending_items = ViewTrackingService.get_trending_content(
        db=db,
        content_type=content_type,
        hours=hours,
        limit=limit
    )
    
    return {"trending_items": trending_items}


@router.get("/stats/{content_type}/{content_id}")
def get_content_stats(
    content_type: str,
    content_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取內容瀏覽統計"""
    
    if content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    stats = ViewTrackingService.get_content_view_stats(
        db=db,
        content_type=content_type,
        content_id=content_id,
        days=days
    )
    
    return {"stats": stats}


@router.get("/history")
def get_user_view_history(
    content_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """獲取用戶瀏覽歷史"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if content_type and content_type not in ["post", "product"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    history = ViewTrackingService.get_user_view_history(
        db=db,
        user_id=current_user.id,
        content_type=content_type,
        limit=limit
    )
    
    # 轉換為可序列化的格式
    history_data = []
    for view in history:
        history_data.append({
            "id": view.id,
            "content_type": view.content_type,
            "content_id": view.content_id,
            "viewed_at": view.viewed_at.isoformat(),
            "duration": view.duration,
            "referrer": view.referrer
        })
    
    return {"history": history_data} 