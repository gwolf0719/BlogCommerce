from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.models.view_log import ViewLog
from app.models.post import Post
from app.models.product import Product
from app.models.user import User
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid


class ViewTrackingService:
    """瀏覽追蹤服務"""
    
    @staticmethod
    def record_view(
        db: Session,
        content_type: str,
        content_id: int,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None
    ) -> ViewLog:
        """記錄瀏覽行為"""
        
        # 如果沒有 session_id，生成一個
        if not session_id and not user_id:
            session_id = str(uuid.uuid4())
        
        # 檢查是否在短時間內重複瀏覽（防止刷新重複計算）
        recent_threshold = datetime.utcnow() - timedelta(minutes=5)
        
        existing_view = db.query(ViewLog).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.content_id == content_id,
                ViewLog.viewed_at > recent_threshold,
                ViewLog.user_id == user_id if user_id else ViewLog.session_id == session_id
            )
        ).first()
        
        if existing_view:
            # 更新現有記錄的時間
            existing_view.viewed_at = datetime.utcnow()
            db.commit()
            return existing_view
        
        # 創建新的瀏覽記錄
        view_log = ViewLog(
            content_type=content_type,
            content_id=content_id,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign
        )
        
        db.add(view_log)
        
        # 更新內容的瀏覽計數
        if content_type == "post":
            post = db.query(Post).filter(Post.id == content_id).first()
            if post:
                post.view_count = (post.view_count or 0) + 1
        elif content_type == "product":
            product = db.query(Product).filter(Product.id == content_id).first()
            if product:
                product.view_count = (product.view_count or 0) + 1
        
        db.commit()
        return view_log
    
    @staticmethod
    def get_popular_content(
        db: Session,
        content_type: str,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        """獲取熱門內容"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # 查詢熱門內容
        query = db.query(
            ViewLog.content_id,
            func.count(ViewLog.id).label('view_count'),
            func.count(func.distinct(ViewLog.user_id)).label('unique_users'),
            func.count(func.distinct(ViewLog.session_id)).label('unique_sessions')
        ).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.viewed_at >= since_date
            )
        ).group_by(ViewLog.content_id).order_by(desc('view_count')).limit(limit)
        
        results = query.all()
        
        # 獲取內容詳情
        popular_items = []
        for result in results:
            if content_type == "post":
                content = db.query(Post).filter(Post.id == result.content_id).first()
            elif content_type == "product":
                content = db.query(Product).filter(Product.id == result.content_id).first()
            else:
                continue
                
            if content:
                popular_items.append({
                    'id': content.id,
                    'title': content.title if hasattr(content, 'title') else content.name,
                    'slug': content.slug,
                    'view_count': result.view_count,
                    'unique_users': result.unique_users,
                    'unique_sessions': result.unique_sessions,
                    'total_views': content.view_count
                })
        
        return popular_items
    
    @staticmethod
    def get_user_view_history(
        db: Session,
        user_id: int,
        content_type: Optional[str] = None,
        limit: int = 50
    ) -> List[ViewLog]:
        """獲取用戶瀏覽歷史"""
        
        query = db.query(ViewLog).filter(ViewLog.user_id == user_id)
        
        if content_type:
            query = query.filter(ViewLog.content_type == content_type)
        
        return query.order_by(desc(ViewLog.viewed_at)).limit(limit).all()
    
    @staticmethod
    def get_content_view_stats(
        db: Session,
        content_type: str,
        content_id: int,
        days: int = 30
    ) -> Dict:
        """獲取內容瀏覽統計"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # 總瀏覽量
        total_views = db.query(ViewLog).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.content_id == content_id,
                ViewLog.viewed_at >= since_date
            )
        ).count()
        
        # 獨立用戶數
        unique_users = db.query(func.count(func.distinct(ViewLog.user_id))).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.content_id == content_id,
                ViewLog.viewed_at >= since_date,
                ViewLog.user_id.isnot(None)
            )
        ).scalar()
        
        # 獨立會話數
        unique_sessions = db.query(func.count(func.distinct(ViewLog.session_id))).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.content_id == content_id,
                ViewLog.viewed_at >= since_date,
                ViewLog.session_id.isnot(None)
            )
        ).scalar()
        
        # 今日瀏覽量
        today = datetime.utcnow().date()
        today_views = db.query(ViewLog).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.content_id == content_id,
                func.date(ViewLog.viewed_at) == today
            )
        ).count()
        
        return {
            'total_views': total_views,
            'unique_users': unique_users or 0,
            'unique_sessions': unique_sessions or 0,
            'today_views': today_views,
            'period_days': days
        }
    
    @staticmethod
    def get_trending_content(
        db: Session,
        content_type: str,
        hours: int = 24,
        limit: int = 5
    ) -> List[Dict]:
        """獲取趨勢內容（最近熱門）"""
        
        since_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(
            ViewLog.content_id,
            func.count(ViewLog.id).label('recent_views')
        ).filter(
            and_(
                ViewLog.content_type == content_type,
                ViewLog.viewed_at >= since_time
            )
        ).group_by(ViewLog.content_id).order_by(desc('recent_views')).limit(limit)
        
        results = query.all()
        
        trending_items = []
        for result in results:
            if content_type == "post":
                content = db.query(Post).filter(Post.id == result.content_id).first()
            elif content_type == "product":
                content = db.query(Product).filter(Product.id == result.content_id).first()
            else:
                continue
                
            if content:
                trending_items.append({
                    'id': content.id,
                    'title': content.title if hasattr(content, 'title') else content.name,
                    'slug': content.slug,
                    'recent_views': result.recent_views,
                    'total_views': content.view_count,
                    'trend_score': result.recent_views  # 可以加權計算
                })
        
        return trending_items 