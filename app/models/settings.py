from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from .base import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="general")
    data_type = Column(String(20), nullable=False, default="string")  # string, boolean, integer, float, json
    is_public = Column(Boolean, default=False)  # 是否允許前端訪問
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 金流設定建議 key：
    # payment_transfer：轉帳設定（json，含銀行、帳號、戶名等）
    # payment_linepay：Line Pay 設定（json，含 channel_id、secret 等）
    # payment_ecpay：綠界設定（json，含 merchant_id、hashkey、hashiv 等）
    # value 欄位可存 json 格式
    
    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.parse_value(),
            "description": self.description,
            "category": self.category,
            "data_type": self.data_type,
            "is_public": self.is_public,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def parse_value(self):
        """根據數據類型解析值"""
        if self.value is None:
            return None
            
        if self.data_type == "boolean":
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.data_type == "integer":
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0
        elif self.data_type == "float":
            try:
                return float(self.value)
            except (ValueError, TypeError):
                return 0.0
        elif self.data_type == "json":
            import json
            try:
                return json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:
            return self.value 