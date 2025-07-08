"""
分析相關的後台任務
這些任務確保統計數據的即時性和準確性
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.database import SessionLocal
from app.models.analytics import PageView, UserSession, PopularContent, DailyStats
from app.models.user import User
from app.models.post import Post
from app.models.product import Product
from app.models.order import Order
from app.services.realtime_analytics import get_realtime_analytics

logger = logging.getLogger(__name__)


async def update_daily_stats():
    """更新每日統計數據"""
    db = SessionLocal()
    try:
        yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        today = yesterday + timedelta(days=1)
        
        logger.info(f"更新 {yesterday.date()} 的每日統計數據")
        
        # 檢查是否已存在該日期的統計
        existing_stats = db.query(DailyStats).filter(
            func.date(DailyStats.stat_date) == yesterday.date()
        ).first()
        
        if existing_stats:
            logger.info(f"{yesterday.date()} 的統計數據已存在，跳過")
            return
        
        # 計算昨日統計
        total_views = db.query(func.count(PageView.id)).filter(
            and_(
                PageView.created_at >= yesterday,
                PageView.created_at < today
            )
        ).scalar() or 0
        
        unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).filter(
            and_(
                PageView.created_at >= yesterday,
                PageView.created_at < today
            )
        ).scalar() or 0
        
        unique_ips = db.query(func.count(func.distinct(PageView.visitor_ip))).filter(
            and_(
                PageView.created_at >= yesterday,
                PageView.created_at < today
            )
        ).scalar() or 0
        
        # 頁面類型統計
        page_type_stats = db.query(
            PageView.page_type,
            func.count(PageView.id).label('views')
        ).filter(
            and_(
                PageView.created_at >= yesterday,
                PageView.created_at < today
            )
        ).group_by(PageView.page_type).all()
        
        home_views = 0
        blog_views = 0
        product_views = 0
        category_views = 0
        
        for stat in page_type_stats:
            if stat.page_type == 'home':
                home_views = stat.views
            elif stat.page_type == 'blog':
                blog_views = stat.views
            elif stat.page_type == 'product':
                product_views = stat.views
            elif stat.page_type == 'category':
                category_views = stat.views
        
        # 設備統計
        device_stats = db.query(
            UserSession.device_type,
            func.count(UserSession.id).label('count')
        ).filter(
            and_(
                UserSession.created_at >= yesterday,
                UserSession.created_at < today
            )
        ).group_by(UserSession.device_type).all()
        
        desktop_views = 0
        mobile_views = 0
        tablet_views = 0
        
        for stat in device_stats:
            if stat.device_type == 'desktop':
                desktop_views = stat.count
            elif stat.device_type == 'mobile':
                mobile_views = stat.count
            elif stat.device_type == 'tablet':
                tablet_views = stat.count
        
        # 用戶統計
        registered_user_views = db.query(func.count(PageView.id)).filter(
            and_(
                PageView.created_at >= yesterday,
                PageView.created_at < today,
                PageView.user_id.isnot(None)
            )
        ).scalar() or 0
        
        guest_views = total_views - registered_user_views
        
        # 計算平均會話時長和跳出率
        sessions = db.query(UserSession).filter(
            and_(
                UserSession.created_at >= yesterday,
                UserSession.created_at < today
            )
        ).all()
        
        total_sessions = len(sessions)
        total_duration = 0
        bounce_sessions = 0
        
        for session in sessions:
            if session.duration:
                total_duration += session.duration
            if session.is_bounce:
                bounce_sessions += 1
        
        avg_session_duration = total_duration // total_sessions if total_sessions > 0 else 0
        bounce_rate = (bounce_sessions * 100) // total_sessions if total_sessions > 0 else 0
        
        # 創建每日統計記錄
        daily_stats = DailyStats(
            stat_date=yesterday,
            total_views=total_views,
            unique_visitors=unique_visitors,
            unique_ips=unique_ips,
            home_views=home_views,
            blog_views=blog_views,
            product_views=product_views,
            category_views=category_views,
            desktop_views=desktop_views,
            mobile_views=mobile_views,
            tablet_views=tablet_views,
            registered_user_views=registered_user_views,
            guest_views=guest_views,
            avg_session_duration=avg_session_duration,
            bounce_rate=bounce_rate
        )
        
        db.add(daily_stats)
        db.commit()
        
        logger.info(f"成功更新 {yesterday.date()} 的每日統計數據")
        
    except Exception as e:
        logger.error(f"更新每日統計數據失敗: {e}")
        db.rollback()
    finally:
        db.close()


async def update_popular_content():
    """更新熱門內容統計"""
    db = SessionLocal()
    try:
        logger.info("開始更新熱門內容統計")
        
        analytics_service = await get_realtime_analytics()
        await analytics_service.update_popular_content(db)
        
        logger.info("成功更新熱門內容統計")
        
    except Exception as e:
        logger.error(f"更新熱門內容統計失敗: {e}")
    finally:
        db.close()


async def cleanup_old_data(days_to_keep: int = 365):
    """清理舊的分析數據"""
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        logger.info(f"開始清理 {cutoff_date.date()} 之前的舊數據")
        
        # 清理舊的頁面瀏覽記錄
        old_page_views = db.query(PageView).filter(
            PageView.created_at < cutoff_date
        ).count()
        
        if old_page_views > 0:
            db.query(PageView).filter(
                PageView.created_at < cutoff_date
            ).delete(synchronize_session=False)
            logger.info(f"清理了 {old_page_views} 條舊的頁面瀏覽記錄")
        
        # 清理舊的會話記錄
        old_sessions = db.query(UserSession).filter(
            UserSession.created_at < cutoff_date
        ).count()
        
        if old_sessions > 0:
            db.query(UserSession).filter(
                UserSession.created_at < cutoff_date
            ).delete(synchronize_session=False)
            logger.info(f"清理了 {old_sessions} 條舊的會話記錄")
        
        # 清理舊的每日統計（保留更長時間）
        daily_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
        old_daily_stats = db.query(DailyStats).filter(
            DailyStats.stat_date < daily_cutoff
        ).count()
        
        if old_daily_stats > 0:
            db.query(DailyStats).filter(
                DailyStats.stat_date < daily_cutoff
            ).delete(synchronize_session=False)
            logger.info(f"清理了 {old_daily_stats} 條舊的每日統計記錄")
        
        db.commit()
        logger.info("舊數據清理完成")
        
        # 清理分析快取
        analytics_service = await get_realtime_analytics()
        await analytics_service.invalidate_cache()
        logger.info("清理了分析快取")
        
    except Exception as e:
        logger.error(f"清理舊數據失敗: {e}")
        db.rollback()
    finally:
        db.close()


async def optimize_analytics_performance():
    """優化分析性能"""
    db = SessionLocal()
    try:
        logger.info("開始優化分析性能")
        
        # 分析資料庫查詢性能
        # 檢查索引使用情況
        
        # 統計表大小
        page_views_count = db.query(func.count(PageView.id)).scalar()
        sessions_count = db.query(func.count(UserSession.id)).scalar()
        
        logger.info(f"PageView 記錄數: {page_views_count}")
        logger.info(f"UserSession 記錄數: {sessions_count}")
        
        # 如果記錄過多，建議清理
        if page_views_count > 10000000:  # 1000萬條記錄
            logger.warning(f"PageView 記錄過多 ({page_views_count})，建議執行數據清理")
        
        if sessions_count > 1000000:  # 100萬條記錄
            logger.warning(f"UserSession 記錄過多 ({sessions_count})，建議執行數據清理")
        
        logger.info("分析性能優化完成")
        
    except Exception as e:
        logger.error(f"分析性能優化失敗: {e}")
    finally:
        db.close()


async def generate_analytics_report():
    """生成分析報告"""
    db = SessionLocal()
    try:
        logger.info("開始生成分析報告")
        
        now = datetime.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # 7天統計
        views_7d = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_7_days
        ).scalar() or 0
        
        visitors_7d = db.query(func.count(func.distinct(PageView.session_id))).filter(
            PageView.created_at >= last_7_days
        ).scalar() or 0
        
        # 30天統計
        views_30d = db.query(func.count(PageView.id)).filter(
            PageView.created_at >= last_30_days
        ).scalar() or 0
        
        visitors_30d = db.query(func.count(func.distinct(PageView.session_id))).filter(
            PageView.created_at >= last_30_days
        ).scalar() or 0
        
        # 熱門頁面
        top_pages = db.query(
            PageView.page_url,
            func.count(PageView.id).label('views')
        ).filter(
            PageView.created_at >= last_7_days
        ).group_by(PageView.page_url).order_by(
            desc('views')
        ).limit(10).all()
        
        report = {
            "generated_at": now.isoformat(),
            "period": "7 days",
            "stats": {
                "views_7d": views_7d,
                "visitors_7d": visitors_7d,
                "views_30d": views_30d,
                "visitors_30d": visitors_30d
            },
            "top_pages": [
                {
                    "url": page.page_url,
                    "views": page.views
                } for page in top_pages
            ]
        }
        
        logger.info(f"分析報告: {report}")
        
        return report
        
    except Exception as e:
        logger.error(f"生成分析報告失敗: {e}")
        return None
    finally:
        db.close()


# 任務調度器
class AnalyticsTaskScheduler:
    """分析任務調度器"""
    
    def __init__(self):
        self.running = False
    
    async def start_background_tasks(self):
        """啟動後台任務"""
        if self.running:
            return
        
        self.running = True
        logger.info("啟動分析後台任務")
        
        # 每小時更新熱門內容
        asyncio.create_task(self._schedule_popular_content_updates())
        
        # 每天午夜更新每日統計
        asyncio.create_task(self._schedule_daily_stats_updates())
        
        # 每周清理一次舊數據
        asyncio.create_task(self._schedule_data_cleanup())
        
        # 每小時優化一次性能
        asyncio.create_task(self._schedule_performance_optimization())
    
    async def stop_background_tasks(self):
        """停止後台任務"""
        self.running = False
        logger.info("停止分析後台任務")
    
    async def _schedule_popular_content_updates(self):
        """調度熱門內容更新"""
        while self.running:
            try:
                await update_popular_content()
                await asyncio.sleep(3600)  # 每小時執行一次
            except Exception as e:
                logger.error(f"熱門內容更新任務失敗: {e}")
                await asyncio.sleep(1800)  # 出錯時等待30分鐘後重試
    
    async def _schedule_daily_stats_updates(self):
        """調度每日統計更新"""
        while self.running:
            try:
                now = datetime.now()
                # 計算到下一個午夜的時間
                next_midnight = (now + timedelta(days=1)).replace(
                    hour=0, minute=5, second=0, microsecond=0
                )
                sleep_seconds = (next_midnight - now).total_seconds()
                
                await asyncio.sleep(sleep_seconds)
                await update_daily_stats()
                
            except Exception as e:
                logger.error(f"每日統計更新任務失敗: {e}")
                await asyncio.sleep(3600)  # 出錯時等待1小時後重試
    
    async def _schedule_data_cleanup(self):
        """調度數據清理"""
        while self.running:
            try:
                # 每周日凌晨3點執行清理
                now = datetime.now()
                days_until_sunday = (6 - now.weekday()) % 7
                next_sunday = (now + timedelta(days=days_until_sunday)).replace(
                    hour=3, minute=0, second=0, microsecond=0
                )
                if next_sunday <= now:
                    next_sunday += timedelta(days=7)
                
                sleep_seconds = (next_sunday - now).total_seconds()
                await asyncio.sleep(sleep_seconds)
                
                await cleanup_old_data()
                
            except Exception as e:
                logger.error(f"數據清理任務失敗: {e}")
                await asyncio.sleep(86400)  # 出錯時等待1天後重試
    
    async def _schedule_performance_optimization(self):
        """調度性能優化"""
        while self.running:
            try:
                await optimize_analytics_performance()
                await asyncio.sleep(3600)  # 每小時執行一次
            except Exception as e:
                logger.error(f"性能優化任務失敗: {e}")
                await asyncio.sleep(1800)  # 出錯時等待30分鐘後重試


# 全域任務調度器實例
task_scheduler = AnalyticsTaskScheduler() 