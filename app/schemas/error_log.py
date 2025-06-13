from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.error_log import ErrorSource, ErrorSeverity

class ErrorLogCreate(BaseModel):
    source: ErrorSource
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    error_type: str = Field(..., max_length=100)
    error_message: str
    stack_trace: Optional[str] = None
    url: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = Field(None, max_length=500)
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    browser_info: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class ErrorLogUpdate(BaseModel):
    is_resolved: Optional[bool] = None
    resolution_note: Optional[str] = None
    tags: Optional[List[str]] = None

class ErrorLogResponse(BaseModel):
    id: int
    source: ErrorSource
    severity: ErrorSeverity
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    browser_info: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_resolved: bool
    resolution_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z' if v else None
        }

class ErrorLogFilter(BaseModel):
    source: Optional[ErrorSource] = None
    severity: Optional[ErrorSeverity] = None
    error_type: Optional[str] = None
    is_resolved: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None  # 搜尋錯誤訊息或 URL
    tags: Optional[List[str]] = None

class ErrorLogStats(BaseModel):
    total_errors: int
    resolved_errors: int
    unresolved_errors: int
    errors_by_source: Dict[str, int]
    errors_by_severity: Dict[str, int]
    recent_errors: List[ErrorLogResponse] 