from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.base import BaseModel


class ShippingTier(BaseModel):
    """
    運費級距模型
    
    用於管理多段運費級距設定，支援根據訂單金額或重量
    計算對應的運費金額。
    """
    __tablename__ = "shipping_tiers"
    
    # 基本資訊
    name = Column(String(100), nullable=False, comment="級距名稱")
    description = Column(String(500), nullable=True, comment="級距描述")
    
    # 級距範圍 (以訂單金額為基準)
    min_amount = Column(
        Numeric(10, 2), 
        nullable=False, 
        default=0,
        comment="最低訂單金額 (包含)"
    )
    max_amount = Column(
        Numeric(10, 2), 
        nullable=True,
        comment="最高訂單金額 (不包含)，NULL表示無上限"
    )
    
    # 運費設定
    shipping_fee = Column(
        Numeric(10, 2), 
        nullable=False, 
        default=0,
        comment="運費金額"
    )
    
    # 免運設定
    free_shipping = Column(
        Boolean, 
        default=False, 
        comment="是否免運費"
    )
    
    # 狀態控制
    is_active = Column(Boolean, default=True, comment="是否啟用")
    sort_order = Column(Integer, default=0, comment="排序權重，數字越大越優先")
    
    # 時間記錄
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="更新時間"
    )
    
    @property
    def is_unlimited_max(self):
        """檢查是否為無上限級距"""
        return self.max_amount is None
    
    def applies_to_amount(self, amount):
        """
        檢查指定金額是否適用此級距
        
        Args:
            amount (Decimal): 訂單金額
            
        Returns:
            bool: 是否適用此級距
        """
        if self.is_active is False:
            return False
            
        # 檢查最低金額
        if amount < self.min_amount:
            return False
            
        # 檢查最高金額 (如果有設定)
        if self.max_amount is not None and amount >= self.max_amount:
            return False
            
        return True
    
    def get_shipping_cost(self):
        """
        取得運費金額
        
        Returns:
            Decimal: 運費金額，免運費則返回 0
        """
        if self.free_shipping:
            return 0
        return self.shipping_fee
    
    def __repr__(self):
        max_amount_str = "無上限" if self.is_unlimited_max else str(self.max_amount)
        return f"<ShippingTier {self.name}: ${self.min_amount} - ${max_amount_str}, 運費: ${self.shipping_fee}>" 