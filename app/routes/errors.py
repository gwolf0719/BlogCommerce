from fastapi import APIRouter, Request
from app.utils.logger import app_logger

router = APIRouter(prefix="/errors", tags=["錯誤日誌"])

@router.post("/log")
async def log_frontend_error(request: Request):
    """記錄前端錯誤"""
    try:
        error_data = await request.json()
        app_logger.error(f"[Frontend Error]: {error_data}")
        return {"status": "logged"}
    except Exception as e:
        app_logger.error(f"記錄前端錯誤失敗: {e}")
        return {"status": "failed", "error": str(e)}
