from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Enum
from sqlalchemy.sql import func
from app.models.base import BaseModel
from enum import Enum as PyEnum


class BannerPosition(PyEnum):
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


class Banner(BaseModel):
    """
    輪播廣告模型
    
    用於管理網站各版位的輪播廣告，支援多種版位顯示，
    包含時間範圍控制和點擊統計功能。
    """
    __tablename__ = "banners"
    
    # 基本資訊
    title = Column(String(200), nullable=False, comment="廣告標題")
    description = Column(Text, nullable=True, comment="廣告描述")
    link_url = Column(String(500), nullable=False, comment="點擊導向連結")
    
    # 圖片資訊
    mobile_image = Column(String(255), nullable=False, comment="手機版圖片路徑")
    desktop_image = Column(String(255), nullable=False, comment="電腦版圖片路徑")
    alt_text = Column(String(200), nullable=True, comment="圖片替代文字")
    
    # 版位資訊
    position = Column(
        Enum(BannerPosition), 
        nullable=False, 
        comment="顯示版位"
    )
    
    # 時間控制
    start_date = Column(
        DateTime(timezone=True), 
        nullable=False, 
        comment="刊登開始時間"
    )
    end_date = Column(
        DateTime(timezone=True), 
        nullable=False, 
        comment="刊登結束時間"
    )
    
    # 狀態控制
    is_active = Column(Boolean, default=True, comment="是否啟用")
    sort_order = Column(Integer, default=0, comment="排序權重，數字越大越優先")
    
    # 統計資訊
    click_count = Column(Integer, default=0, comment="點擊次數")
    
    # 新增屬性用於檢查廣告是否在有效期間內
    @property
    def is_valid_period(self):
        """檢查廣告是否在有效期間內"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # 如果日期沒有時區信息，則假設為 UTC
        start_date = self.start_date
        end_date = self.end_date
        
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
            
        return start_date <= now <= end_date
    
    @property
    def is_displayable(self):
        """檢查廣告是否可以顯示（啟用且在有效期間內）"""
        return self.is_active and self.is_valid_period
    
    def increment_click_count(self):
        """增加點擊次數"""
        self.click_count += 1
    
    def __repr__(self):
        return f"<Banner {self.title} - {self.position.value}>" 