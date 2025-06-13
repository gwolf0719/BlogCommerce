from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum

class ErrorSource(str, enum.Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    API = "api"
    DATABASE = "database"

class ErrorSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorLog(Base):
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(Enum(ErrorSource), nullable=False)  # 錯誤來源
    severity = Column(Enum(ErrorSeverity), default=ErrorSeverity.MEDIUM)  # 嚴重程度
    error_type = Column(String(100), nullable=False)  # 錯誤類型
    error_message = Column(Text, nullable=False)  # 錯誤訊息
    stack_trace = Column(Text)  # 堆疊追蹤
    url = Column(String(500))  # 錯誤發生的URL
    user_agent = Column(String(500))  # 用戶代理字串
    user_id = Column(Integer)  # 用戶ID（如果已登入）
    session_id = Column(String(100))  # 會話ID
    ip_address = Column(String(45))  # IP地址
    request_data = Column(JSON)  # 請求數據
    response_data = Column(JSON)  # 響應數據
    browser_info = Column(JSON)  # 瀏覽器資訊
    device_info = Column(JSON)  # 設備資訊
    tags = Column(JSON)  # 標籤（用於分類和搜尋）
    is_resolved = Column(Boolean, default=False)  # 是否已解決
    resolution_note = Column(Text)  # 解決方案說明
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, source={self.source}, type={self.error_type})>" 