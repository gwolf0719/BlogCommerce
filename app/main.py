from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.config import settings
from app.database import init_db
from app.middleware import get_feature_settings, get_public_settings
from pathlib import Path
from fastapi.responses import FileResponse
from app.api import router as api_router
from app.utils.logger import app_logger, log_api_error, log_validation_error, LoggingMiddleware

# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.site_name,
    description=settings.site_description,
    version="1.0.0",
    debug=settings.debug
)

# 日誌中間件
app.add_middleware(LoggingMiddleware)

# Session 中介軟體（用於購物車功能）
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# CORS 設定（開發階段允許所有來源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境請改為具體域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案設定
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# 模板設定
templates = Jinja2Templates(directory="app/templates")

# 包含 API 路由
app.include_router(api_router)

# 全局異常處理器
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """處理HTTP異常"""
    log_api_error(f"{request.method} {request.url.path}", exc, {"status_code": exc.status_code})
    
    # 同時記錄到錯誤日誌系統
    try:
        from app.database import SessionLocal
        from app.services.error_log_service import ErrorLogService
        from app.models.error_log import ErrorSeverity
        
        db = SessionLocal()
        try:
            error_service = ErrorLogService(db)
            severity = ErrorSeverity.CRITICAL if exc.status_code >= 500 else ErrorSeverity.MEDIUM
            error_service.log_backend_error(
                error=exc,
                request=request,
                severity=severity,
                tags=['http_exception', f'status_{exc.status_code}']
            )
        finally:
            db.close()
    except Exception as e:
        app_logger.error(f"記錄HTTP異常到錯誤日誌系統失敗: {e}")
    
    return await http_exception_handler(request, exc)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """處理驗證錯誤"""
    log_validation_error("Request", exc.errors(), None)
    
    # 同時記錄到錯誤日誌系統
    try:
        from app.database import SessionLocal
        from app.services.error_log_service import ErrorLogService
        from app.models.error_log import ErrorSeverity
        
        db = SessionLocal()
        try:
            error_service = ErrorLogService(db)
            error_service.log_backend_error(
                error=exc,
                request=request,
                severity=ErrorSeverity.MEDIUM,
                tags=['validation', 'pydantic']
            )
        finally:
            db.close()
    except Exception as e:
        app_logger.error(f"記錄驗證錯誤到錯誤日誌系統失敗: {e}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": "驗證錯誤", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """處理一般異常"""
    log_api_error(f"{request.method} {request.url.path}", exc)
    
    # 同時記錄到錯誤日誌系統
    try:
        from app.database import SessionLocal
        from app.services.error_log_service import ErrorLogService
        from app.models.error_log import ErrorSeverity
        
        db = SessionLocal()
        try:
            error_service = ErrorLogService(db)
            error_service.log_backend_error(
                error=exc,
                request=request,
                severity=ErrorSeverity.CRITICAL,
                tags=['unhandled_exception', 'server_error']
            )
        finally:
            db.close()
    except Exception as e:
        app_logger.error(f"記錄一般異常到錯誤日誌系統失敗: {e}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "內部服務器錯誤"}
    )

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用程式啟動時初始化資料庫"""
    app_logger.info("應用程式正在啟動...")
    init_db()
    app_logger.info("資料庫初始化完成")
    app_logger.info(f"應用程式已啟動，運行在 {settings.debug and 'DEBUG' or 'PRODUCTION'} 模式")

# 前端路由
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "settings": settings})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "settings": settings})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request, "settings": settings})

@app.get("/products")
async def products_page(request: Request):
    return templates.TemplateResponse("shop/products.html", {"request": request, "settings": settings})

@app.get("/product/{slug}")
async def product_detail_page(request: Request, slug: str):
    return templates.TemplateResponse("shop/product_detail.html", {"request": request, "slug": slug, "settings": settings})

@app.get("/cart")
async def cart_page(request: Request):
    return templates.TemplateResponse("shop/cart.html", {"request": request, "settings": settings})

@app.get("/checkout")
async def checkout_page(request: Request):
    return templates.TemplateResponse("shop/checkout.html", {"request": request, "settings": settings})

@app.get("/blog")
async def blog_page(request: Request):
    return templates.TemplateResponse("blog/posts.html", {"request": request, "settings": settings})

@app.get("/blog/{slug}")
async def post_detail_page(request: Request, slug: str):
    # 這個路由現在會由前端 JavaScript 處理，模板只需要 slug
    return templates.TemplateResponse("blog/post_detail.html", {
        "request": request, 
        "slug": slug, 
        "settings": settings,
        "post": None  # 暫時設為 None，由前端 API 載入
    })

@app.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse("auth/profile.html", {"request": request, "settings": settings})

@app.get("/orders")
async def orders_page(request: Request):
    return templates.TemplateResponse("shop/orders.html", {"request": request, "settings": settings})

@app.get("/favorites")
async def favorites_page(request: Request):
    return templates.TemplateResponse("shop/favorites.html", {"request": request, "settings": settings})

# Footer 頁面路由
@app.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse("pages/about.html", {"request": request, "settings": settings})

@app.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse("pages/contact.html", {"request": request, "settings": settings})

@app.get("/help")
async def help_page(request: Request):
    return templates.TemplateResponse("pages/help.html", {"request": request, "settings": settings})

@app.get("/shipping")
async def shipping_page(request: Request):
    return templates.TemplateResponse("pages/shipping.html", {"request": request, "settings": settings})

@app.get("/returns")
async def returns_page(request: Request):
    return templates.TemplateResponse("pages/returns.html", {"request": request, "settings": settings})

@app.get("/privacy")
async def privacy_page(request: Request):
    return templates.TemplateResponse("pages/privacy.html", {"request": request, "settings": settings})

@app.get("/terms")
async def terms_page(request: Request):
    return templates.TemplateResponse("pages/terms.html", {"request": request, "settings": settings})


# Admin SPA routes
@app.get("/admin", include_in_schema=False)
@app.get("/admin/{path:path}", include_in_schema=False)
async def admin_spa(path: str = ""):
    return FileResponse(Path("app/static/index.html"))

# 標籤和分類路由已移除

# API 根路徑
@app.get("/api")
async def api_root():
    return {
        "message": "歡迎使用 BlogCommerce API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康檢查
@app.get("/health")
async def health_check():
    return {"status": "ok", "app_name": settings.site_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 