from fastapi import FastAPI, Request, HTTPException, APIRouter
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
from app.utils.logger import app_logger, log_api_error, log_validation_error, LoggingMiddleware
from datetime import datetime
from typing import Optional
from app.services.markdown_service import markdown_service
from starlette.responses import RedirectResponse

# 引入所有路由模組
from app.routes import (
    auth, posts, products, orders, cart, newsletter, 
    admin, settings as settings_router, banners, discount_codes, 
    favorites, payment, shipping_tiers, view_tracking, errors
)

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
            "description": "用戶認證相關操作，包括登入、註冊、密碼管理等。"
        },
        {
            "name": "文章",
            "description": "部落格文章的 CRUD 操作，支援 Markdown 格式。"
        },
        {
            "name": "商品",
            "description": "電商商品管理，包括商品資訊、庫存、價格等。"
        },
        {
            "name": "購物車",
            "description": "購物車功能，支援商品加入、移除、數量調整等操作。"
        },
        {
            "name": "訂單",
            "description": "訂單管理系統，包括訂單創建、狀態更新、歷史記錄等。"
        },
        {
            "name": "收藏",
            "description": "用戶收藏功能，允許收藏商品並管理收藏清單。"
        },
        {
            "name": "系統設定",
            "description": "系統配置管理，包括網站設定、功能開關等。"
        },
        {
            "name": "金流處理",
            "description": "金流付款處理，支援多種付款方式。"
        },
        {
            "name": "瀏覽追蹤",
            "description": "網站瀏覽行為追蹤和統計。"
        },
        {
            "name": "電子報",
            "description": "電子報系統，包括訂閱管理、內容發送等功能。"
        },
        {
            "name": "管理員",
            "description": "管理員專用功能，需要管理員權限。"
        },
        {
            "name": "健康檢查",
            "description": "系統健康狀態檢查和監控。"
        },
        {
            "name": "折扣碼管理",
            "description": "折扣碼系統，包括建立、管理、驗證和使用統計等功能。"
        }
    ],
    servers=[
        {
            "url": "http://localhost:8002",
            "description": "開發環境伺服器"
        },
        {
            "url": "https://api.blogcommerce.com",
            "description": "正式環境伺服器"
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

# 輔助函數：生成帶有動態設定的模板回應
def render_template(template_name: str, request: Request, **kwargs):
    """渲染模板並自動載入動態設定"""
    dynamic_settings = get_public_settings()
    context = {"request": request, "settings": dynamic_settings}
    context.update(kwargs)
    return templates.TemplateResponse(template_name, context)

# --- API 路由掛載 ---
api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(posts.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(cart.router)
api_router.include_router(newsletter.router)
api_router.include_router(admin.router)
api_router.include_router(banners.router)
api_router.include_router(discount_codes.router)
api_router.include_router(favorites.router)
api_router.include_router(payment.router)
api_router.include_router(shipping_tiers.router)
api_router.include_router(view_tracking.router)
api_router.include_router(errors.router)

# 特殊處理 settings 路由
api_router.include_router(settings_router.router)
api_router.include_router(settings_router.admin_router)
api_router.include_router(settings_router.public_router)

app.include_router(api_router, prefix="/api")

# 全局異常處理器
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """處理HTTP異常"""
    log_api_error(f"{request.method} {request.url.path}", exc, {"status_code": exc.status_code})
    return await http_exception_handler(request, exc)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """處理驗證錯誤"""
    log_validation_error("Request", exc.errors(), None)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """處理一般異常 - 詳細診斷版本"""
    
    error_detail = {
        "exception_type": str(type(exc)),
        "exception_message": str(exc),
        "request_path": request.url.path,
        "request_method": request.method
    }
    
    app_logger.error(f"捕獲異常: {error_detail}")
    
    if any(keyword in str(type(exc)) for keyword in ['pydantic', 'ValidationError', 'serialization', 'JSONDecodeError', 'UnicodeDecodeError']):
        app_logger.error(f"重新拋出異常: {type(exc)}")
        raise exc
    
    if 'json' in str(exc).lower() or 'serialize' in str(exc).lower():
        app_logger.error(f"JSON相關異常，重新拋出: {exc}")
        raise exc
    
    log_api_error(f"{request.method} {request.url.path}", exc)
    
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

# --- 前端頁面路由 ---
@app.get("/")
async def index(request: Request):
    return render_template("index.html", request)

@app.get("/login")
async def login_page(request: Request):
    return render_template("auth/login.html", request)

@app.get("/register")
async def register_page(request: Request):
    return render_template("auth/register.html", request)

@app.get("/products")
async def products_page(request: Request):
    return render_template("shop/products.html", request)

@app.get("/product/{slug}")
async def product_detail_page(request: Request, slug: str):
    return render_template("shop/product_detail.html", request, slug=slug)

@app.get("/cart")
async def cart_page(request: Request):
    return render_template("shop/cart.html", request)

@app.get("/checkout")
async def checkout_page(request: Request, product_id: Optional[int] = None, quantity: Optional[int] = None):
    """結帳頁面 - 檢查購物車是否為空"""
    from app.database import get_db
    from app.models.product import Product
    from sqlalchemy.orm import Session
    
    if product_id and quantity:
        db: Session = next(get_db())
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.is_active.is_(True)
            ).first()
            
            if not product or product.stock_quantity < quantity:
                return RedirectResponse(url="/products", status_code=302)
            
            cart = request.session.get("cart", {})
            cart[str(product_id)] = quantity
            request.session["cart"] = cart
            
        except Exception as e:
            app_logger.error(f"立即購買驗證失敗: {e}")
            return RedirectResponse(url="/products", status_code=302)
        finally:
            db.close()
    
    cart = request.session.get("cart", {})
    if not cart:
        return RedirectResponse(url="/cart", status_code=302)
    
    return render_template("shop/checkout.html", request)

@app.get("/blog")
async def blog_page(request: Request):
    return render_template("blog/posts.html", request)

@app.get("/blog/{slug}")
async def post_detail_page(request: Request, slug: str):
    """文章詳細頁面 - 載入文章以確保SEO標籤正確設置"""
    from app.database import get_db
    from app.models.post import Post
    from sqlalchemy.orm import Session
    
    db: Session = next(get_db())
    post = None
    
    try:
        post = db.query(Post).filter(Post.slug == slug, Post.is_published == True).first()
    except Exception as e:
        app_logger.error(f"載入文章失敗: {e}")
    finally:
        db.close()
    
    return render_template("blog/post_detail.html", request, slug=slug, post=post)

@app.get("/profile")
async def profile_page(request: Request):
    return render_template("auth/profile.html", request)

@app.get("/orders")
async def orders_page(request: Request):
    return render_template("shop/orders.html", request)

@app.get("/favorites")
async def favorites_page(request: Request):
    return render_template("shop/favorites.html", request)

# Footer 頁面路由
@app.get("/about")
async def about_page(request: Request):
    return render_template("pages/about.html", request)

@app.get("/contact")
async def contact_page(request: Request):
    return render_template("pages/contact.html", request)

@app.get("/help")
async def help_page(request: Request):
    return render_template("pages/help.html", request)

@app.get("/returns")
async def returns_page(request: Request):
    return render_template("pages/returns.html", request)

@app.get("/privacy")
async def privacy_page(request: Request):
    return render_template("pages/privacy.html", request)

@app.get("/terms")
async def terms_page(request: Request):
    return render_template("pages/terms.html", request)


# Admin SPA: Mount the entire built frontend under /admin
# 修正: 這裡的路徑是關鍵
admin_spa_path = Path("admin") # 假設前端打包後放在專案根目錄的 'admin' 資料夾

if admin_spa_path.exists() and (admin_spa_path / "index.html").exists():
    # 修正: 掛載 assets 的路徑必須包含 /admin 前綴
    app.mount("/admin/assets", StaticFiles(directory=admin_spa_path / "assets"), name="admin-assets")
    
    @app.get("/admin/{path:path}", include_in_schema=False)
    async def admin_spa_catch_all(request: Request, path: str):
        """
        捕捉所有 /admin 下的路徑並回傳 index.html，讓 Vue Router 處理。
        """
        return FileResponse(admin_spa_path / "index.html")
else:
    @app.get("/admin/{path:path}", include_in_schema=False)
    async def admin_spa_placeholder(path: str = ""):
        return JSONResponse(
            status_code=404,
            content={"message": "Admin panel not built. Please run the build script."},
        )

# API 根路徑
@app.get("/api")
async def api_root():
    return {
        "message": "歡迎使用 BlogCommerce API",
        "docs": "/docs",
        "redoc": "/redoc",
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
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    return render_template("index.html", request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.debug
    )
