#!/usr/bin/env python3
"""
生成測試流量分析數據
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random
from app.database import get_db
from app.models.analytics import PageView, UserSession, PopularContent
from app.models.post import Post
from app.models.product import Product

def generate_analytics_test_data():
    """生成測試流量數據"""
    db = next(get_db())
    
    try:
        print("🔄 正在生成測試流量數據...")
        
        # 清理現有數據
        print("清理現有流量數據...")
        db.query(PageView).delete()
        db.query(UserSession).delete()
        db.query(PopularContent).delete()
        
        # 獲取現有內容
        posts = db.query(Post).all()
        products = db.query(Product).all()
        
        print(f"找到 {len(posts)} 篇文章，{len(products)} 個商品")
        
        # 生成過去30天的數據
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36"
        ]
        
        device_types = ["desktop", "mobile", "tablet"]
        browsers = ["Chrome 91.0", "Safari 14.0", "Firefox 89.0", "Edge 91.0"]
        oses = ["Windows 10", "macOS 11.4", "iOS 14.6", "Android 11"]
        
        session_counter = 0
        page_view_counter = 0
        
        # 為每一天生成數據
        current_date = start_date
        while current_date <= end_date:
            # 每天生成 5-50 個瀏覽量
            daily_views = random.randint(5, 50)
            
            # 週末減少瀏覽量
            if current_date.weekday() >= 5:
                daily_views = int(daily_views * 0.7)
            
            # 最近幾天增加瀏覽量
            days_ago = (end_date - current_date).days
            if days_ago <= 3:
                daily_views = int(daily_views * 1.5)
            
            # 為今天生成分時數據
            if current_date.date() == end_date.date():
                for hour in range(24):
                    hour_views = random.randint(0, 5)
                    if 9 <= hour <= 17:  # 上班時間增加流量
                        hour_views = random.randint(2, 8)
                    
                    for _ in range(hour_views):
                        create_page_view(
                            db, current_date.replace(hour=hour, minute=random.randint(0, 59)),
                            posts, products, user_agents, device_types, browsers, oses,
                            session_counter, page_view_counter
                        )
                        session_counter += 1
                        page_view_counter += 1
            else:
                # 為其他天生成數據
                for _ in range(daily_views):
                    # 隨機時間
                    random_hour = random.randint(0, 23)
                    random_minute = random.randint(0, 59)
                    view_time = current_date.replace(hour=random_hour, minute=random_minute)
                    
                    create_page_view(
                        db, view_time, posts, products, user_agents, device_types, 
                        browsers, oses, session_counter, page_view_counter
                    )
                    session_counter += 1
                    page_view_counter += 1
            
            current_date += timedelta(days=1)
        
        # 生成熱門內容統計
        print("生成熱門內容統計...")
        for post in posts:
            views = db.query(PageView).filter(
                PageView.content_id == post.id,
                PageView.page_type == 'blog'
            ).count()
            
            if views > 0:
                popular = PopularContent(
                    content_type='blog',
                    content_id=post.id,
                    content_title=post.title,
                    content_url=f'/blog/{post.slug}',
                    total_views=views,
                    unique_views=max(1, int(views * 0.8)),
                    today_views=random.randint(0, min(5, views))
                )
                db.add(popular)
        
        for product in products:
            views = db.query(PageView).filter(
                PageView.content_id == product.id,
                PageView.page_type == 'product'
            ).count()
            
            if views > 0:
                popular = PopularContent(
                    content_type='product',
                    content_id=product.id,
                    content_title=product.name,
                    content_url=f'/product/{product.slug}',
                    total_views=views,
                    unique_views=max(1, int(views * 0.8)),
                    today_views=random.randint(0, min(5, views))
                )
                db.add(popular)
        
        db.commit()
        
        # 統計生成的數據
        total_page_views = db.query(PageView).count()
        total_sessions = db.query(UserSession).count()
        total_popular = db.query(PopularContent).count()
        
        print(f"✅ 測試數據生成完成！")
        print(f"   - 頁面瀏覽量: {total_page_views}")
        print(f"   - 用戶會話: {total_sessions}")
        print(f"   - 熱門內容: {total_popular}")
        
    except Exception as e:
        print(f"❌ 生成測試數據失敗: {e}")
        db.rollback()
    finally:
        db.close()

def create_page_view(db, view_time, posts, products, user_agents, device_types, browsers, oses, session_counter, page_view_counter):
    """創建單個頁面瀏覽記錄"""
    
    # 隨機選擇內容類型
    content_type = random.choice(['blog', 'product', 'home', 'category'])
    content_id = None
    page_url = "/"
    
    if content_type == 'blog' and posts:
        post = random.choice(posts)
        content_id = post.id
        page_url = f"/blog/{post.slug}"
    elif content_type == 'product' and products:
        product = random.choice(products)
        content_id = product.id
        page_url = f"/product/{product.slug}"
    elif content_type == 'home':
        page_url = "/"
        content_type = 'home'
    else:
        page_url = "/products"
        content_type = 'product_list'
    
    # 生成隨機IP
    ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    # 隨機選擇設備信息
    user_agent = random.choice(user_agents)
    device_type = random.choice(device_types)
    browser = random.choice(browsers)
    os = random.choice(oses)
    
    session_id = f"session_{session_counter}"
    
    # 創建會話
    session = UserSession(
        session_id=session_id,
        visitor_ip=ip,
        user_agent=user_agent,
        device_type=device_type,
        browser=browser,
        os=os,
        created_at=view_time,
        last_activity=view_time,
        page_views=1,
        is_bounce=random.choice([True, False])
    )
    db.add(session)
    
    # 創建頁面瀏覽
    page_view = PageView(
        page_url=page_url,
        page_type=content_type,
        content_id=content_id,
        visitor_ip=ip,
        user_agent=user_agent,
        device_type=device_type,
        browser=browser,
        os=os,
        session_id=session_id,
        created_at=view_time
    )
    db.add(page_view)

if __name__ == "__main__":
    generate_analytics_test_data() 