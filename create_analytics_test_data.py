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
from sqlalchemy.sql import func

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
        
        # 生成基礎數據
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0"
        ]
        
        device_types = ["Desktop", "Mobile", "Tablet"]
        browsers = ["Chrome", "Safari", "Firefox", "Edge"]
        oses = ["Windows", "macOS", "iOS", "Android"]
        
        # 生成過去30天的流量數據
        print("生成頁面瀏覽記錄...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        session_counter = 1
        page_view_counter = 1
        
        # 每天生成20-50個瀏覽量
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            daily_views = random.randint(20, 50)
            
            for view in range(daily_views):
                # 隨機時間
                view_time = current_date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # 創建頁面瀏覽記錄
                create_page_view(
                    db, view_time, posts, products, user_agents, 
                    device_types, browsers, oses, session_counter, page_view_counter
                )
                
                session_counter += 1
                page_view_counter += 1
        
        # 提交基礎數據
        db.commit()
        print(f"生成了 {db.query(PageView).count()} 個頁面瀏覽記錄")
        
        # 生成熱門內容統計
        print("生成熱門內容統計...")
        
        # 處理文章
        blog_content_stats = db.query(
            PageView.content_id,
            func.count(PageView.id).label('views')
        ).filter(
            PageView.page_type == 'blog',
            PageView.content_id.isnot(None)
        ).group_by(PageView.content_id).all()
        
        print(f"找到 {len(blog_content_stats)} 個部落格內容統計")
        
        for stat in blog_content_stats:
            post = db.query(Post).filter(Post.id == stat.content_id).first()
            if post:
                try:
                    popular = PopularContent(
                        content_type='post',
                        content_id=post.id,
                        content_title=post.title,
                        content_url=f'/blog/{post.slug}',
                        total_views=stat.views,
                        unique_views=max(1, int(stat.views * 0.8)),
                        today_views=random.randint(0, min(5, stat.views))
                    )
                    db.add(popular)
                    print(f"添加部落格內容統計: {post.title} ({stat.views} 次瀏覽)")
                except Exception as e:
                    print(f"添加部落格內容統計失敗: {e}")

        # 處理商品
        product_content_stats = db.query(
            PageView.content_id,
            func.count(PageView.id).label('views')
        ).filter(
            PageView.page_type == 'product',
            PageView.content_id.isnot(None)
        ).group_by(PageView.content_id).all()
        
        print(f"找到 {len(product_content_stats)} 個商品內容統計")
        
        for stat in product_content_stats:
            product = db.query(Product).filter(Product.id == stat.content_id).first()
            if product:
                try:
                    popular = PopularContent(
                        content_type='product',
                        content_id=product.id,
                        content_title=product.name,
                        content_url=f'/product/{product.slug}',
                        total_views=stat.views,
                        unique_views=max(1, int(stat.views * 0.8)),
                        today_views=random.randint(0, min(5, stat.views))
                    )
                    db.add(popular)
                    print(f"添加商品內容統計: {product.name} ({stat.views} 次瀏覽)")
                except Exception as e:
                    print(f"添加商品內容統計失敗: {e}")
        
        try:
            db.commit()
            print("成功提交PopularContent數據")
        except Exception as e:
            print(f"提交PopularContent數據失敗: {e}")
            db.rollback()
        
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