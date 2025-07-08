from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel


class PageView(BaseModel):
    """頁面瀏覽記錄"""
    __tablename__ = "page_views"
    
    # 基本信息
    page_url = Column(String(500), nullable=False, index=True)
    page_title = Column(String(200), nullable=True)
    page_type = Column(String(50), nullable=False, index=True)  # home, blog, product, category, etc.
    
    # 關聯ID（用於具體頁面）
    content_id = Column(Integer, nullable=True, index=True)  # 文章ID、商品ID等
    
    # 訪客信息
    visitor_ip = Column(String(45), nullable=True, index=True)  # IPv4/IPv6
    user_agent = Column(Text, nullable=True)
    referer = Column(String(500), nullable=True)
    
    # 用戶信息（如果已登入）
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # 地理位置信息
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # 設備信息
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    # 時間信息
    session_id = Column(String(100), nullable=True, index=True)
    view_duration = Column(Integer, nullable=True)  # 停留時間（秒）
    
    # 索引優化
    __table_args__ = (
        Index('idx_page_views_date_type', 'created_at', 'page_type'),
        Index('idx_page_views_content', 'page_type', 'content_id'),
        Index('idx_page_views_ip_date', 'visitor_ip', 'created_at'),
    )


class DailyStats(BaseModel):
    """每日統計數據"""
    __tablename__ = "daily_stats"
    
    stat_date = Column(DateTime, nullable=False, index=True)
    
    # 基本統計
    total_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    unique_ips = Column(Integer, default=0)
    
    # 頁面類型統計
    home_views = Column(Integer, default=0)
    blog_views = Column(Integer, default=0)
    product_views = Column(Integer, default=0)
    category_views = Column(Integer, default=0)
    
    # 設備統計
    desktop_views = Column(Integer, default=0)
    mobile_views = Column(Integer, default=0)
    tablet_views = Column(Integer, default=0)
    
    # 用戶統計
    registered_user_views = Column(Integer, default=0)
    guest_views = Column(Integer, default=0)
    
    # 平均數據
    avg_session_duration = Column(Integer, default=0)  # 秒
    bounce_rate = Column(Integer, default=0)  # 百分比


class PopularContent(BaseModel):
    """熱門內容統計"""
    __tablename__ = "popular_content"
    
    content_type = Column(String(50), nullable=False, index=True)  # post, product
    content_id = Column(Integer, nullable=False, index=True)
    content_title = Column(String(200), nullable=False)
    content_url = Column(String(500), nullable=False)
    
    # 統計數據
    total_views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    today_views = Column(Integer, default=0)
    week_views = Column(Integer, default=0)
    month_views = Column(Integer, default=0)
    
    # 最後更新時間
    last_viewed = Column(DateTime, default=datetime.utcnow)


class UserSession(BaseModel):
    """用戶會話記錄"""
    __tablename__ = "user_sessions"
    
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    visitor_ip = Column(String(45), nullable=False, index=True)
    
    # 會話信息
    start_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # 統計信息
    page_views = Column(Integer, default=0)
    duration = Column(Integer, default=0)  # 總時長（秒）
    is_bounce = Column(Boolean, default=True)  # 是否跳出
    
    # 設備信息
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    # 地理信息
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # 來源信息
    referer = Column(String(500), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)