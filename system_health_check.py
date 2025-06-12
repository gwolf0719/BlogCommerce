#!/usr/bin/env python3
"""
系統健康檢查腳本
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.post import Post
from app.utils.logger import app_logger

BASE_URL = "http://127.0.0.1:8000"

def check_database():
    """檢查資料庫連接和數據"""
    try:
        db = SessionLocal()
        
        # 檢查表格存在和基本數據
        users_count = db.query(User).count()
        products_count = db.query(Product).count()
        orders_count = db.query(Order).count()
        posts_count = db.query(Post).count()
        
        db.close()
        
        return {
            "status": "✅ 正常",
            "users": users_count,
            "products": products_count,
            "orders": orders_count,
            "posts": posts_count
        }
    except Exception as e:
        return {"status": f"❌ 錯誤: {e}"}

def check_api_endpoint(endpoint, method="GET", data=None, auth_token=None):
    """檢查API端點"""
    try:
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=10)
        
        return {
            "status": f"✅ {response.status_code}",
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        return {"status": f"❌ 錯誤: {e}"}

def get_admin_token():
    """取得管理員JWT Token"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        }, timeout=10)
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            return None
    except:
        return None

def main():
    """主要檢查流程"""
    print("🔍 系統健康檢查")
    print("=" * 50)
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 資料庫檢查
    print("📊 資料庫狀態:")
    db_status = check_database()
    print(f"   狀態: {db_status['status']}")
    if "users" in db_status:
        print(f"   用戶數: {db_status['users']}")
        print(f"   商品數: {db_status['products']}")
        print(f"   訂單數: {db_status['orders']}")
        print(f"   文章數: {db_status['posts']}")
    print()
    
    # 2. 服務器健康檢查
    print("🏥 服務器健康:")
    health = check_api_endpoint("/health")
    print(f"   狀態: {health['status']}")
    if "response_time" in health:
        print(f"   響應時間: {health['response_time']:.3f}s")
    print()
    
    # 3. 管理員登入檢查
    print("🔐 管理員認證:")
    admin_token = get_admin_token()
    if admin_token:
        print("   狀態: ✅ 登入成功")
        print(f"   Token: {admin_token[:20]}...")
    else:
        print("   狀態: ❌ 登入失敗")
    print()
    
    # 4. API端點檢查
    print("🔗 API端點檢查:")
    
    endpoints = [
        ("/api", "GET", "API根路徑"),
        ("/api/categories/", "GET", "分類列表"),
        ("/api/products/", "GET", "商品列表"),
        ("/api/posts/", "GET", "文章列表"),
    ]
    
    for endpoint, method, description in endpoints:
        result = check_api_endpoint(endpoint, method)
        print(f"   {description}: {result['status']}")
        if "response_time" in result:
            print(f"      響應時間: {result['response_time']:.3f}s")
    
    # 5. 管理員API檢查
    if admin_token:
        print("\n🛠️  管理員API檢查:")
        admin_endpoints = [
            ("/api/admin/stats", "GET", "管理員統計"),
            ("/api/admin/users", "GET", "用戶管理"),
            ("/api/admin/products", "GET", "商品管理"),
        ]
        
        for endpoint, method, description in admin_endpoints:
            result = check_api_endpoint(endpoint, method, auth_token=admin_token)
            print(f"   {description}: {result['status']}")
            if "response_time" in result:
                print(f"      響應時間: {result['response_time']:.3f}s")
    
    # 6. 前端頁面檢查
    print("\n🌐 前端頁面檢查:")
    frontend_pages = [
        ("/", "首頁"),
        ("/products", "商品頁面"),
        ("/blog", "部落格頁面"),
        ("/admin", "管理員前端"),
    ]
    
    for page, description in frontend_pages:
        result = check_api_endpoint(page)
        print(f"   {description}: {result['status']}")
        if "response_time" in result:
            print(f"      響應時間: {result['response_time']:.3f}s")
    
    print("\n" + "=" * 50)
    print("✅ 健康檢查完成")
    
    # 生成日誌報告
    app_logger.info("系統健康檢查完成")
    
if __name__ == "__main__":
    main() 