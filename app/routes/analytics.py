from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid
import re
from user_agents import parse
from pydantic import BaseModel

from app.database import get_db
from app.models.analytics import PageView, DailyStats, PopularContent, UserSession
from app.models.post import Post
from app.models.product import Product

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_client_info(request: Request) -> Dict[str, Any]:
    """從請求中提取客戶端信息"""
    user_agent_string = request.headers.get("user-agent", "")
    user_agent = parse(user_agent_string)
    
    # 獲取 IP 地址
    ip = request.client.host
    if "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        ip = request.headers["x-real-ip"]
    
    return {
        "ip": ip,
        "user_agent": user_agent_string,
        "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
        "os": f"{user_agent.os.family} {user_agent.os.version_string}",
        "device_type": "mobile" if user_agent.is_mobile else ("tablet" if user_agent.is_tablet else "desktop"),
        "referer": request.headers.get("referer", "")
    }


def get_or_create_session(request: Request, db: Session) -> str:
    """獲取或創建用戶會話"""
    session_id = request.session.get("analytics_session_id")
    
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["analytics_session_id"] = session_id
        
        # 創建新會話記錄
        client_info = get_client_info(request)
        session = UserSession(
            session_id=session_id,
            visitor_ip=client_info["ip"],
            user_agent=client_info["user_agent"],
            device_type=client_info["device_type"],
            browser=client_info["browser"],
            os=client_info["os"],
            referer=client_info["referer"]
        )
        
        db.add(session)
        db.commit()
    
    return session_id


async def track_page_view_background(
    page_url: str,
    page_type: str,
    content_id: Optional[int],
    session_id: str,
    client_info: Dict[str, Any],
    db: Session
):
    """後台任務：記錄頁面瀏覽"""
    try:
        # 記錄頁面瀏覽
        page_view = PageView(
            page_url=page_url,
            page_type=page_type,
            content_id=content_id,
            visitor_ip=client_info["ip"],
            user_agent=client_info["user_agent"],
            referer=client_info["referer"],
            device_type=client_info["device_type"],
            browser=client_info["browser"],
            os=client_info["os"],
            session_id=session_id
        )
        
        db.add(page_view)
        
        # 更新會話信息
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            session.page_views += 1
            if session.page_views > 1:
                session.is_bounce = False
        
        # 更新熱門內容統計
        if content_id and page_type in ["blog", "product"]:
            popular = db.query(PopularContent).filter(
                and_(
                    PopularContent.content_type == page_type,
                    PopularContent.content_id == content_id
                )
            ).first()
            
            if popular:
                popular.total_views += 1
                popular.last_viewed = datetime.utcnow()
                popular.today_views += 1
            else:
                # 創建新的熱門內容記錄
                title = ""
                if page_type == "blog":
                    post = db.query(Post).filter(Post.id == content_id).first()
                    title = post.title if post else ""
                elif page_type == "product":
                    product = db.query(Product).filter(Product.id == content_id).first()
                    title = product.name if product else ""
                
                popular = PopularContent(
                    content_type=page_type,
                    content_id=content_id,
                    content_title=title,
                    content_url=page_url,
                    total_views=1,
                    unique_views=1,
                    today_views=1
                )
                db.add(popular)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Error tracking page view: {e}")


class PageViewRequest(BaseModel):
    page_url: str
    page_type: str
    content_id: Optional[int] = None
    page_title: Optional[str] = None
    view_duration: Optional[int] = None
    session_id: Optional[str] = None

