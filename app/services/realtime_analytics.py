from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.database import get_db
from app.models.analytics import PageView, UserSession, DailyStats, PopularContent
from app.models.user import User
from app.models.post import Post
from app.models.product import Product
from app.models.order import Order
# 分類已移除
import asyncio
import redis
import json
import logging

logger = logging.getLogger(__name__)

class RealtimeAnalyticsService:
    """即時分析服務"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.cache_ttl = 300  # 5分鐘快取過期時間
    
    def get_cache_key(self, key_type: str, *args) -> str:
        """生成快取鍵"""
        return f"analytics:{key_type}:{':'.join(map(str, args))}"
    
    async def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """從快取獲取數據"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"快取讀取失敗: {e}")
        return None
    
    async def set_cached_data(self, cache_key: str, data: Dict, ttl: int = None) -> None:
        """設置快取數據"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                cache_key, 
                ttl or self.cache_ttl, 
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"快取設置失敗: {e}")
    
    async def get_realtime_overview(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """獲取即時總覽統計"""
        cache_key = self.get_cache_key("overview", days)
        
        # 嘗試從快取獲取
        cached_data = await self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # 計算即時數據
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 並行查詢多個統計數據
        stats = {}
        
        # 基本瀏覽統計
        stats['total_views'] = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= start_date
        ).scalar() or 0
        
        stats['unique_visitors'] = db.query(func.count(func.distinct(PageView.session_id))).filter(
            PageView.created_at >= start_date
        ).scalar() or 0
        
        stats['unique_ips'] = db.query(func.count(func.distinct(PageView.visitor_ip))).filter(
            PageView.created_at >= start_date
        ).scalar() or 0
        
        # 訂單和收入統計
        stats['total_orders'] = db.query(func.count(Order.id)).filter(
            Order.created_at >= start_date
        ).scalar() or 0
        
        stats['total_revenue'] = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.created_at >= start_date,
                Order.status.in_(['confirmed', 'shipped', 'delivered'])
            )
        ).scalar() or 0.0
        
        # 今日統計
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats['today_views'] = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= today_start
        ).scalar() or 0
        
        stats['today_orders'] = db.query(func.count(Order.id)).filter(
            Order.created_at >= today_start
        ).scalar() or 0
        
        stats['today_revenue'] = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.created_at >= today_start,
                Order.status.in_(['confirmed', 'shipped', 'delivered'])
            )
        ).scalar() or 0.0
        
        # 活躍會話數（過去15分鐘）
        active_cutoff = datetime.utcnow() - timedelta(minutes=15)
        stats['active_sessions'] = db.query(func.count(UserSession.id)).filter(
            UserSession.last_activity >= active_cutoff
        ).scalar() or 0
        
        # 添加計算時間戳
        stats['calculated_at'] = datetime.utcnow().isoformat()
        stats['period_days'] = days
        
        # 快取結果
        await self.set_cached_data(cache_key, stats, ttl=60)  # 1分鐘快取
        
        return stats
    
    async def get_realtime_content_stats(self, db: Session, content_type: Optional[str] = None, 
                                       days: int = 30, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """獲取即時內容統計"""
        cache_key = self.get_cache_key("content_stats", content_type or "all", days, limit, offset)
        
        # 短期快取（30秒）
        cached_data = await self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
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
                PageView.content_id.isnot(None)
            )
        )
        
        if content_type:
            query = query.filter(PageView.page_type == content_type)
        else:
            query = query.filter(PageView.page_type.in_(['blog', 'product']))
        
        stats = query.group_by(
            PageView.content_id, PageView.page_type
        ).order_by(desc('total_views')).offset(offset).limit(limit).all()
        
        # 獲取內容詳細信息
        content_list = []
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
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
                'category': ''
            }
            
            # 獲取今日瀏覽數（即時計算）
            today_views = db.query(func.count(PageView.id)).filter(
                and_(
                    PageView.content_id == stat.content_id,
                    PageView.page_type == stat.page_type,
                    PageView.created_at >= today_start
                )
            ).scalar() or 0
            content_info['today_views'] = today_views
            
            # 獲取內容詳細信息
            if stat.page_type == 'blog':
                post = db.query(Post).filter(Post.id == stat.content_id).first()
                if post:
                    content_info.update({
                        'title': post.title,
                        'url': f'/blog/{post.slug}',
                        'published_at': post.created_at.isoformat() if post.created_at else None,
                        'category': post.categories[0].name if post.categories else ''
                    })
            elif stat.page_type == 'product':
                product = db.query(Product).filter(Product.id == stat.content_id).first()
                if product:
                    content_info.update({
                        'title': product.name,
                        'url': f'/product/{product.slug}',
                        'published_at': product.created_at.isoformat() if product.created_at else None,
                        'category': product.categories[0].name if product.categories else ''
                    })
            
            content_list.append(content_info)
        
        # 獲取總數
        total_query = db.query(func.count(func.distinct(
            func.concat(PageView.content_id, ':', PageView.page_type)
        ))).filter(
            and_(
                PageView.created_at >= start_date,
                PageView.content_id.isnot(None)
            )
        )
        
        if content_type:
            total_query = total_query.filter(PageView.page_type == content_type)
        else:
            total_query = total_query.filter(PageView.page_type.in_(['blog', 'product']))
        
        total_count = total_query.scalar() or 0
        
        result = {
            "content_stats": content_list,
            "total_count": total_count,
            "period_days": days,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        # 短期快取
        await self.set_cached_data(cache_key, result, ttl=30)
        
        return result
    
    async def get_realtime_dashboard_stats(self, db: Session) -> Dict[str, Any]:
        """獲取即時儀表板統計"""
        cache_key = self.get_cache_key("dashboard_stats")
        
        # 短期快取（30秒）
        cached_data = await self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # 即時計算各項統計
        stats = {
            # 基本統計 - 直接從資料庫即時查詢
            "total_users": db.query(func.count(User.id)).scalar() or 0,
            "total_posts": db.query(func.count(Post.id)).scalar() or 0,
            "published_posts": db.query(func.count(Post.id)).filter(Post.is_published == True).scalar() or 0,
            "total_products": db.query(func.count(Product.id)).scalar() or 0,
            "active_products": db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0,
            "total_orders": db.query(func.count(Order.id)).scalar() or 0,
            "pending_orders": db.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0,
        }
        
        # 計算總銷售額（即時）
        total_sales = db.query(func.sum(Order.total_amount)).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).scalar() or 0
        stats["total_sales"] = float(total_sales)
        
        # 今日統計
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats["today_orders"] = db.query(func.count(Order.id)).filter(
            Order.created_at >= today_start
        ).scalar() or 0
        
        stats["today_revenue"] = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.created_at >= today_start,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).scalar() or 0.0
        
        # 即時活躍統計
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        stats["hour_views"] = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_hour
        ).scalar() or 0
        
        # 活躍會話（過去15分鐘）
        active_cutoff = now - timedelta(minutes=15)
        stats["active_sessions"] = db.query(func.count(UserSession.id)).filter(
            UserSession.last_activity >= active_cutoff
        ).scalar() or 0
        
        stats["calculated_at"] = now.isoformat()
        
        # 短期快取
        await self.set_cached_data(cache_key, stats, ttl=30)
        
        return stats
    
    async def get_realtime_device_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """獲取即時設備統計"""
        cache_key = self.get_cache_key("device_stats", days)
        
        cached_data = await self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 設備類型統計（基於即時會話數據）
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
        ).limit(10).all()
        
        # 處理數據
        total_sessions = sum(row.count for row in device_query) or 1
        
        device_stats = []
        for row in device_query:
            device_name = row.device_type or "unknown"
            if device_name == "unknown":
                device_name = "其他"
            
            device_stats.append({
                "name": device_name,
                "count": row.count,
                "percentage": round((row.count / total_sessions * 100), 1)
            })
        
        browser_stats = []
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
                "percentage": round((row.count / total_sessions * 100), 1)
            })
        
        result = {
            "devices": device_stats,
            "browsers": browser_stats,
            "total_sessions": total_sessions,
            "period_days": days,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        # 2分鐘快取
        await self.set_cached_data(cache_key, result, ttl=120)
        
        return result
    
    async def invalidate_cache(self, pattern: str = None) -> None:
        """清除快取"""
        if not self.redis_client:
            return
        
        try:
            if pattern:
                keys = self.redis_client.keys(f"analytics:{pattern}:*")
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # 清除所有分析快取
                keys = self.redis_client.keys("analytics:*")
                if keys:
                    self.redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"快取清除失敗: {e}")
    
    async def update_popular_content(self, db: Session) -> None:
        """更新熱門內容統計（定時任務）"""
        try:
            # 清除舊的熱門內容記錄
            db.query(PopularContent).delete()
            
            # 計算新的熱門內容
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = now - timedelta(days=7)
            month_start = now - timedelta(days=30)
            
            # 獲取各時間段的熱門內容
            content_types = ['blog', 'product']
            
            for content_type in content_types:
                # 查詢內容瀏覽統計
                content_stats = db.query(
                    PageView.content_id,
                    func.count(PageView.id).label('total_views'),
                    func.count(func.distinct(PageView.visitor_ip)).label('unique_views')
                ).filter(
                    and_(
                        PageView.page_type == content_type,
                        PageView.content_id.isnot(None)
                    )
                ).group_by(PageView.content_id).all()
                
                for stat in content_stats:
                    # 獲取內容信息
                    if content_type == 'blog':
                        content = db.query(Post).filter(Post.id == stat.content_id).first()
                        if content:
                            title = content.title
                            url = f'/blog/{content.slug}'
                    else:
                        content = db.query(Product).filter(Product.id == stat.content_id).first()
                        if content:
                            title = content.name
                            url = f'/product/{content.slug}'
                    
                    if not content:
                        continue
                    
                    # 計算各時間段的瀏覽量
                    today_views = db.query(func.count(PageView.id)).filter(
                        and_(
                            PageView.content_id == stat.content_id,
                            PageView.page_type == content_type,
                            PageView.created_at >= today_start
                        )
                    ).scalar() or 0
                    
                    week_views = db.query(func.count(PageView.id)).filter(
                        and_(
                            PageView.content_id == stat.content_id,
                            PageView.page_type == content_type,
                            PageView.created_at >= week_start
                        )
                    ).scalar() or 0
                    
                    month_views = db.query(func.count(PageView.id)).filter(
                        and_(
                            PageView.content_id == stat.content_id,
                            PageView.page_type == content_type,
                            PageView.created_at >= month_start
                        )
                    ).scalar() or 0
                    
                    # 創建熱門內容記錄
                    popular_content = PopularContent(
                        content_type=content_type,
                        content_id=stat.content_id,
                        content_title=title,
                        content_url=url,
                        total_views=stat.total_views,
                        unique_views=stat.unique_views,
                        today_views=today_views,
                        week_views=week_views,
                        month_views=month_views,
                        last_viewed=now
                    )
                    db.add(popular_content)
            
            db.commit()
            
            # 清除相關快取
            await self.invalidate_cache("content")
            await self.invalidate_cache("overview")
            
        except Exception as e:
            logger.error(f"更新熱門內容統計失敗: {e}")
            db.rollback()


# 全域實例
realtime_analytics = RealtimeAnalyticsService()

async def get_realtime_analytics() -> RealtimeAnalyticsService:
    """獲取即時分析服務實例"""
    return realtime_analytics