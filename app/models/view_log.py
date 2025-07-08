from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime


class ViewLog(BaseModel):
    __tablename__ = "view_logs"
    
    # 瀏覽對象類型和ID
    content_type = Column(String(50), nullable=False)  # 'post' 或 'product'
    content_id = Column(Integer, nullable=False)
    
    # 用戶信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 登入用戶
    session_id = Column(String(255), nullable=True)  # 未登入用戶的 session
    ip_address = Column(String(45), nullable=True)  # IP 地址
    user_agent = Column(Text, nullable=True)  # 瀏覽器信息
    
    # 來源信息
    referrer = Column(String(500), nullable=True)  # 來源頁面
    utm_source = Column(String(100), nullable=True)  # UTM 來源
    utm_medium = Column(String(100), nullable=True)  # UTM 媒介
    utm_campaign = Column(String(100), nullable=True)  # UTM 活動
    
    # 瀏覽時間
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration = Column(Integer, nullable=True)  # 停留時間（秒）
    
    # 關聯
    user = relationship("User", back_populates="view_logs")
    
    def __repr__(self):
        return f"<ViewLog {self.content_type}:{self.content_id} by {self.user_id or self.session_id}>" 