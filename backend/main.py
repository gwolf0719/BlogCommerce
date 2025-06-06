from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn

from database import settings, create_tables
from api import auth, posts, products, orders, admin
from models import models

# 建立 FastAPI 應用
app = FastAPI(
    title=settings.app_name,
    description="一個現代化的部落格電商系統框架",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立上傳目錄
os.makedirs(settings.upload_dir, exist_ok=True)

# 靜態檔案服務
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# API 路由
app.include_router(auth.router, prefix=settings.api_v1_prefix + "/auth", tags=["認證"])
app.include_router(posts.router, prefix=settings.api_v1_prefix + "/posts", tags=["文章"])
app.include_router(products.router, prefix=settings.api_v1_prefix + "/products", tags=["商品"])
app.include_router(orders.router, prefix=settings.api_v1_prefix + "/orders", tags=["訂單"])
app.include_router(admin.router, prefix=settings.api_v1_prefix + "/admin", tags=["管理後台"])

@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    # 建立資料表
    create_tables()
    print(f"🚀 {settings.app_name} v{settings.app_version} 啟動成功!")
    print(f"📊 資料庫類型: {settings.database_type}")
    print(f"🌍 API 網址: {settings.api_v1_prefix}")
    if settings.debug:
        print(f"📖 API 文件: /docs")

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": f"歡迎使用 {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "文件已在生產環境中關閉",
        "api": settings.api_v1_prefix
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": settings.database_type
    }

@app.get("/sitemap.xml")
async def sitemap():
    """SEO: 網站地圖"""
    # TODO: 實作動態 sitemap 生成
    return {"message": "Sitemap generation will be implemented"}

@app.get("/robots.txt")
async def robots():
    """SEO: robots.txt"""
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: {settings.api_v1_prefix}/

Sitemap: {settings.site_url}/sitemap.xml
"""
    return content

# 錯誤處理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"detail": "找不到請求的資源"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"detail": "伺服器內部錯誤"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    ) 