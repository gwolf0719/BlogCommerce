from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BannerPosition(str, Enum):
    """
    廣告版位枚舉
    
    定義廣告可以顯示的版位：
    - HOME: 首頁
    - BLOG_LIST: 部落格文章列表
    - PRODUCT_LIST: 商品列表
    """
    HOME = "HOME"
    BLOG_LIST = "BLOG_LIST"
    PRODUCT_LIST = "PRODUCT_LIST"


class BannerBase(BaseModel):
    """
    廣告基礎 Schema
    
    包含廣告的基本資訊欄位。
    """
    title: str = Field(..., min_length=1, max_length=200, description="廣告標題")
    description: Optional[str] = Field(None, description="廣告描述")
    link_url: str = Field(..., min_length=1, max_length=500, description="點擊導向連結")
    mobile_image: str = Field(..., min_length=1, max_length=255, description="手機版圖片路徑")
    desktop_image: str = Field(..., min_length=1, max_length=255, description="電腦版圖片路徑")
    alt_text: Optional[str] = Field(None, max_length=200, description="圖片替代文字")
    position: BannerPosition = Field(..., description="顯示版位")
    start_date: datetime = Field(..., description="刊登開始時間")
    end_date: datetime = Field(..., description="刊登結束時間")
    is_active: bool = Field(True, description="是否啟用")
    sort_order: int = Field(0, description="排序權重，數字越大越優先")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """驗證結束時間必須大於開始時間"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('結束時間必須大於開始時間')
        return v
    
    @validator('link_url')
    def validate_link_url(cls, v):
        """驗證連結 URL 格式"""
        if not v.startswith(('http://', 'https://', '/')):
            raise ValueError('連結必須是有效的 URL 或相對路徑')
        return v


class BannerCreate(BannerBase):
    """
    建立廣告 Schema
    
    用於建立新廣告時的資料驗證。
    """
    pass


class BannerUpdate(BaseModel):
    """
    更新廣告 Schema
    
    用於更新廣告時的資料驗證，所有欄位都是可選的。
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="廣告標題")
    description: Optional[str] = Field(None, description="廣告描述")
    link_url: Optional[str] = Field(None, min_length=1, max_length=500, description="點擊導向連結")
    mobile_image: Optional[str] = Field(None, min_length=1, max_length=255, description="手機版圖片路徑")
    desktop_image: Optional[str] = Field(None, min_length=1, max_length=255, description="電腦版圖片路徑")
    alt_text: Optional[str] = Field(None, max_length=200, description="圖片替代文字")
    position: Optional[BannerPosition] = Field(None, description="顯示版位")
    start_date: Optional[datetime] = Field(None, description="刊登開始時間")
    end_date: Optional[datetime] = Field(None, description="刊登結束時間")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    sort_order: Optional[int] = Field(None, description="排序權重，數字越大越優先")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """驗證結束時間必須大於開始時間"""
        if v and 'start_date' in values and values['start_date'] and v <= values['start_date']:
            raise ValueError('結束時間必須大於開始時間')
        return v
    
    @validator('link_url')
    def validate_link_url(cls, v):
        """驗證連結 URL 格式"""
        if v and not v.startswith(('http://', 'https://', '/')):
            raise ValueError('連結必須是有效的 URL 或相對路徑')
        return v


class BannerResponse(BannerBase):
    """
    廣告回應 Schema
    
    用於 API 回應時的資料格式。
    """
    id: int = Field(..., description="廣告 ID")
    click_count: int = Field(0, description="點擊次數")
    view_count: int = Field(0, description="瀏覽次數")
    is_valid_period: bool = Field(..., description="是否在有效期間內")
    is_displayable: bool = Field(..., description="是否可以顯示")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")
    
    class Config:
        from_attributes = True


class BannerSummary(BannerResponse):
    """廣告列表項目摘要"""
    pass


class BannerListResponse(BaseModel):
    """廣告列表的分頁回應"""
    items: List[BannerSummary]
    total: int



class BannerStatusToggle(BaseModel):
    """
    廣告狀態切換 Schema
    
    用於切換廣告啟用狀態。
    """
    is_active: bool = Field(..., description="是否啟用")


class BannerClickTrack(BaseModel):
    """
    廣告點擊追蹤 Schema
    
    用於記錄廣告點擊事件。
    """
    banner_id: int = Field(..., description="廣告 ID")
    user_ip: Optional[str] = Field(None, description="用戶 IP")
    user_agent: Optional[str] = Field(None, description="用戶代理")
    referrer: Optional[str] = Field(None, description="來源頁面")


class BannerStats(BaseModel):
    """
    廣告統計 Schema
    
    用於廣告統計資料的回應。
    """
    total_banners: int = Field(..., description="總廣告數")
    active_banners: int = Field(..., description="啟用廣告數")
    expired_banners: int = Field(..., description="過期廣告數")
    total_clicks: int = Field(..., description="總點擊次數")
    position_stats: dict = Field(..., description="各版位統計")
    
    class Config:
        from_attributes = True 