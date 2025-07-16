import os
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
    description="BlogCommerce API 文檔",
    version="1.0.0",
    debug=settings.debug,
    # 在生產環境中，後台的 docs 路徑會衝突，所以動態調整
    docs_url="/api/docs" if os.getenv("APP_ENV") == "production" else "/docs",
    redoc_url="/api/redoc" if os.getenv("APP_ENV") == "production" else "/redoc",
)

# --- 中介軟體設定 ---
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"] if os.getenv("APP_ENV") == "development" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 靜態檔案與模板 ---
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
templates = Jinja2Templates(directory="app/templates")

def render_template(template_name: str, request: Request, **kwargs):
    dynamic_settings = get_public_settings()
    context = {"request": request, "settings": dynamic_settings, **kwargs}
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
api_router.include_router(settings_router.router)
api_router.include_router(settings_router.admin_router)
api_router.include_router(settings_router.public_router)
app.include_router(api_router, prefix="/api")

# --- 生產模式下掛載 Admin 後台 (SPA 處理) ---
if os.getenv("APP_ENV") == "production":
    admin_dist_path = Path("admin-src/dist")
    # 確保建置目錄存在
    if admin_dist_path.is_dir():
        # 1. 將 assets 目錄掛載到 /admin/assets
        assets_path = admin_dist_path / "assets"
        if assets_path.is_dir():
            app.mount("/admin/assets", StaticFiles(directory=assets_path), name="admin-assets")

        # 2. 建立一個 catch-all 路由來服務 index.html
        @app.get("/admin/{path:path}", include_in_schema=False)
        async def serve_admin_spa(request: Request, path: str):
            index_path = admin_dist_path / "index.html"
            if index_path.is_file():
                return FileResponse(index_path)
            # 如果連 index.html 都找不到，返回一個錯誤
            return JSONResponse(
                status_code=404,
                content={"message": "Admin panel index.html not found."},
            )
        
        # 3. 處理根路徑 /admin 或 /admin/
        @app.get("/admin", include_in_schema=False)
        @app.get("/admin/", include_in_schema=False)
        async def serve_admin_root(request: Request):
            index_path = admin_dist_path / "index.html"
            if index_path.is_file():
                return FileResponse(index_path)
            return JSONResponse(
                status_code=404,
                content={"message": "Admin panel index.html not found."},
            )


# --- 前端頁面路由 ---
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return render_template("index.html", request)

@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return render_template("auth/login.html", request)

@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return render_template("auth/register.html", request)

@app.get("/products", include_in_schema=False)
async def products_page(request: Request):
    return render_template("shop/products.html", request)

@app.get("/product/{slug}", include_in_schema=False)
async def product_detail_page(request: Request, slug: str):
    return render_template("shop/product_detail.html", request, slug=slug)

@app.get("/cart", include_in_schema=False)
async def cart_page(request: Request):
    return render_template("shop/cart.html", request)

@app.get("/checkout", include_in_schema=False)
async def checkout_page(request: Request, product_id: Optional[int] = None, quantity: Optional[int] = None):
    from app.database import get_db
    from app.models.product import Product
    from sqlalchemy.orm import Session
    
    if product_id and quantity:
        db: Session = next(get_db())
        try:
            product = db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first()
            if not product or product.stock_quantity < quantity:
                return RedirectResponse(url="/products", status_code=302)
            cart = request.session.get("cart", {})
            cart[str(product_id)] = quantity
            request.session["cart"] = cart
        finally:
            db.close()
    
    if not request.session.get("cart", {}):
        return RedirectResponse(url="/cart", status_code=302)
    
    return render_template("shop/checkout.html", request)

@app.get("/blog", include_in_schema=False)
async def blog_page(request: Request):
    return render_template("blog/posts.html", request)

@app.get("/blog/{slug}", include_in_schema=False)
async def post_detail_page(request: Request, slug: str):
    from app.database import get_db
    from app.models.post import Post
    from sqlalchemy.orm import Session
    db: Session = next(get_db())
    post = db.query(Post).filter(Post.slug == slug, Post.is_published == True).first()
    db.close()
    return render_template("blog/post_detail.html", request, slug=slug, post=post)

@app.get("/profile", include_in_schema=False)
async def profile_page(request: Request):
    return render_template("auth/profile.html", request)

@app.get("/orders", include_in_schema=False)
async def orders_page(request: Request):
    return render_template("shop/orders.html", request)

@app.get("/favorites", include_in_schema=False)
async def favorites_page(request: Request):
    return render_template("shop/favorites.html", request)

# --- Footer 頁面路由 ---
@app.get("/about", include_in_schema=False)
async def about_page(request: Request):
    return render_template("pages/about.html", request)

@app.get("/contact", include_in_schema=False)
async def contact_page(request: Request):
    return render_template("pages/contact.html", request)

@app.get("/help", include_in_schema=False)
async def help_page(request: Request):
    return render_template("pages/help.html", request)

@app.get("/returns", include_in_schema=False)
async def returns_page(request: Request):
    return render_template("pages/returns.html", request)

@app.get("/privacy", include_in_schema=False)
async def privacy_page(request: Request):
    return render_template("pages/privacy.html", request)

@app.get("/terms", include_in_schema=False)
async def terms_page(request: Request):
    return render_template("pages/terms.html", request)

# --- 應用程式事件 ---
@app.on_event("startup")
async def startup_event():
    app_logger.info("應用程式正在啟動...")
    init_db()
    app_logger.info("資料庫初始化完成")
    app_logger.info(f"應用程式已啟動，運行在 {os.getenv('APP_ENV', 'undefined')} 模式")

# --- 全局異常處理器 ---
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    log_api_error(f"{request.method} {request.url.path}", exc, {"status_code": exc.status_code})
    return await http_exception_handler(request, exc)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    log_validation_error("Request", exc.errors(), None)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    log_api_error(f"{request.method} {request.url.path}", exc)
    return JSONResponse(status_code=500, content={"detail": "內部服務器錯誤"})

# --- Catch-all 路由必須在最後 ---
@app.get("/{path:path}", include_in_schema=False)
async def catch_all_public(request: Request, path: str):
    # 這個 catch-all 不應該捕捉到 /admin 或 /api 的路徑，因為它們已經被前面的路由處理了
    # 如果有需要，可以返回一個自訂的 404 頁面
    return render_template("index.html", request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.debug
    )
