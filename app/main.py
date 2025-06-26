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
from datetime import datetime

# 建立 FastAPI 應用程式
app = FastAPI(
    title="BlogCommerce API",
    description="""
    # BlogCommerce API 文檔
    
    ## 簡介
    BlogCommerce 是一個功能完整的電商部落格系統，集成了內容管理、電商功能、用戶管理和分析統計等模組。
    
    ## 主要功能
    
    ### 🔐 認證與用戶系統
    - 用戶註冊、登入、密碼管理
    - JWT Token 認證
    - 用戶資料管理
    
    ### 📝 內容管理系統
    - 文章 CRUD 操作
    - Markdown 支援
    - SEO 友好的 URL
    
    ### 🛒 電商系統
    - 商品管理
    - 購物車功能
    - 訂單處理
    - 收藏功能
    
    ### 📊 分析統計
    - 頁面瀏覽統計
    - 用戶行為分析
    - 即時數據追蹤
    
    ### 🔧 系統管理
    - 系統設定管理
    - 錯誤日誌記錄
    - 電子報系統
    
    ## 認證方式
    
    大部分 API 端點需要 JWT Token 認證：
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    
    ## 狀態碼說明
    
    - `200` - 請求成功
    - `201` - 資源創建成功
    - `400` - 請求參數錯誤
    - `401` - 未授權（需要登入）
    - `403` - 權限不足
    - `404` - 資源不存在
    - `422` - 資料驗證失敗
    - `500` - 服務器內部錯誤
    
    ## 開發者資訊
    
    - 版本: 1.0.0
    - 開發環境: FastAPI + SQLAlchemy + Vue.js
    - 文檔更新: 自動生成（基於代碼註解）
    """,
    version="1.0.0",
    terms_of_service="/terms",
    contact={
        "name": "BlogCommerce 開發團隊",
        "url": "https://blogcommerce.com/contact",
        "email": "admin@blogcommerce.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    debug=settings.debug,
    openapi_tags=[
        {
            "name": "認證",
            "description": "用戶認證相關操作，包括登入、註冊、密碼管理等。",
        },
        {
            "name": "文章",
            "description": "部落格文章的 CRUD 操作，支援 Markdown 格式。",
        },
        {
            "name": "商品",
            "description": "電商商品管理，包括商品資訊、庫存、價格等。",
        },
        {
            "name": "購物車",
            "description": "購物車功能，支援商品加入、移除、數量調整等操作。",
        },
        {
            "name": "訂單",
            "description": "訂單管理系統，包括訂單創建、狀態更新、歷史記錄等。",
        },
        {
            "name": "收藏",
            "description": "用戶收藏功能，允許收藏商品並管理收藏清單。",
        },
        {
            "name": "分析統計",
            "description": "網站分析統計，包括頁面瀏覽、用戶行為、即時數據等。",
        },
        {
            "name": "系統設定",
            "description": "系統配置管理，包括網站設定、功能開關等。",
        },
        {
            "name": "錯誤日誌",
            "description": "系統錯誤日誌記錄與查詢功能。",
        },
        {
            "name": "電子報",
            "description": "電子報系統，包括訂閱管理、內容發送等功能。",
        },
        {
            "name": "管理員",
            "description": "管理員專用功能，需要管理員權限。",
        },
        {
            "name": "健康檢查",
            "description": "系統健康狀態檢查和監控。",
        }
    ]
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


# Admin SPA: Mount the entire built frontend under /admin
admin_spa_path = Path("app/static")

if admin_spa_path.exists() and (admin_spa_path / "index.html").exists():
    # Mount assets directory for static files
    app.mount("/assets", StaticFiles(directory=admin_spa_path / "assets"), name="assets")
    
    @app.get("/admin", include_in_schema=False)
    async def admin_spa_root(request: Request):
        """Serve the admin SPA root"""
        return FileResponse(admin_spa_path / "index.html")
    
    @app.get("/admin/{path:path}", include_in_schema=False)
    async def admin_spa_catch_all(request: Request, path: str):
        """
        Catches all paths under /admin and serves the index.html.
        This is necessary for single-page applications (SPAs) where routing is handled client-side.
        """
        return FileResponse(admin_spa_path / "index.html")
else:
    @app.get("/admin", include_in_schema=False)
    @app.get("/admin/{path:path}", include_in_schema=False)
    async def admin_spa_placeholder(path: str = ""):
        return JSONResponse(
            status_code=404,
            content={"message": "Admin panel not built. Please run the build script."},
        )

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
@app.get("/health", tags=["健康檢查"])
async def health_check():
    """檢查應用程式健康狀態"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 增強版 ReDoc 文檔
@app.get("/api-docs", include_in_schema=False)
async def enhanced_redoc():
    """提供增強版的 ReDoc API 文檔，包含測試功能"""
    return FileResponse("app/static/enhanced-redoc.html")

# 404 處理
@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str, request: Request):
    """捕捉所有其他路由，返回前端頁面"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    ) 