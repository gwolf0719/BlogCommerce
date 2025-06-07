from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.database import init_db
from app.routes import categories, posts, auth, products, orders, admin, cart, analytics, tags, favorites

# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.site_name,
    description=settings.site_description,
    version="1.0.0",
    debug=settings.debug
)

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
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 模板設定
templates = Jinja2Templates(directory="app/templates")

# 包含 API 路由
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(posts.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(cart.router)
app.include_router(analytics.router)
app.include_router(tags.router)
app.include_router(favorites.router)

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用程式啟動時初始化資料庫"""
    init_db()

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

# 管理員前端路由
@app.get("/admin/login")
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request, "settings": settings})

@app.get("/admin")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "settings": settings})

@app.get("/admin/users")
async def admin_users_page(request: Request):
    return templates.TemplateResponse("admin/users.html", {"request": request, "settings": settings})

@app.get("/admin/posts")
async def admin_posts_page(request: Request):
    return templates.TemplateResponse("admin/posts.html", {"request": request, "settings": settings})

@app.get("/admin/posts/create")
async def admin_post_create_page(request: Request):
    return templates.TemplateResponse("admin/post_form.html", {"request": request, "settings": settings})

@app.get("/admin/posts/{post_id}/edit")
async def admin_post_edit_page(request: Request, post_id: int):
    return templates.TemplateResponse("admin/post_form.html", {"request": request, "post_id": post_id, "settings": settings})

@app.get("/admin/products")
async def admin_products_page(request: Request):
    return templates.TemplateResponse("admin/products.html", {"request": request, "settings": settings})

@app.get("/admin/products/create")
async def admin_product_create_page(request: Request):
    return templates.TemplateResponse("admin/product_form.html", {"request": request, "settings": settings})

@app.get("/admin/products/{product_id}/edit")
async def admin_product_edit_page(request: Request, product_id: int):
    return templates.TemplateResponse("admin/product_form.html", {"request": request, "product_id": product_id, "settings": settings})

@app.get("/admin/orders")
async def admin_orders_page(request: Request):
    return templates.TemplateResponse("admin/orders.html", {"request": request, "settings": settings})

@app.get("/admin/categories")
async def admin_categories_page(request: Request):
    return templates.TemplateResponse("admin/categories.html", {"request": request, "settings": settings})

@app.get("/admin/settings")
async def admin_settings_page(request: Request):
    return templates.TemplateResponse("admin/settings.html", {"request": request, "settings": settings})

@app.get("/admin/analytics")
async def admin_analytics_page(request: Request):
    return templates.TemplateResponse("admin/analytics.html", {"request": request, "settings": settings})

# 標籤相關路由
@app.get("/tags")
async def tags_page(request: Request):
    return templates.TemplateResponse("tags/index.html", {"request": request, "settings": settings})

@app.get("/tags/{tag_slug}/posts")
async def tag_posts_page(request: Request, tag_slug: str):
    return templates.TemplateResponse("tags/posts.html", {"request": request, "tag_slug": tag_slug, "settings": settings})

@app.get("/tags/{tag_slug}/products")
async def tag_products_page(request: Request, tag_slug: str):
    return templates.TemplateResponse("tags/products.html", {"request": request, "tag_slug": tag_slug, "settings": settings})

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