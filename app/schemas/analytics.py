from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PageViewCreate(BaseModel):
    """頁面瀏覽記錄創建請求"""
    page_url: str = Field(..., description="頁面URL")
    page_title: Optional[str] = Field(None, description="頁面標題")
    page_type: str = Field(..., description="頁面類型")
    content_id: Optional[int] = Field(None, description="內容ID")
    user_agent: Optional[str] = Field(None, description="用戶代理")
    referer: Optional[str] = Field(None, description="來源頁面")
    session_id: str = Field(..., description="會話ID")
    device_type: Optional[str] = Field(None, description="設備類型")
    browser: Optional[str] = Field(None, description="瀏覽器")
    os: Optional[str] = Field(None, description="操作系統")
    country: Optional[str] = Field(None, description="國家")
    city: Optional[str] = Field(None, description="城市")


class HeartbeatRequest(BaseModel):
    """心跳請求"""
    session_id: str = Field(..., description="會話ID")


class RecentView(BaseModel):
    """最近瀏覽記錄"""
    page_url: str
    page_type: str
    time: str
    device: Optional[str] = None
    country: Optional[str] = None


class RealtimeStatsResponse(BaseModel):
    """即時統計響應"""
    current_time: str
    active_users: int
    hour_views: int
    day_views: int
    recent_views: List[RecentView]


class ContentStat(BaseModel):
    """內容統計"""
    content_id: int
    content_type: str
    total_views: int
    unique_views: int
    unique_sessions: int
    today_views: int
    title: str
    url: str
    published_at: Optional[str] = None
    category: Optional[str] = None


class ContentStatsResponse(BaseModel):
    """內容統計響應"""
    content_stats: List[ContentStat]
    total_count: int
    period_days: int
    calculated_at: str


class DailyTrend(BaseModel):
    """每日趨勢數據"""
    date: str
    views: int
    visitors: int


class PageTypeStats(BaseModel):
    """頁面類型統計"""
    type: str
    views: int


class DeviceStats(BaseModel):
    """設備統計"""
    device: str
    views: int


class AnalyticsOverviewResponse(BaseModel):
    """分析概覽響應"""
    total_views: int
    unique_visitors: int
    unique_ips: int
    total_orders: int
    total_revenue: float
    today_views: int
    today_orders: int
    today_revenue: float
    active_sessions: int
    period_days: int
    calculated_at: str


class DeviceStatItem(BaseModel):
    """設備統計項目"""
    name: str
    count: int
    percentage: float


class DeviceStatsResponse(BaseModel):
    """設備統計響應"""
    devices: List[DeviceStatItem]
    browsers: List[DeviceStatItem]
    total_sessions: int
    period_days: int
    calculated_at: str


class TopContentItem(BaseModel):
    """熱門內容項目"""
    content_id: int
    title: str
    url: str
    total_views: int
    unique_views: int


class TopContentResponse(BaseModel):
    """熱門內容響應"""
    content_type: str
    period_days: int
    top_content: List[TopContentItem]
    calculated_at: str


class TrendDataPoint(BaseModel):
    """趨勢數據點"""
    date: str
    total_views: int
    blog_views: int
    product_views: int
    unique_sessions: int


class TimeSeriesTrendsResponse(BaseModel):
    """時間序列趨勢響應"""
    granularity: str
    period_days: int
    trend_data: List[TrendDataPoint]
    calculated_at: str


class CacheInvalidateRequest(BaseModel):
    """快取清除請求"""
    pattern: Optional[str] = Field(None, description="快取模式")


class CacheInvalidateResponse(BaseModel):
    """快取清除響應"""
    status: str
    message: str
    timestamp: str


class UpdateResponse(BaseModel):
    """更新響應"""
    status: str
    message: str
    timestamp: str


class AnalyticsService(BaseModel):
    """分析服務配置"""
    redis_enabled: bool = False
    cache_ttl: int = 300
    realtime_enabled: bool = True 