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


@router.get("/content-stats")
async def get_content_stats_overview(
    content_type: Optional[str] = None,
    days: int = 30,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "total_views",  # total_views, unique_views, today_views
    db: Session = Depends(get_db)
):
    """獲取內容流量統計概覽 - 支援部落格和商品的詳細統計"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 基礎查詢
        query = db.query(
            PageView.content_id,
            PageView.page_type,
            func.count(PageView.id).label('total_views'),
            func.count(func.distinct(PageView.visitor_ip)).label('unique_views'),
            func.count(func.distinct(PageView.session_id)).label('unique_sessions')
        ).filter(
            and_(
                PageView.created_at >= start_date,
                PageView.created_at <= end_date,
                PageView.content_id.isnot(None)
            )
        )
        
        # 篩選內容類型
        if content_type:
            query = query.filter(PageView.page_type == content_type)
        else:
            query = query.filter(PageView.page_type.in_(['blog', 'product']))
        
        # 分組並排序
        stats = query.group_by(
            PageView.content_id, 
            PageView.page_type
        ).order_by(
            desc(sort_by) if sort_by in ['total_views', 'unique_views', 'unique_sessions'] 
            else desc('total_views')
        ).offset(offset).limit(limit).all()
        
        # 獲取內容詳細信息
        content_list = []
        for stat in stats:
            content_info = {
                'content_id': stat.content_id,
                'content_type': stat.page_type,
                'total_views': stat.total_views,
                'unique_views': stat.unique_views,
                'unique_sessions': stat.unique_sessions,
                'title': '',
                'url': '',
                'published_at': None,
                'author': '',
                'category': ''
            }
            
            # 獲取具體內容信息
            if stat.page_type == 'blog':
                post = db.query(Post).filter(Post.id == stat.content_id).first()
                if post:
                    content_info.update({
                        'title': post.title,
                        'url': f'/blog/{post.slug}',
                        'published_at': post.published_at,
                        'author': post.author_id,
                        'category': post.categories[0].name if post.categories else ''
                    })
            elif stat.page_type == 'product':
                product = db.query(Product).filter(Product.id == stat.content_id).first()
                if product:
                    content_info.update({
                        'title': product.name,
                        'url': f'/product/{product.slug}',
                        'published_at': product.created_at,
                        'author': '',
                        'category': product.categories[0].name if product.categories else ''
                    })
            
            # 獲取今日瀏覽數
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_views = db.query(func.count(PageView.id)).filter(
                and_(
                    PageView.content_id == stat.content_id,
                    PageView.page_type == stat.page_type,
                    PageView.created_at >= today_start
                )
            ).scalar()
            
            content_info['today_views'] = today_views or 0
            content_list.append(content_info)
        
        # 獲取總數
        total_query = db.query(func.count(func.distinct(
            func.concat(PageView.content_id, ':', PageView.page_type)
        ))).filter(
            and_(
                PageView.created_at >= start_date,
                PageView.created_at <= end_date,
                PageView.content_id.isnot(None)
            )
        )
        
        if content_type:
            total_query = total_query.filter(PageView.page_type == content_type)
        else:
            total_query = total_query.filter(PageView.page_type.in_(['blog', 'product']))
        
        total_count = total_query.scalar()
        
        return {
            "content_stats": content_list,
            "total_count": total_count,
            "period_days": days,
            "filters": {
                "content_type": content_type,
                "sort_by": sort_by
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取內容統計失敗: {str(e)}")


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
                'published_at': post.published_at,
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


@router.get("/top-content-by-category")
async def get_top_content_by_category(
    content_type: str = "blog",  # blog 或 product
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """獲取按分類的熱門內容統計"""
    try:
        if content_type not in ['blog', 'product']:
            raise HTTPException(status_code=400, detail="內容類型必須是 blog 或 product")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 基礎統計查詢
        view_stats = db.query(
            PageView.content_id,
            func.count(PageView.id).label('total_views'),
            func.count(func.distinct(PageView.visitor_ip)).label('unique_views')
        ).filter(
            and_(
                PageView.page_type == content_type,
                PageView.content_id.isnot(None),
                PageView.created_at >= start_date,
                PageView.created_at <= end_date
            )
        ).group_by(PageView.content_id).subquery()
        
        # 獲取分類信息
        if content_type == 'blog':
            from app.models.post import post_categories
            from app.models.category import Category
            
            result = db.query(
                Post.id,
                Post.title,
                Post.slug,
                Category.name.label('category_name'),
                view_stats.c.total_views,
                view_stats.c.unique_views
            ).join(
                view_stats, Post.id == view_stats.c.content_id
            ).join(
                post_categories, Post.id == post_categories.c.post_id
            ).join(
                Category, post_categories.c.category_id == Category.id
            ).order_by(
                desc(view_stats.c.total_views)
            ).limit(limit).all()
            
        else:  # product
            from app.models.product import product_categories
            from app.models.category import Category
            
            result = db.query(
                Product.id,
                Product.name.label('title'),
                Product.slug,
                Category.name.label('category_name'),
                view_stats.c.total_views,
                view_stats.c.unique_views
            ).join(
                view_stats, Product.id == view_stats.c.content_id
            ).join(
                product_categories, Product.id == product_categories.c.product_id
            ).join(
                Category, product_categories.c.category_id == Category.id
            ).order_by(
                desc(view_stats.c.total_views)
            ).limit(limit).all()
        
        # 整理結果
        content_by_category = {}
        for item in result:
            category = item.category_name
            if category not in content_by_category:
                content_by_category[category] = []
            
            content_by_category[category].append({
                'id': item.id,
                'title': item.title,
                'slug': item.slug,
                'url': f'/{content_type}/{item.slug}' if content_type == 'blog' else f'/product/{item.slug}',
                'total_views': item.total_views or 0,
                'unique_views': item.unique_views or 0
            })
        
        return {
            "content_type": content_type,
            "period_days": days,
            "content_by_category": content_by_category
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取分類統計失敗: {str(e)}")


@router.get("/trend/time-series")
async def get_time_series_trends(
    granularity: str = "day",  # hour, day, month
    days: int = 30,
    db: Session = Depends(get_db)
):
    """獲取時間序列趨勢數據"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if granularity == "hour":
            # 按小時統計（僅限當天）
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            blog_query = db.query(
                extract('hour', PageView.created_at).label('time_unit'),
                func.count(PageView.id).label('views')
            ).filter(
                and_(
                    PageView.created_at >= start_date,
                    PageView.page_type == 'blog'
                )
            ).group_by(extract('hour', PageView.created_at))
            
            product_query = db.query(
                extract('hour', PageView.created_at).label('time_unit'),
                func.count(PageView.id).label('views')
            ).filter(
                and_(
                    PageView.created_at >= start_date,
                    PageView.page_type == 'product'
                )
            ).group_by(extract('hour', PageView.created_at))
            
            # 生成24小時的完整數據
            time_labels = [f"{i:02d}:00" for i in range(24)]
            
        elif granularity == "day":
            # 按天統計
            blog_query = db.query(
                func.date(PageView.created_at).label('time_unit'),
                func.count(PageView.id).label('views')
            ).filter(
                and_(
                    PageView.created_at >= start_date,
                    PageView.page_type == 'blog'
                )
            ).group_by(func.date(PageView.created_at))
            
            product_query = db.query(
                func.date(PageView.created_at).label('time_unit'),
                func.count(PageView.id).label('views')
            ).filter(
                and_(
                    PageView.created_at >= start_date,
                    PageView.page_type == 'product'
                )
            ).group_by(func.date(PageView.created_at))
            
            # 生成日期標籤
            time_labels = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                time_labels.append(current_date.strftime("%m/%d"))
                current_date += timedelta(days=1)
            
        else:  # month
            # 按月統計
            blog_query = db.query(
                extract('year', PageView.created_at).label('year'),
                extract('month', PageView.created_at).label('month'),
                func.count(PageView.id).label('views')
            ).filter(
                and_(
                    PageView.created_at >= start_date,
                    PageView.page_type == 'blog'
                )
            ).group_by(
                extract('year', PageView.created_at),
                extract('month', PageView.created_at)
            )
            
            product_query = db.query(
                extract('year', PageView.created_at).label('year'),
                extract('month', PageView.created_at).label('month'),
                func.count(PageView.id).label('views')
            ).filter(
                and_(
                    PageView.created_at >= start_date,
                    PageView.page_type == 'product'
                )
            ).group_by(
                extract('year', PageView.created_at),
                extract('month', PageView.created_at)
            )
            
            # 生成月份標籤
            time_labels = []
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                time_labels.append(current_date.strftime("%Y/%m"))
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # 執行查詢
        blog_results = blog_query.all()
        product_results = product_query.all()
        
        # 處理結果數據
        blog_data = {}
        product_data = {}
        
        if granularity == "hour":
            for result in blog_results:
                blog_data[int(result.time_unit)] = result.views
            for result in product_results:
                product_data[int(result.time_unit)] = result.views
                
            blog_values = [blog_data.get(i, 0) for i in range(24)]
            product_values = [product_data.get(i, 0) for i in range(24)]
            
        elif granularity == "day":
            for result in blog_results:
                # 確保 time_unit 是 date 物件
                if hasattr(result.time_unit, 'strftime'):
                    key = result.time_unit.strftime("%m/%d")
                else:
                    # 如果是字符串，嘗試轉換為 date
                    try:
                        date_obj = datetime.strptime(str(result.time_unit), "%Y-%m-%d").date()
                        key = date_obj.strftime("%m/%d")
                    except:
                        key = str(result.time_unit)
                blog_data[key] = result.views
                
            for result in product_results:
                if hasattr(result.time_unit, 'strftime'):
                    key = result.time_unit.strftime("%m/%d")
                else:
                    try:
                        date_obj = datetime.strptime(str(result.time_unit), "%Y-%m-%d").date()
                        key = date_obj.strftime("%m/%d")
                    except:
                        key = str(result.time_unit)
                product_data[key] = result.views
                
            blog_values = [blog_data.get(label, 0) for label in time_labels]
            product_values = [product_data.get(label, 0) for label in time_labels]
            
        else:  # month
            for result in blog_results:
                key = f"{int(result.year)}/{int(result.month):02d}"
                blog_data[key] = result.views
            for result in product_results:
                key = f"{int(result.year)}/{int(result.month):02d}"
                product_data[key] = result.views
                
            blog_values = [blog_data.get(label, 0) for label in time_labels]
            product_values = [product_data.get(label, 0) for label in time_labels]
        
        return {
            "labels": time_labels,
            "datasets": [
                {
                    "label": "部落格文章",
                    "data": blog_values,
                    "borderColor": "#3B82F6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "tension": 0.1
                },
                {
                    "label": "商品頁面",
                    "data": product_values,
                    "borderColor": "#10B981",
                    "backgroundColor": "rgba(16, 185, 129, 0.1)",
                    "tension": 0.1
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取趨勢數據失敗: {str(e)}")


@router.get("/top-content")
async def get_top_content(
    content_type: str = "blog",  # blog or product
    granularity: str = "day",  # hour, day, month
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """獲取指定時間範圍內的熱門內容"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if granularity == "hour":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if content_type == "blog":
            query = db.query(
                Post.id,
                Post.title,
                Post.slug,
                Post.featured_image,
                func.count(PageView.id).label('views'),
                func.count(func.distinct(PageView.visitor_ip)).label('unique_views')
            ).join(
                PageView, and_(
                    PageView.content_id == Post.id,
                    PageView.page_type == 'blog'
                )
            ).filter(
                PageView.created_at >= start_date
            ).group_by(
                Post.id, Post.title, Post.slug, Post.featured_image
            ).order_by(
                desc('views')
            ).limit(limit)
            
        else:  # product
            query = db.query(
                Product.id,
                Product.name.label('title'),
                Product.slug,
                Product.featured_image,
                func.count(PageView.id).label('views'),
                func.count(func.distinct(PageView.visitor_ip)).label('unique_views')
            ).join(
                PageView, and_(
                    PageView.content_id == Product.id,
                    PageView.page_type == 'product'
                )
            ).filter(
                PageView.created_at >= start_date
            ).group_by(
                Product.id, Product.name, Product.slug, Product.featured_image
            ).order_by(
                desc('views')
            ).limit(limit)
        
        results = query.all()
        
        return [
            {
                "id": result.id,
                "title": result.title,
                "slug": result.slug,
                "featured_image": result.featured_image,
                "views": result.views,
                "unique_views": result.unique_views,
                "content_type": content_type
            }
            for result in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取熱門內容失敗: {str(e)}") 