import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import traceback
import json

# 創建logs目錄
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

class CustomFormatter(logging.Formatter):
    """自定義日誌格式化器"""
    
    def format(self, record):
        # 添加時間戳
        record.timestamp = datetime.now().isoformat()
        
        # 格式化錯誤信息
        if record.exc_info:
            record.exception_details = traceback.format_exception(*record.exc_info)
        
        return super().format(record)

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """設置日誌記錄器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    # 文件處理器 - 所有日誌
    file_handler = logging.FileHandler(
        logs_dir / f"{name}.log", 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 錯誤文件處理器 - 只記錄錯誤
    error_handler = logging.FileHandler(
        logs_dir / f"{name}_errors.log", 
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 日誌格式
    formatter = CustomFormatter(
        '%(timestamp)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# 創建不同模組的日誌記錄器
app_logger = setup_logger("app")
api_logger = setup_logger("api")
db_logger = setup_logger("database")
auth_logger = setup_logger("auth")
admin_logger = setup_logger("admin")

def log_api_error(endpoint: str, error: Exception, request_data: Optional[dict] = None):
    """記錄API錯誤"""
    error_info = {
        "endpoint": endpoint,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_data": request_data,
        "traceback": traceback.format_exc()
    }
    api_logger.error(f"API錯誤: {json.dumps(error_info, ensure_ascii=False, indent=2)}")

def log_db_error(operation: str, error: Exception, context: Optional[dict] = None):
    """記錄資料庫錯誤"""
    error_info = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc()
    }
    db_logger.error(f"資料庫錯誤: {json.dumps(error_info, ensure_ascii=False, indent=2)}")

def log_auth_error(action: str, username: str, error: Exception):
    """記錄認證錯誤"""
    error_info = {
        "action": action,
        "username": username,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    auth_logger.error(f"認證錯誤: {json.dumps(error_info, ensure_ascii=False, indent=2)}")

def log_validation_error(model: str, errors: list, data: Optional[dict] = None):
    """記錄驗證錯誤"""
    error_info = {
        "model": model,
        "validation_errors": errors,
        "input_data": data
    }
    api_logger.error(f"驗證錯誤: {json.dumps(error_info, ensure_ascii=False, indent=2)}")

# 日誌中間件
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 記錄請求開始
            try:
                # 安全地處理headers（將bytes轉換為字符串）
                headers = {}
                for name, value in scope.get("headers", []):
                    try:
                        key = name.decode('utf-8') if isinstance(name, bytes) else str(name)
                        val = value.decode('utf-8') if isinstance(value, bytes) else str(value)
                        headers[key] = val
                    except UnicodeDecodeError:
                        headers[str(name)] = str(value)
                
                request_info = {
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "query_string": scope.get("query_string", b"").decode('utf-8', errors='replace'),
                    "client": scope.get("client"),
                    "headers": headers
                }
                api_logger.info(f"請求開始: {json.dumps(request_info, ensure_ascii=False)}")
            except Exception as e:
                # 如果日誌記錄失敗，不影響請求處理
                api_logger.error(f"記錄請求日誌失敗: {e}")
        
        # 繼續處理請求
        await self.app(scope, receive, send) 