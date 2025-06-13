from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request
from app.models.error_log import ErrorLog, ErrorSource, ErrorSeverity
from app.schemas.error_log import ErrorLogCreate, ErrorLogUpdate, ErrorLogResponse, ErrorLogFilter, ErrorLogStats
from app.utils.logger import app_logger
import traceback
import json

class ErrorLogService:
    def __init__(self, db: Session):
        self.db = db

    def create_error_log(self, error_data: ErrorLogCreate) -> ErrorLog:
        """建立錯誤日誌記錄"""
        try:
            db_error = ErrorLog(**error_data.model_dump())
            self.db.add(db_error)
            self.db.commit()
            self.db.refresh(db_error)
            return db_error
        except Exception as e:
            self.db.rollback()
            app_logger.error(f"建立錯誤日誌失敗: {e}")
            raise

    def log_frontend_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        url: Optional[str] = None,
        user_agent: Optional[str] = None,
        browser_info: Optional[Dict[str, Any]] = None,
        device_info: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        tags: Optional[List[str]] = None
    ) -> ErrorLog:
        """記錄前端錯誤"""
        error_data = ErrorLogCreate(
            source=ErrorSource.FRONTEND,
            severity=severity,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            url=url,
            user_agent=user_agent,
            user_id=user_id,
            session_id=session_id,
            browser_info=browser_info,
            device_info=device_info,
            tags=tags
        )
        return self.create_error_log(error_data)

    def log_backend_error(
        self,
        error: Exception,
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        tags: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ErrorLog:
        """記錄後端錯誤"""
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        url = None
        user_agent = None
        ip_address = None
        request_data = None
        
        if request:
            url = str(request.url)
            user_agent = request.headers.get("user-agent")
            ip_address = request.client.host if request.client else None
            
            # 安全地記錄請求數據，避免敏感信息
            try:
                request_data = {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "headers": dict(request.headers),
                }
                if additional_data:
                    request_data.update(additional_data)
            except Exception:
                request_data = {"error": "無法序列化請求數據"}

        error_data = ErrorLogCreate(
            source=ErrorSource.BACKEND,
            severity=severity,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            url=url,
            user_agent=user_agent,
            user_id=user_id,
            ip_address=ip_address,
            request_data=request_data,
            tags=tags
        )
        return self.create_error_log(error_data)

    def log_api_error(
        self,
        error: Exception,
        endpoint: str,
        method: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        tags: Optional[List[str]] = None
    ) -> ErrorLog:
        """記錄API錯誤"""
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()

        error_data = ErrorLogCreate(
            source=ErrorSource.API,
            severity=severity,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            url=endpoint,
            user_id=user_id,
            request_data={"method": method, "data": request_data},
            response_data=response_data,
            tags=tags
        )
        return self.create_error_log(error_data)

    def get_error_logs(
        self,
        filter_params: Optional[ErrorLogFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ErrorLog]:
        """取得錯誤日誌列表"""
        query = self.db.query(ErrorLog)
        
        if filter_params:
            if filter_params.source:
                query = query.filter(ErrorLog.source == filter_params.source)
            if filter_params.severity:
                query = query.filter(ErrorLog.severity == filter_params.severity)
            if filter_params.error_type:
                query = query.filter(ErrorLog.error_type.ilike(f"%{filter_params.error_type}%"))
            if filter_params.is_resolved is not None:
                query = query.filter(ErrorLog.is_resolved == filter_params.is_resolved)
            if filter_params.start_date:
                query = query.filter(ErrorLog.created_at >= filter_params.start_date)
            if filter_params.end_date:
                query = query.filter(ErrorLog.created_at <= filter_params.end_date)
            if filter_params.search:
                search_term = f"%{filter_params.search}%"
                query = query.filter(
                    or_(
                        ErrorLog.error_message.ilike(search_term),
                        ErrorLog.url.ilike(search_term),
                        ErrorLog.error_type.ilike(search_term)
                    )
                )
            if filter_params.tags:
                # 搜尋包含任何指定標籤的錯誤
                for tag in filter_params.tags:
                    query = query.filter(ErrorLog.tags.contains([tag]))
        
        return query.order_by(desc(ErrorLog.created_at)).offset(skip).limit(limit).all()

    def get_error_log_by_id(self, error_id: int) -> Optional[ErrorLog]:
        """根據ID取得錯誤日誌"""
        return self.db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

    def update_error_log(self, error_id: int, update_data: ErrorLogUpdate) -> Optional[ErrorLog]:
        """更新錯誤日誌"""
        error_log = self.get_error_log_by_id(error_id)
        if error_log:
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(error_log, key, value)
            
            self.db.commit()
            self.db.refresh(error_log)
            return error_log
        return None

    def delete_error_log(self, error_id: int) -> bool:
        """刪除錯誤日誌"""
        error_log = self.get_error_log_by_id(error_id)
        if error_log:
            self.db.delete(error_log)
            self.db.commit()
            return True
        return False

    def get_error_stats(self, days: int = 30) -> ErrorLogStats:
        """取得錯誤統計資料"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 總錯誤數
        total_errors = self.db.query(ErrorLog).filter(
            ErrorLog.created_at >= start_date
        ).count()
        
        # 已解決的錯誤數
        resolved_errors = self.db.query(ErrorLog).filter(
            and_(
                ErrorLog.created_at >= start_date,
                ErrorLog.is_resolved == True
            )
        ).count()
        
        # 未解決的錯誤數
        unresolved_errors = total_errors - resolved_errors
        
        # 按來源分類的錯誤數
        source_stats = self.db.query(
            ErrorLog.source,
            func.count(ErrorLog.id).label('count')
        ).filter(
            ErrorLog.created_at >= start_date
        ).group_by(ErrorLog.source).all()
        
        errors_by_source = {str(source): count for source, count in source_stats}
        
        # 按嚴重程度分類的錯誤數
        severity_stats = self.db.query(
            ErrorLog.severity,
            func.count(ErrorLog.id).label('count')
        ).filter(
            ErrorLog.created_at >= start_date
        ).group_by(ErrorLog.severity).all()
        
        errors_by_severity = {str(severity): count for severity, count in severity_stats}
        
        # 最近的錯誤
        recent_errors = self.db.query(ErrorLog).filter(
            ErrorLog.created_at >= start_date
        ).order_by(desc(ErrorLog.created_at)).limit(10).all()
        
        return ErrorLogStats(
            total_errors=total_errors,
            resolved_errors=resolved_errors,
            unresolved_errors=unresolved_errors,
            errors_by_source=errors_by_source,
            errors_by_severity=errors_by_severity,
            recent_errors=[ErrorLogResponse.from_orm(error) for error in recent_errors]
        )

    def clean_old_errors(self, days: int = 90) -> int:
        """清理舊的錯誤日誌"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = self.db.query(ErrorLog).filter(
            and_(
                ErrorLog.created_at < cutoff_date,
                ErrorLog.is_resolved == True
            )
        ).delete()
        
        self.db.commit()
        return deleted_count 