from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.services.error_log_service import ErrorLogService
from app.schemas.error_log import (
    ErrorLogCreate, ErrorLogResponse, ErrorLogUpdate, 
    ErrorLogFilter, ErrorLogStats
)
from app.models.error_log import ErrorSource, ErrorSeverity
from app.auth import get_current_admin_user

router = APIRouter(prefix="/api/error-logs", tags=["錯誤日誌"])

def get_error_log_service(db: Session = Depends(get_db)) -> ErrorLogService:
    return ErrorLogService(db)

@router.post("/log", response_model=ErrorLogResponse)
async def create_error_log(
    error_data: ErrorLogCreate,
    request: Request,
    service: ErrorLogService = Depends(get_error_log_service)
):
    """記錄錯誤日誌"""
    try:
        # 自動填入 IP 地址
        if not error_data.ip_address and request.client:
            error_data.ip_address = request.client.host
        
        # 自動填入 User-Agent
        if not error_data.user_agent:
            error_data.user_agent = request.headers.get("user-agent")
        
        error_log = service.create_error_log(error_data)
        return ErrorLogResponse.from_orm(error_log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"記錄錯誤日誌失敗: {str(e)}")

class FrontendErrorData(BaseModel):
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    url: Optional[str] = None
    browser_info: Optional[dict] = None
    device_info: Optional[dict] = None
    severity: Optional[str] = "MEDIUM"
    tags: Optional[List[str]] = None

@router.post("/log/frontend", response_model=ErrorLogResponse)
async def log_frontend_error(
    error_data: FrontendErrorData,
    request: Request,
    service: ErrorLogService = Depends(get_error_log_service)
):
    """記錄前端錯誤"""
    try:
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        
        # 轉換嚴重性等級
        severity = ErrorSeverity.MEDIUM
        if error_data.severity:
            try:
                severity = ErrorSeverity(error_data.severity.upper())
            except ValueError:
                severity = ErrorSeverity.MEDIUM
        
        error_log = service.log_frontend_error(
            error_type=error_data.error_type,
            error_message=error_data.error_message,
            stack_trace=error_data.stack_trace,
            url=error_data.url,
            user_agent=user_agent,
            browser_info=error_data.browser_info,
            device_info=error_data.device_info,
            severity=severity,
            tags=error_data.tags
        )
        return ErrorLogResponse.from_orm(error_log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"記錄前端錯誤失敗: {str(e)}")

@router.get("/", response_model=List[ErrorLogResponse])
async def get_error_logs(
    source: Optional[ErrorSource] = None,
    severity: Optional[ErrorSeverity] = None,
    error_type: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    service: ErrorLogService = Depends(get_error_log_service),
    current_admin = Depends(get_current_admin_user)
):
    """取得錯誤日誌列表（需要管理員權限）"""
    try:
        filter_params = ErrorLogFilter(
            source=source,
            severity=severity,
            error_type=error_type,
            is_resolved=is_resolved,
            start_date=start_date,
            end_date=end_date,
            search=search
        )
        
        error_logs = service.get_error_logs(filter_params, skip, limit)
        return [ErrorLogResponse.from_orm(log) for log in error_logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得錯誤日誌失敗: {str(e)}")

@router.get("/stats", response_model=ErrorLogStats)
async def get_error_stats(
    days: int = Query(default=30, ge=1, le=365),
    service: ErrorLogService = Depends(get_error_log_service),
    current_admin = Depends(get_current_admin_user)
):
    """取得錯誤統計資料（需要管理員權限）"""
    try:
        return service.get_error_stats(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得錯誤統計失敗: {str(e)}")

@router.get("/{error_id}", response_model=ErrorLogResponse)
async def get_error_log(
    error_id: int,
    service: ErrorLogService = Depends(get_error_log_service),
    current_admin = Depends(get_current_admin_user)
):
    """取得特定錯誤日誌（需要管理員權限）"""
    error_log = service.get_error_log_by_id(error_id)
    if not error_log:
        raise HTTPException(status_code=404, detail="錯誤日誌不存在")
    return ErrorLogResponse.from_orm(error_log)

@router.put("/{error_id}", response_model=ErrorLogResponse)
async def update_error_log(
    error_id: int,
    update_data: ErrorLogUpdate,
    service: ErrorLogService = Depends(get_error_log_service),
    current_admin = Depends(get_current_admin_user)
):
    """更新錯誤日誌（需要管理員權限）"""
    error_log = service.update_error_log(error_id, update_data)
    if not error_log:
        raise HTTPException(status_code=404, detail="錯誤日誌不存在")
    return ErrorLogResponse.from_orm(error_log)

@router.delete("/{error_id}")
async def delete_error_log(
    error_id: int,
    service: ErrorLogService = Depends(get_error_log_service),
    current_admin = Depends(get_current_admin_user)
):
    """刪除錯誤日誌（需要管理員權限）"""
    success = service.delete_error_log(error_id)
    if not success:
        raise HTTPException(status_code=404, detail="錯誤日誌不存在")
    return {"message": "錯誤日誌已刪除"}

@router.post("/clean")
async def clean_old_errors(
    days: int = Query(default=90, ge=30, le=365),
    service: ErrorLogService = Depends(get_error_log_service),
    current_admin = Depends(get_current_admin_user)
):
    """清理舊的已解決錯誤日誌（需要管理員權限）"""
    try:
        deleted_count = service.clean_old_errors(days)
        return {"message": f"已清理 {deleted_count} 條舊的錯誤日誌"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理錯誤日誌失敗: {str(e)}") 