@router.post("/track")
async def track_page_view(
    data: PageViewRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """記錄頁面瀏覽"""
    try:
        client_info = get_client_info(request)
        session_id = get_or_create_session(request, db)
        
        # 使用後台任務處理統計記錄
        background_tasks.add_task(
            track_page_view_background,
            data.page_url,
            data.page_type,
            data.content_id,
            session_id,
            client_info,
            db
        )
        
        return {"status": "success", "message": "頁面瀏覽已記錄"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"記錄失敗: {str(e)}")


class HeartbeatRequest(BaseModel):
    session_id: str
    page_url: str
    active_time: int


@router.post("/heartbeat")
async def heartbeat(
    data: HeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """更新會話活動狀態"""
    try:
        # 更新會話的最後活動時間
        session = db.query(UserSession).filter(
            UserSession.session_id == data.session_id
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()
        
        return {"status": "success", "message": "心跳已記錄"}
        
    except Exception as e:
        return {"status": "error", "message": f"心跳記錄失敗: {str(e)}"}


@router.get("/stats/overview")
async def get_overview_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取總覽統計數據"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 總瀏覽量
        total_views = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= start_date
        ).scalar()
        
        # 獨立訪客數
        unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).filter(
            PageView.created_at >= start_date
        ).scalar()
        
        # 獨立 IP 數
        unique_ips = db.query(func.count(func.distinct(PageView.visitor_ip))).filter(
            PageView.created_at >= start_date
        ).scalar()
        
        # 頁面類型統計
        page_type_stats = db.query(
            PageView.page_type,
            func.count(PageView.id).label('views')
        ).filter(
            PageView.created_at >= start_date
        ).group_by(PageView.page_type).all()
        
        # 設備類型統計
        device_stats = db.query(
            PageView.device_type,
            func.count(PageView.id).label('views')
        ).filter(
            PageView.created_at >= start_date
        ).group_by(PageView.device_type).all()
        
        # 每日趨勢
        daily_stats = db.query(
            func.date(PageView.created_at).label('date'),
            func.count(PageView.id).label('views'),
            func.count(func.distinct(PageView.session_id)).label('visitors')
        ).filter(
            PageView.created_at >= start_date
        ).group_by(func.date(PageView.created_at)).order_by('date').all()
        
        return {
            "period": f"過去 {days} 天",
            "total_views": total_views or 0,
            "unique_visitors": unique_visitors or 0,
            "unique_ips": unique_ips or 0,
            "page_types": [{"type": pt.page_type, "views": pt.views} for pt in page_type_stats],
            "devices": [{"device": ds.device_type, "views": ds.views} for ds in device_stats],
            "daily_trend": [
                {
                    "date": str(ds.date),
                    "views": ds.views,
                    "visitors": ds.visitors
                } for ds in daily_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計失敗: {str(e)}")


@router.get("/popular/content")
async def get_popular_content(
    content_type: Optional[str] = None,
    period: str = "month",  # today, week, month, all
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """獲取熱門內容"""
    try:
        query = db.query(PopularContent)
        
        if content_type:
            query = query.filter(PopularContent.content_type == content_type)
        
        # 根據時間段排序
        if period == "today":
            query = query.order_by(desc(PopularContent.today_views))
        elif period == "week":
            query = query.order_by(desc(PopularContent.week_views))
        elif period == "month":
            query = query.order_by(desc(PopularContent.month_views))
        else:
            query = query.order_by(desc(PopularContent.total_views))
        
        results = query.limit(limit).all()
        
        return [
            {
                "content_type": pc.content_type,
                "content_id": pc.content_id,
                "title": pc.content_title,
                "url": pc.content_url,
                "total_views": pc.total_views,
                "today_views": pc.today_views,
                "week_views": pc.week_views,
                "month_views": pc.month_views,
                "last_viewed": pc.last_viewed.isoformat() if pc.last_viewed else None
            } for pc in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取熱門內容失敗: {str(e)}")


@router.get("/realtime")
async def get_realtime_stats(db: Session = Depends(get_db)):
    """獲取實時統計"""
    try:
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # 過去一小時的瀏覽量
        hour_views = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_hour
        ).scalar()
        
        # 過去24小時的瀏覽量
        day_views = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_24h
        ).scalar()
        
        # 當前在線用戶數（過去15分鐘有活動）
        active_sessions = db.query(func.count(UserSession.id)).filter(
            UserSession.last_activity >= now - timedelta(minutes=15)
        ).scalar()
        
        # 最近的頁面瀏覽
        recent_views = db.query(PageView).filter(
            PageView.created_at >= last_hour
        ).order_by(desc(PageView.created_at)).limit(10).all()
        
        return {
            "current_time": now.isoformat(),
            "active_users": active_sessions or 0,
            "hour_views": hour_views or 0,
            "day_views": day_views or 0,
            "recent_views": [
                {
                    "page_url": pv.page_url,
                    "page_type": pv.page_type,
                    "time": pv.created_at.isoformat(),
                    "device": pv.device_type,
                    "country": pv.country
                } for pv in recent_views
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取實時統計失敗: {str(e)}")


@router.get("/content/{content_type}/{content_id}/stats")
async def get_content_stats(
    content_type: str,
    content_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取特定內容的統計數據"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 總瀏覽量
        total_views = db.query(func.count(PageView.id)).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= start_date
            )
        ).scalar()
        
        # 獨立訪客
        unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= start_date
            )
        ).scalar()
        
        # 每日瀏覽趨勢
        daily_views = db.query(
            func.date(PageView.created_at).label('date'),
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= start_date
            )
        ).group_by(func.date(PageView.created_at)).order_by('date').all()
        
        # 來源統計
        referer_stats = db.query(
            PageView.referer,
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= start_date,
                PageView.referer.isnot(None),
                PageView.referer != ""
            )
        ).group_by(PageView.referer).order_by(desc('views')).limit(10).all()
        
        return {
            "content_type": content_type,
            "content_id": content_id,
            "period": f"過去 {days} 天",
            "total_views": total_views or 0,
            "unique_visitors": unique_visitors or 0,
            "daily_views": [
                {
                    "date": str(dv.date),
                    "views": dv.views
                } for dv in daily_views
            ],
            "top_referers": [
                {
                    "referer": rs.referer,
                    "views": rs.views
                } for rs in referer_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取內容統計失敗: {str(e)}")


class EventRequest(BaseModel):
    event_type: str
    event_data: dict
    session_id: str
    page_url: str
    timestamp: int


@router.post("/event")
async def track_event(
    data: EventRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """記錄自定義事件"""
    try:
        # 這裡可以根據需要記錄事件到資料庫
        # 目前先簡單返回成功狀態
        return {"status": "success", "message": "事件已記錄"}
        
    except Exception as e:
        return {"status": "error", "message": f"事件記錄失敗: {str(e)}"} 