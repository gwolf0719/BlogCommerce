from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid
import re
import logging
from user_agents import parse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.analytics import PageView, DailyStats, PopularContent, UserSession
from app.models.post import Post
from app.models.product import Product
from app.models.user import User
from app.models.order import Order, OrderItem
from app.schemas.analytics import (
    PageViewCreate, 
    HeartbeatRequest,
    AnalyticsOverviewResponse,
    ContentStatsResponse,
    RealtimeStatsResponse
)
from app.services.realtime_analytics import get_realtime_analytics

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
    data: PageViewCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """記錄頁面瀏覽（即時更新）"""
    try:
        # 獲取客戶端IP
        visitor_ip = request.client.host
        if hasattr(request.state, 'forwarded_for'):
            visitor_ip = request.state.forwarded_for
        
        # 創建頁面瀏覽記錄
        page_view = PageView(
            page_url=data.page_url,
            page_title=data.page_title,
            page_type=data.page_type,
            content_id=data.content_id,
            visitor_ip=visitor_ip,
            user_agent=data.user_agent,
            referer=data.referer,
            session_id=data.session_id,
            device_type=data.device_type,
            browser=data.browser,
            os=data.os,
            country=data.country,
            city=data.city
        )
        
        db.add(page_view)
        
        # 更新或創建會話記錄
        session = db.query(UserSession).filter(
            UserSession.session_id == data.session_id
        ).first()
        
        current_time = datetime.utcnow()
        
        if session:
            # 更新現有會話
            session.last_activity = current_time
            session.page_views += 1
            if session.page_views > 1:
                session.is_bounce = False
        else:
            # 創建新會話
            session = UserSession(
                session_id=data.session_id,
                visitor_ip=visitor_ip,
                start_time=current_time,
                last_activity=current_time,
                page_views=1,
                user_agent=data.user_agent,
                device_type=data.device_type,
                browser=data.browser,
                os=data.os,
                country=data.country,
                city=data.city,
                referer=data.referer
            )
            db.add(session)
        
        db.commit()
        
        # 即時清除相關快取
        analytics_service = await get_realtime_analytics()
        await analytics_service.invalidate_cache("overview")
        await analytics_service.invalidate_cache("dashboard_stats")
        
        return {"status": "success", "message": "頁面瀏覽已記錄"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"記錄頁面瀏覽失敗: {str(e)}")


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
    """更新會話活動狀態（即時更新）"""
    try:
        # 更新會話的最後活動時間
        session = db.query(UserSession).filter(
            UserSession.session_id == data.session_id
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()
            
            # 即時清除活躍會話快取
            analytics_service = await get_realtime_analytics()
            await analytics_service.invalidate_cache("overview")
        
        return {"status": "success", "message": "心跳已記錄"}
        
    except Exception as e:
        return {"status": "error", "message": f"心跳記錄失敗: {str(e)}"}


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取即時分析概覽數據"""
    try:
        analytics_service = await get_realtime_analytics()
        overview_data = await analytics_service.get_realtime_overview(db, days)
        
        return AnalyticsOverviewResponse(**overview_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取概覽數據失敗: {str(e)}")


@router.get("/realtime", response_model=RealtimeStatsResponse) 
async def get_realtime_stats(db: Session = Depends(get_db)):
    """獲取即時統計數據"""
    try:
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # 即時計算統計數據
        hour_views = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_hour
        ).scalar() or 0
        
        day_views = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_24h
        ).scalar() or 0
        
        # 當前在線用戶數（過去15分鐘有活動）
        active_sessions = db.query(func.count(UserSession.id)).filter(
            UserSession.last_activity >= now - timedelta(minutes=15)
        ).scalar() or 0
        
        # 最近的頁面瀏覽
        recent_views = db.query(PageView).filter(
            PageView.created_at >= last_hour
        ).order_by(desc(PageView.created_at)).limit(10).all()
        
        return RealtimeStatsResponse(
            current_time=now.isoformat(),
            active_users=active_sessions,
            hour_views=hour_views,
            day_views=day_views,
            recent_views=[
                {
                    "page_url": pv.page_url,
                    "page_type": pv.page_type,
                    "time": pv.created_at.isoformat(),
                    "device": pv.device_type,
                    "country": pv.country
                } for pv in recent_views
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取實時統計失敗: {str(e)}")


@router.get("/content-stats", response_model=ContentStatsResponse)
async def get_content_stats_overview(
    content_type: Optional[str] = None,
    days: int = 30,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "total_views",
    db: Session = Depends(get_db)
):
    """獲取即時內容統計概覽"""
    try:
        analytics_service = await get_realtime_analytics()
        content_data = await analytics_service.get_realtime_content_stats(
            db, content_type, days, limit, offset
        )
        
        return ContentStatsResponse(**content_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取內容統計失敗: {str(e)}")


@router.get("/device-stats")
async def get_device_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取即時設備統計數據"""
    try:
        analytics_service = await get_realtime_analytics()
        device_data = await analytics_service.get_realtime_device_stats(db, days)
        
        return device_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取設備統計失敗: {str(e)}")


@router.get("/content/{content_type}/{content_id}/stats")
async def get_content_stats(
    content_type: str,
    content_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取特定內容的即時統計數據"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 即時計算統計數據
        total_views = db.query(func.count(PageView.id)).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= start_date
            )
        ).scalar() or 0
        
        unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= start_date
            )
        ).scalar() or 0
        
        # 今日瀏覽數
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_views = db.query(func.count(PageView.id)).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id == content_id,
                PageView.created_at >= today_start
            )
        ).scalar() or 0
        
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
        
        return {
            "content_type": content_type,
            "content_id": content_id,
            "period_days": days,
            "total_views": total_views,
            "unique_visitors": unique_visitors,
            "today_views": today_views,
            "daily_trend": [
                {
                    "date": str(dv.date),
                    "views": dv.views
                } for dv in daily_views
            ],
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取內容統計失敗: {str(e)}")


@router.get("/top-content")
async def get_top_content(
    content_type: str = "blog",
    days: int = 30,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """獲取即時熱門內容"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 即時查詢熱門內容統計
        content_stats = db.query(
            PageView.content_id,
            func.count(PageView.id).label('total_views'),
            func.count(func.distinct(PageView.session_id)).label('unique_views')
        ).filter(
            PageView.created_at >= start_date,
            PageView.page_type == content_type,
            PageView.content_id.isnot(None)
        ).group_by(PageView.content_id).order_by(
            func.count(PageView.id).desc()
        ).limit(limit).all()
        
        results = []
        for stat in content_stats:
            if content_type == 'blog':
                content = db.query(Post).filter(Post.id == stat.content_id).first()
                if content:
                    results.append({
                        "content_id": stat.content_id,
                        "title": content.title,
                        "url": f"/blog/{content.slug}",
                        "total_views": stat.total_views,
                        "unique_views": stat.unique_views
                    })
            elif content_type == 'product':
                content = db.query(Product).filter(Product.id == stat.content_id).first()
                if content:
                    results.append({
                        "content_id": stat.content_id,
                        "title": content.name,
                        "url": f"/product/{content.slug}",
                        "total_views": stat.total_views,
                        "unique_views": stat.unique_views
                    })
        
        return {
            "content_type": content_type,
            "period_days": days,
            "top_content": results,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取熱門內容失敗: {str(e)}")


@router.get("/trend/time-series")
async def get_time_series_trends(
    granularity: str = "day",
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取即時時間序列趨勢數據（支援 SQLite）"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # SQLite 兼容的時間分組
        if granularity == "hour":
            # SQLite: strftime('%Y-%m-%d %H:00:00', datetime)
            time_trunc = func.strftime('%Y-%m-%d %H:00:00', PageView.created_at)
        elif granularity == "month":
            # SQLite: strftime('%Y-%m-01', datetime)  
            time_trunc = func.strftime('%Y-%m-01', PageView.created_at)
        else:  # day
            # SQLite: date(datetime)
            time_trunc = func.date(PageView.created_at)
        
        # 即時查詢趨勢數據（SQLite 兼容版本）
        trend_data = db.query(
            time_trunc.label('date'),
            func.count(PageView.id).label('total_views'),
            func.sum(func.case([(PageView.page_type == 'blog', 1)], else_=0)).label('blog_views'),
            func.sum(func.case([(PageView.page_type == 'product', 1)], else_=0)).label('product_views'),
            func.count(func.distinct(PageView.session_id)).label('unique_sessions')
        ).filter(
            PageView.created_at >= start_date
        ).group_by(time_trunc).order_by(time_trunc).all()
        
        # 處理結果並確保日期格式一致
        result_data = []
        for trend in trend_data:
            try:
                # 根據粒度處理日期
                if granularity == "hour":
                    # 從 '2025-06-11 14:00:00' 格式解析
                    date_obj = datetime.strptime(trend.date, '%Y-%m-%d %H:%M:%S')
                elif granularity == "month":
                    # 從 '2025-06-01' 格式解析
                    date_obj = datetime.strptime(trend.date, '%Y-%m-%d')
                else:  # day
                    # 從 '2025-06-11' 格式解析
                    date_obj = datetime.strptime(trend.date, '%Y-%m-%d')
                
                result_data.append({
                    "date": date_obj.isoformat(),
                    "total_views": trend.total_views or 0,
                    "blog_views": trend.blog_views or 0,
                    "product_views": trend.product_views or 0,
                    "unique_sessions": trend.unique_sessions or 0
                })
            except (ValueError, AttributeError) as e:
                # 如果日期解析失敗，跳過這個數據點
                logger.warning(f"日期解析失敗: {trend.date}, 錯誤: {e}")
                continue
        
        return {
            "granularity": granularity,
            "period_days": days,
            "trend_data": result_data,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取趨勢數據失敗: {str(e)}")


@router.post("/cache/invalidate")
async def invalidate_analytics_cache(
    pattern: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """手動清除分析快取"""
    try:
        analytics_service = await get_realtime_analytics()
        await analytics_service.invalidate_cache(pattern)
        
        return {
            "status": "success", 
            "message": f"快取已清除: {pattern or '全部'}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除快取失敗: {str(e)}")


@router.post("/update-popular-content")
async def update_popular_content(db: Session = Depends(get_db)):
    """手動更新熱門內容統計"""
    try:
        analytics_service = await get_realtime_analytics()
        await analytics_service.update_popular_content(db)
        
        return {
            "status": "success",
            "message": "熱門內容統計已更新",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新熱門內容統計失敗: {str(e)}")


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


@router.get("/content/{content_type}/{content_id}/detailed-stats")
async def get_detailed_content_stats(
    content_type: str,
    content_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取單個內容的詳細統計數據"""
    try:
        if content_type not in ['blog', 'product']:
            raise HTTPException(status_code=400, detail="內容類型必須是 blog 或 product")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 獲取內容基本信息
        content_info = {}
        if content_type == 'blog':
            post = db.query(Post).filter(Post.id == content_id).first()
            if not post:
                raise HTTPException(status_code=404, detail="文章不存在")
            content_info = {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'url': f'/blog/{post.slug}',
                'published_at': post.created_at,
                'type': 'blog'
            }
        else:
            product = db.query(Product).filter(Product.id == content_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="商品不存在")
            content_info = {
                'id': product.id,
                'title': product.name,
                'slug': product.slug,
                'url': f'/product/{product.slug}',
                'published_at': product.created_at,
                'type': 'product'
            }
        
        # 總體統計
        total_stats = db.query(
            func.count(PageView.id).label('total_views'),
            func.count(func.distinct(PageView.visitor_ip)).label('unique_visitors'),
            func.count(func.distinct(PageView.session_id)).label('unique_sessions'),
            func.avg(PageView.view_duration).label('avg_duration')
        ).filter(
            and_(
                PageView.content_id == content_id,
                PageView.page_type == content_type,
                PageView.created_at >= start_date,
                PageView.created_at <= end_date
            )
        ).first()
        
        # 每日統計
        daily_stats = db.query(
            func.date(PageView.created_at).label('date'),
            func.count(PageView.id).label('views'),
            func.count(func.distinct(PageView.visitor_ip)).label('unique_visitors')
        ).filter(
            and_(
                PageView.content_id == content_id,
                PageView.page_type == content_type,
                PageView.created_at >= start_date,
                PageView.created_at <= end_date
            )
        ).group_by(
            func.date(PageView.created_at)
        ).order_by(
            func.date(PageView.created_at)
        ).all()
        
        # 設備統計
        device_stats = db.query(
            PageView.device_type,
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.content_id == content_id,
                PageView.page_type == content_type,
                PageView.created_at >= start_date,
                PageView.created_at <= end_date
            )
        ).group_by(PageView.device_type).all()
        
        # 來源統計
        referer_stats = db.query(
            PageView.referer,
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.content_id == content_id,
                PageView.page_type == content_type,
                PageView.created_at >= start_date,
                PageView.created_at <= end_date,
                PageView.referer.isnot(None),
                PageView.referer != ''
            )
        ).group_by(PageView.referer).order_by(
            desc('views')
        ).limit(10).all()
        
        # 瀏覽器統計
        browser_stats = db.query(
            PageView.browser,
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.content_id == content_id,
                PageView.page_type == content_type,
                PageView.created_at >= start_date,
                PageView.created_at <= end_date
            )
        ).group_by(PageView.browser).order_by(
            desc('views')
        ).limit(10).all()
        
        # 地理位置統計
        location_stats = db.query(
            PageView.country,
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.content_id == content_id,
                PageView.page_type == content_type,
                PageView.created_at >= start_date,
                PageView.created_at <= end_date,
                PageView.country.isnot(None)
            )
        ).group_by(PageView.country).order_by(
            desc('views')
        ).limit(10).all()
        
        return {
            "content_info": content_info,
            "period_days": days,
            "total_stats": {
                "total_views": total_stats.total_views or 0,
                "unique_visitors": total_stats.unique_visitors or 0,
                "unique_sessions": total_stats.unique_sessions or 0,
                "avg_duration": round(total_stats.avg_duration or 0, 2)
            },
            "daily_stats": [
                {
                    "date": stat.date.strftime('%Y-%m-%d'),
                    "views": stat.views,
                    "unique_visitors": stat.unique_visitors
                }
                for stat in daily_stats
            ],
            "device_stats": [
                {
                    "device_type": stat.device_type or 'unknown',
                    "views": stat.views
                }
                for stat in device_stats
            ],
            "referer_stats": [
                {
                    "referer": stat.referer,
                    "views": stat.views
                }
                for stat in referer_stats
            ],
            "browser_stats": [
                {
                    "browser": stat.browser or 'unknown',
                    "views": stat.views
                }
                for stat in browser_stats
            ],
            "location_stats": [
                {
                    "country": stat.country or 'unknown',
                    "views": stat.views
                }
                for stat in location_stats
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取詳細統計失敗: {str(e)}")


# 分類統計端點已移除


@router.get("/overview")
async def get_analytics_overview(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取分析概覽數據"""
    try:
        # 計算時間範圍
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 總瀏覽量
        total_views = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= start_date
        ).scalar() or 0
        
        # 獨立訪客數（基於session_id）
        unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).filter(
            PageView.created_at >= start_date
        ).scalar() or 0
        
        # 總會話數
        total_sessions = db.query(func.count(UserSession.id)).filter(
            UserSession.created_at >= start_date
        ).scalar() or 0
        
        # 跳出率（瀏覽頁面數為1的會話比例）
        bounce_sessions = db.query(func.count(UserSession.id)).filter(
            and_(
                UserSession.created_at >= start_date,
                UserSession.page_views == 1
            )
        ).scalar() or 0
        
        bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # 計算平均會話時長（基於真實數據）
        session_durations = db.query(
            func.extract('epoch', UserSession.last_activity - UserSession.created_at).label('duration')
        ).filter(
            UserSession.created_at >= start_date,
            UserSession.last_activity > UserSession.created_at
        ).all()
        
        if session_durations:
            total_duration = sum(row.duration for row in session_durations if row.duration)
            avg_session_duration = round(total_duration / len(session_durations) / 60, 1)  # 轉換為分鐘
        else:
            avg_session_duration = 0
        
        # 新訪客比例（基於首次訪問判斷）
        total_unique_ips = db.query(func.count(func.distinct(PageView.visitor_ip))).filter(
            PageView.created_at >= start_date
        ).scalar() or 0
        
        # 計算在此期間首次訪問的IP數量
        if total_unique_ips > 0:
            # 獲取在指定期間內每個IP的最早訪問時間
            first_visits = db.query(
                PageView.visitor_ip,
                func.min(PageView.created_at).label('first_visit')
            ).group_by(PageView.visitor_ip).subquery()
            
            new_visitor_ips = db.query(func.count(first_visits.c.visitor_ip)).filter(
                first_visits.c.first_visit >= start_date
            ).scalar() or 0
            
            new_visitor_rate = round((new_visitor_ips / total_unique_ips * 100), 1)
        else:
            new_visitor_rate = 0
        
        # 獲取總訂單數和總收入（電商統計）
        total_orders = db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date
        ).scalar() or 0
        
        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        ).scalar() or 0
        
        return {
            "total_views": total_views,
            "unique_visitors": unique_visitors,
            "total_sessions": total_sessions,
            "bounce_rate": round(bounce_rate, 1),
            "avg_session_duration": avg_session_duration,
            "new_visitor_rate": new_visitor_rate,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "period": f"過去 {days} 天"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取概覽數據失敗: {str(e)}")


@router.get("/device-stats")
async def get_device_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取設備統計數據"""
    try:
        # 計算時間範圍
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 設備類型統計（基於會話）
        device_query = db.query(
            UserSession.device_type,
            func.count(UserSession.id).label('count')
        ).filter(
            UserSession.created_at >= start_date
        ).group_by(UserSession.device_type).all()
        
        # 瀏覽器統計
        browser_query = db.query(
            UserSession.browser,
            func.count(UserSession.id).label('count')
        ).filter(
            UserSession.created_at >= start_date
        ).group_by(UserSession.browser).order_by(
            func.count(UserSession.id).desc()
        ).limit(5).all()
        
        # 操作系統統計
        os_query = db.query(
            UserSession.os,
            func.count(UserSession.id).label('count')
        ).filter(
            UserSession.created_at >= start_date
        ).group_by(UserSession.os).order_by(
            func.count(UserSession.id).desc()
        ).limit(5).all()
        
        # 處理設備類型數據
        total_sessions = sum(row.count for row in device_query) or 1
        device_stats = []
        
        for row in device_query:
            device_name = row.device_type or "unknown"
            # 標準化設備名稱
            if device_name == "unknown":
                device_name = "其他"
            
            device_stats.append({
                "name": device_name,
                "count": row.count,
                "percentage": round((row.count / total_sessions * 100), 1)
            })
        
        # 處理瀏覽器數據
        browser_stats = []
        total_browser_sessions = sum(row.count for row in browser_query) or 1
        
        for row in browser_query:
            browser_name = row.browser or "Unknown"
            # 簡化瀏覽器名稱
            if "Chrome" in browser_name:
                browser_name = "Chrome"
            elif "Firefox" in browser_name:
                browser_name = "Firefox"
            elif "Safari" in browser_name:
                browser_name = "Safari"
            elif "Edge" in browser_name:
                browser_name = "Edge"
            else:
                browser_name = "其他"
            
            browser_stats.append({
                "name": browser_name,
                "count": row.count,
                "percentage": round((row.count / total_browser_sessions * 100), 1)
            })
        
        # 處理操作系統數據
        os_stats = []
        total_os_sessions = sum(row.count for row in os_query) or 1
        
        for row in os_query:
            os_name = row.os or "Unknown"
            # 簡化操作系統名稱
            if "Windows" in os_name:
                os_name = "Windows"
            elif "Mac" in os_name or "macOS" in os_name:
                os_name = "macOS"
            elif "iOS" in os_name:
                os_name = "iOS"
            elif "Android" in os_name:
                os_name = "Android"
            elif "Linux" in os_name:
                os_name = "Linux"
            else:
                os_name = "其他"
            
            os_stats.append({
                "name": os_name,
                "count": row.count,
                "percentage": round((row.count / total_os_sessions * 100), 1)
            })
        
        # 如果沒有數據，返回空統計而不是模擬數據
        if not device_stats:
            device_stats = []
        
        if not browser_stats:
            browser_stats = []
        
        if not os_stats:
            os_stats = []
        
        return {
            "devices": device_stats,
            "browsers": browser_stats,
            "operating_systems": os_stats,
            "total_sessions": total_sessions,
            "period": f"過去 {days} 天"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取設備統計失敗: {str(e)}")


@router.get("/popular-products")
async def get_popular_products(
    limit: int = Query(default=5, ge=1, le=20),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """獲取熱門商品列表（基於真實訂單數據）"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, desc, and_
        
        # 計算時間範圍
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 優先基於訂單項目統計熱門商品（真實銷售數據）
        popular_products = db.query(
            Product.name,
            Product.id,
            func.sum(OrderItem.quantity).label('sales_count'),
            func.sum(OrderItem.quantity * OrderItem.product_price).label('total_revenue')
        ).join(OrderItem, Product.id == OrderItem.product_id
        ).join(Order, OrderItem.order_id == Order.id
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.status.in_(['confirmed', 'shipped', 'delivered']),
                Product.is_active == True
            )
        ).group_by(Product.id, Product.name).order_by(
            desc('sales_count')
        ).limit(limit).all()
        
        if popular_products:
            return [
                {
                    "name": product.name,
                    "id": product.id,
                    "sales_count": int(product.sales_count),
                    "total_revenue": float(product.total_revenue),
                    "data_source": "sales"
                }
                for product in popular_products
            ]
        
        # 如果沒有銷售數據，則基於瀏覽量統計（但仍是真實數據）
        popular_by_views = db.query(
            Product.name,
            Product.id,
            func.count(PageView.id).label('view_count')
        ).join(
            PageView, 
            and_(
                PageView.content_id == Product.id,
                PageView.page_type == 'product'
            )
        ).filter(
            and_(
                PageView.created_at >= start_date,
                Product.is_active == True
            )
        ).group_by(Product.id, Product.name).order_by(
            desc('view_count')
        ).limit(limit).all()
        
        if popular_by_views:
            return [
                {
                    "name": product.name,
                    "id": product.id,
                    "sales_count": 0,
                    "view_count": int(product.view_count),
                    "data_source": "views"
                }
                for product in popular_by_views
            ]
        
        # 如果都沒有數據，返回活躍商品列表（真實但無統計數據）
        active_products = db.query(Product).filter(
            Product.is_active == True
        ).order_by(desc(Product.created_at)).limit(limit).all()
        
        return [
            {
                "name": product.name,
                "id": product.id,
                "sales_count": 0,
                "view_count": 0,
                "data_source": "no_data"
            }
            for product in active_products
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取熱門商品失敗: {str(e)}")


@router.get("/popular-posts")
async def get_popular_posts(
    limit: int = Query(default=5, ge=1, le=20),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """獲取熱門文章列表（基於真實瀏覽量數據）"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, desc, and_
        
        # 計算時間範圍
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 優先基於頁面瀏覽統計熱門文章（真實瀏覽數據）
        popular_posts = db.query(
            Post.title,
            Post.id,
            func.count(PageView.id).label('views'),
            func.count(func.distinct(PageView.session_id)).label('unique_views')
        ).join(
            PageView,
            and_(
                PageView.content_id == Post.id,
                PageView.page_type == 'blog'
            )
        ).filter(
            and_(
                PageView.created_at >= start_date,
                Post.is_published == True
            )
        ).group_by(Post.id, Post.title).order_by(
            desc('views')
        ).limit(limit).all()
        
        if popular_posts:
            return [
                {
                    "title": post.title,
                    "id": post.id,
                    "views": int(post.views),
                    "unique_views": int(post.unique_views),
                    "data_source": "views"
                }
                for post in popular_posts
            ]
        
        # 如果沒有瀏覽數據，返回最新發布的文章（真實但無統計數據）
        recent_posts = db.query(Post).filter(
            Post.is_published == True
        ).order_by(desc(Post.created_at)).limit(limit).all()
        
        return [
            {
                "title": post.title,
                "id": post.id,
                "views": 0,
                "unique_views": 0,
                "data_source": "no_data"
            }
            for post in recent_posts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取熱門文章失敗: {str(e)}")