#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置數據庫並建立包含圖片的全新測試數據

測試資料規格：
- 10 個部落格圖文（2 個分類）
- 30 個商品（4 個分類）
- 8 個會員
- 20 張訂單
- 所有文章和商品都有對應圖片
"""

import os
import sys
import random
import requests
import urllib.parse
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from faker import Faker
from decimal import Decimal
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import (
    User, Category, Post, Product, Order, OrderItem, 
    PageView, NewsletterSubscriber, Favorite, Tag, UserRole, CategoryType, OrderStatus
)
from app.auth import get_password_hash
from app.config import settings

# 初始化 Faker
fake = Faker('zh_TW')

def ensure_image_directories():
    """確保圖片目錄存在"""
    dirs = [
        "app/static/images/blog",
        "app/static/images/products",
        "app/static/images/categories"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 圖片目錄已建立: {dir_path}")

def download_image(url, filepath):
    """下載圖片到指定路徑"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"❌ 下載圖片失敗 {url}: {e}")
        return False

def generate_blog_images():
    """生成部落格文章圖片"""
    print("🖼️  正在生成部落格圖片...")
    
    # 科技主題圖片
    tech_keywords = [
        "artificial intelligence",
        "5G technology",
        "blockchain",
        "cloud computing",
        "quantum computing"
    ]
    
    # 生活主題圖片
    lifestyle_keywords = [
        "remote work",
        "home fitness",
        "home office",
        "digital minimalism",
        "sustainable living"
    ]
    
    blog_images = []
    
    # 為每個主題生成圖片
    for i, keyword in enumerate(tech_keywords):
        filename = f"tech-{i+1}.jpg"
        filepath = f"app/static/images/blog/{filename}"
        
        # 使用 Unsplash API 獲取圖片
        query = urllib.parse.quote(keyword)
        url = f"https://source.unsplash.com/800x600/?{query}"
        
        if download_image(url, filepath):
            blog_images.append(f"/static/images/blog/{filename}")
            print(f"✅ 科技圖片已下載: {filename}")
        else:
            blog_images.append("/static/images/default-blog.jpg")
    
    for i, keyword in enumerate(lifestyle_keywords):
        filename = f"lifestyle-{i+1}.jpg"
        filepath = f"app/static/images/blog/{filename}"
        
        query = urllib.parse.quote(keyword)
        url = f"https://source.unsplash.com/800x600/?{query}"
        
        if download_image(url, filepath):
            blog_images.append(f"/static/images/blog/{filename}")
            print(f"✅ 生活圖片已下載: {filename}")
        else:
            blog_images.append("/static/images/default-blog.jpg")
    
    return blog_images

def generate_product_images():
    """生成商品圖片"""
    print("🛍️  正在生成商品圖片...")
    
    # 商品關鍵字
    product_keywords = {
        "digital": [
            "iphone", "macbook", "ipad", "airpods", "apple watch", 
            "dell laptop", "samsung phone", "nintendo switch"
        ],
        "home": [
            "dyson vacuum", "air fryer", "dining table", "storage box",
            "robot vacuum", "bed sheets", "water filter", "rice cooker"
        ],
        "sports": [
            "running shoes", "sports shirt", "yoga pants", "yoga mat",
            "dumbbell", "exercise ball", "jump rope"
        ],
        "beauty": [
            "skincare", "foundation", "eye cream", "cleanser",
            "lipstick", "sunscreen", "cleansing oil"
        ]
    }
    
    product_images = {}
    
    for category, keywords in product_keywords.items():
        product_images[category] = []
        
        for i, keyword in enumerate(keywords):
            filename = f"{category}-{i+1}.jpg"
            filepath = f"app/static/images/products/{filename}"
            
            query = urllib.parse.quote(keyword)
            url = f"https://source.unsplash.com/600x600/?{query}"
            
            if download_image(url, filepath):
                product_images[category].append(f"/static/images/products/{filename}")
                print(f"✅ 商品圖片已下載: {filename}")
            else:
                product_images[category].append("/static/images/default-product.jpg")
    
    return product_images

def drop_all_tables():
    """刪除所有資料表"""
    print("🗑️  正在清除所有現有數據...")
    Base.metadata.drop_all(bind=engine)
    print("✅ 所有資料表已清除")

def create_all_tables():
    """建立所有資料表"""
    print("📊 正在建立資料表結構...")
    Base.metadata.create_all(bind=engine)
    print("✅ 資料表結構已建立")

def create_admin_user(db: Session):
    """建立管理員帳號"""
    print("👑 正在建立管理員帳號...")
    
    admin = User(
        username=settings.admin_username,
        email=settings.admin_email,
        full_name=settings.admin_full_name,
        hashed_password=get_password_hash(settings.admin_password),
        is_active=True,
        role=UserRole.ADMIN
    )
    
    db.add(admin)
    db.commit()
    print(f"✅ 管理員帳號已建立: {settings.admin_username}")
    return admin

def create_blog_categories(db: Session):
    """建立部落格分類（2個）"""
    print("📂 正在建立部落格分類...")
    
    blog_categories = [
        {
            "name": "科技趨勢",
            "description": "最新的科技資訊和趨勢分析",
            "slug": "tech-trends"
        },
        {
            "name": "生活分享",
            "description": "日常生活經驗和心得分享",
            "slug": "lifestyle"
        }
    ]
    
    categories = []
    for cat_data in blog_categories:
        category = Category(
            name=cat_data["name"],
            description=cat_data["description"],
            slug=cat_data["slug"],
            type=CategoryType.BLOG
        )
        db.add(category)
        categories.append(category)
    
    db.commit()
    print(f"✅ 已建立 {len(categories)} 個部落格分類")
    return categories

def create_product_categories(db: Session):
    """建立商品分類（4個）"""
    print("🛍️  正在建立商品分類...")
    
    product_categories = [
        {
            "name": "3C數位",
            "description": "電腦、手機、平板等數位產品",
            "slug": "digital"
        },
        {
            "name": "居家生活",
            "description": "家居用品、生活必需品",
            "slug": "home-living"
        },
        {
            "name": "運動健身",
            "description": "運動器材、健身用品",
            "slug": "sports-fitness"
        },
        {
            "name": "美妝保養",
            "description": "化妝品、保養品、個人護理",
            "slug": "beauty-care"
        }
    ]
    
    categories = []
    for cat_data in product_categories:
        category = Category(
            name=cat_data["name"],
            description=cat_data["description"],
            slug=cat_data["slug"],
            type=CategoryType.PRODUCT
        )
        db.add(category)
        categories.append(category)
    
    db.commit()
    print(f"✅ 已建立 {len(categories)} 個商品分類")
    return categories

def create_users(db: Session):
    """建立會員（8個）"""
    print("👥 正在建立會員帳號...")
    
    users = []
    for i in range(8):
        user = User(
            username=f"user{i+1:02d}",
            email=fake.email(),
            full_name=fake.name(),
            hashed_password=get_password_hash("password123"),
            is_active=True,
            role=UserRole.USER,
            phone=fake.phone_number(),
            address=fake.address()
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ 已建立 {len(users)} 個會員帳號")
    return users

def create_blog_posts(db: Session, categories, admin_user, blog_images):
    """建立部落格文章（10篇）包含圖片"""
    print("📝 正在建立部落格文章...")
    
    # 科技趨勢文章（5篇）
    tech_posts = [
        {
            "title": "2024年人工智慧發展趨勢",
            "content": """
# 2024年人工智慧發展趨勢

![AI技術發展](blog_images[0])

人工智慧在2024年持續快速發展，以下是主要趨勢：

## 1. 生成式AI的普及
ChatGPT、Claude等大型語言模型已經改變了我們的工作方式。

## 2. AI與日常生活的深度整合
從智慧家居到自動駕駛，AI正在改變我們的生活。

## 3. 企業AI應用的爆發
越來越多企業開始導入AI技術來提升效率。

## 結論
AI技術的發展將持續加速，我們需要持續學習適應這個變化。
            """,
            "summary": "探討2024年AI發展的主要趨勢和應用場景",
            "image": blog_images[0] if len(blog_images) > 0 else "/static/images/default-blog.jpg"
        },
        {
            "title": "5G技術如何改變我們的連接方式",
            "content": """
# 5G技術如何改變我們的連接方式

![5G技術](blog_images[1])

5G技術的普及正在重新定義我們的連接體驗。

## 超高速傳輸
- 下載速度可達1Gbps以上
- 延遲降至1毫秒以下

## 物聯網革命
5G讓更多設備能夠同時連接，推動智慧城市發展。

## 新興應用
- 擴增實境(AR)
- 虛擬實境(VR)
- 遠程手術
- 自動駕駛

## 展望未來
5G將成為數位轉型的重要基礎設施。
            """,
            "summary": "分析5G技術對各行業的影響和未來發展",
            "image": blog_images[1] if len(blog_images) > 1 else "/static/images/default-blog.jpg"
        },
        {
            "title": "區塊鏈技術在金融業的應用",
            "content": """
# 區塊鏈技術在金融業的應用

![區塊鏈技術](blog_images[2])

區塊鏈技術正在革新傳統金融服務。

## 主要應用領域

### 1. 數位貨幣
比特幣、以太坊等加密貨幣的興起。

### 2. 智能合約
自動執行的合約，減少中介成本。

### 3. 供應鏈金融
提高透明度和可追溯性。

## 挑戰與機會
- 監管政策的完善
- 技術標準的統一
- 能耗問題的解決

區塊鏈將重塑金融業的未來。
            """,
            "summary": "探討區塊鏈在金融領域的創新應用",
            "image": blog_images[2] if len(blog_images) > 2 else "/static/images/default-blog.jpg"
        },
        {
            "title": "雲端運算的新發展趨勢",
            "content": """
# 雲端運算的新發展趨勢

![雲端運算](blog_images[3])

雲端技術持續演進，帶來新的可能性。

## 多雲策略
企業開始採用多個雲端服務提供商的策略。

## 邊緣運算
- 降低延遲
- 提高安全性
- 減少頻寬需求

## 無伺服器架構
Functions as a Service (FaaS) 讓開發更簡單。

## 綠色雲端
雲端服務商開始重視環保和節能。

## 未來展望
雲端運算將變得更智慧、更綠色、更安全。
            """,
            "summary": "介紹雲端運算的最新發展和未來趨勢",
            "image": blog_images[3] if len(blog_images) > 3 else "/static/images/default-blog.jpg"
        },
        {
            "title": "量子運算的突破與挑戰",
            "content": """
# 量子運算的突破與挑戰

![量子運算](blog_images[4])

量子運算技術正在逐步從理論走向實用。

## 最新突破

### IBM的量子優勢
IBM發布了新一代量子處理器。

### Google的量子霸權
在特定問題上實現了量子優勢。

## 應用領域
- 密碼學
- 藥物研發
- 金融建模
- 人工智慧

## 面臨的挑戰
- 量子位元的穩定性
- 錯誤率的控制
- 成本問題

量子運算將開啟運算的新紀元。
            """,
            "summary": "分析量子運算技術的最新進展和應用前景",
            "image": blog_images[4] if len(blog_images) > 4 else "/static/images/default-blog.jpg"
        }
    ]
    
    # 生活分享文章（5篇）
    lifestyle_posts = [
        {
            "title": "遠程工作的高效時間管理技巧",
            "content": """
# 遠程工作的高效時間管理技巧

![遠程工作](blog_images[5])

疫情改變了我們的工作模式，遠程工作成為新常態。

## 建立工作儀式感

### 固定的工作時間
- 早上9點開始工作
- 下午6點結束工作
- 中午固定休息時間

### 專用的工作空間
打造一個舒適的家庭辦公室。

## 時間管理工具

### 番茄工作法
- 25分鐘專注工作
- 5分鐘休息
- 4個循環後長休息

### 任務清單
使用Todoist、Notion等工具管理任務。

## 保持專注的技巧
- 關閉社群媒體通知
- 使用白噪音提高專注力
- 定期站起來活動

遠程工作需要更強的自律性，但也帶來更多彈性。
            """,
            "summary": "分享遠程工作的時間管理和效率提升方法",
            "image": blog_images[5] if len(blog_images) > 5 else "/static/images/default-blog.jpg"
        },
        {
            "title": "居家健身的最佳實踐指南",
            "content": """
# 居家健身的最佳實踐指南

![居家健身](blog_images[6])

不需要昂貴的器材，在家也能有效健身。

## 基本器材推薦

### 必備器材
- 瑜伽墊
- 啞鈴（可調重量）
- 彈力帶
- 跳繩

### 進階器材
- 壺鈴
- 懸吊訓練器
- 健身球

## 運動計劃

### 週一：上肢訓練
- 伏地挺身 3組x15次
- 啞鈴彎舉 3組x12次
- 肩部推舉 3組x10次

### 週三：下肢訓練
- 深蹲 3組x20次
- 弓箭步 3組x15次
- 小腿提踵 3組x25次

### 週五：核心訓練
- 平板支撐 3組x60秒
- 捲腹 3組x20次
- 俄羅斯轉體 3組x15次

## 營養建議
運動後30分鐘內補充蛋白質和碳水化合物。

堅持是成功的關鍵！
            """,
            "summary": "提供居家健身的器材選擇和訓練計劃",
            "image": blog_images[6] if len(blog_images) > 6 else "/static/images/default-blog.jpg"
        },
        {
            "title": "打造舒適居家辦公環境的秘訣",
            "content": """
# 打造舒適居家辦公環境的秘訣

![居家辦公](blog_images[7])

良好的工作環境能大幅提升工作效率。

## 空間規劃

### 選擇合適的位置
- 採光良好
- 通風佳
- 相對安靜

### 空間布置
- 面向窗戶或光源
- 背後有實牆支撐
- 保持整潔有序

## 設備配置

### 必備設備
- 人體工學椅子
- 可調高度桌子
- 雙螢幕顯示器
- 機械鍵盤

### 照明設備
- 檯燈避免反光
- 色溫4000K-6500K
- 亮度可調節

## 環境氛圍

### 色彩搭配
使用冷色調提高專注力。

### 植物擺設
綠色植物能減緩眼部疲勞。

### 音響設備
播放白噪音或輕音樂。

投資在工作環境上，等於投資在自己的未來。
            """,
            "summary": "介紹如何設計和布置高效的居家辦公空間",
            "image": blog_images[7] if len(blog_images) > 7 else "/static/images/default-blog.jpg"
        },
        {
            "title": "數位極簡主義：科技與生活的平衡",
            "content": """
# 數位極簡主義：科技與生活的平衡

![數位極簡](blog_images[8])

在資訊爆炸的時代，我們需要學會數位極簡。

## 什麼是數位極簡主義？

數位極簡主義是一種生活哲學，強調：
- 有意識地使用科技
- 專注於真正重要的事物
- 減少數位雜訊的干擾

## 實踐方法

### 1. 清理數位設備
- 刪除不必要的應用程式
- 整理桌面和資料夾
- 定期清理照片和文件

### 2. 管理通知
- 關閉非必要的推播通知
- 設定勿擾時間
- 使用專注模式

### 3. 數位排毒
- 每天固定時間遠離螢幕
- 週末進行數位斷食
- 睡前一小時不使用電子設備

## 好處

### 提高專注力
減少分心，提升工作效率。

### 改善睡眠品質
降低藍光暴露，提升睡眠質量。

### 增進人際關係
更多面對面的真實互動。

數位極簡不是拒絕科技，而是更智慧地使用科技。
            """,
            "summary": "探討如何在數位時代保持生活平衡的方法",
            "image": blog_images[8] if len(blog_images) > 8 else "/static/images/default-blog.jpg"
        },
        {
            "title": "可持續生活：從日常小事做起",
            "content": """
# 可持續生活：從日常小事做起

![可持續生活](blog_images[9])

環保不只是口號，從生活中的小改變開始。

## 減塑生活

### 購物習慣
- 使用環保購物袋
- 選擇散裝商品
- 避免過度包裝

### 替代方案
- 玻璃容器取代塑膠盒
- 不鏽鋼吸管取代塑膠吸管
- 蜂蠟布取代保鮮膜

## 節約能源

### 居家節能
- 使用LED燈泡
- 調整冷氣溫度
- 拔掉不使用的電器插頭

### 交通方式
- 優先使用大眾運輸
- 短距離步行或騎腳踏車
- 共乘或使用電動車

## 減少食物浪費

### 計劃採購
- 列購物清單
- 檢查冰箱存貨
- 適量購買

### 創意料理
- 使用剩菜製作新菜色
- 果皮製作環保清潔劑
- 咖啡渣當作肥料

## 循環利用

### 舊物新用
- 衣物改造
- 家具翻新
- 電子產品回收

每個小行動都是對地球的愛護。
            """,
            "summary": "分享日常生活中的環保實踐方法和技巧",
            "image": blog_images[9] if len(blog_images) > 9 else "/static/images/default-blog.jpg"
        }
    ]
    
    posts = []
    tech_category = categories[0]  # 科技趨勢
    lifestyle_category = categories[1]  # 生活分享
    
    # 建立科技文章
    for i, post_data in enumerate(tech_posts):
        content = post_data["content"].replace("blog_images[0]", post_data["image"])
        
        post = Post(
            title=post_data["title"],
            content=content,
            excerpt=post_data["summary"],
            slug=f"tech-post-{i+1}",
            featured_image=post_data["image"],
            is_published=True
        )
        post.categories.append(tech_category)
        db.add(post)
        posts.append(post)
    
    # 建立生活文章
    for i, post_data in enumerate(lifestyle_posts):
        content = post_data["content"].replace("blog_images[5]", post_data["image"])
        
        post = Post(
            title=post_data["title"],
            content=content,
            excerpt=post_data["summary"],
            slug=f"lifestyle-post-{i+1}",
            featured_image=post_data["image"],
            is_published=True
        )
        post.categories.append(lifestyle_category)
        db.add(post)
        posts.append(post)
    
    db.commit()
    print(f"✅ 已建立 {len(posts)} 篇部落格文章（包含圖片）")
    return posts

def create_products(db: Session, categories, product_images):
    """建立商品（30個）包含圖片"""
    print("🛍️  正在建立商品...")
    
    # 商品數據按分類
    products_data = {
        "3C數位": [
            {"name": "iPhone 15 Pro", "price": 36900, "description": "最新款 iPhone，配備 A17 Pro 晶片，革命性的相機系統和titanium設計", "sku": "IPH15P-128", "category_key": "digital"},
            {"name": "MacBook Air M3", "price": 38900, "description": "輕薄高效能筆記型電腦，搭載M3晶片，續航力可達18小時", "sku": "MBA-M3-256", "category_key": "digital"},
            {"name": "iPad Pro 12.9吋", "price": 35900, "description": "專業級平板電腦，支援Apple Pencil和Magic Keyboard", "sku": "IPD-PRO-129", "category_key": "digital"},
            {"name": "AirPods Pro", "price": 7490, "description": "主動降噪無線耳機，空間音訊技術，完美音質體驗", "sku": "APP-PRO-G2", "category_key": "digital"},
            {"name": "Apple Watch Ultra", "price": 26900, "description": "極限運動智慧手錶，鈦金屬錶殼，49mm大螢幕", "sku": "AWU-49MM", "category_key": "digital"},
            {"name": "Dell XPS 13", "price": 45900, "description": "商務筆記型電腦，13.4吋InfinityEdge螢幕，輕薄便攜", "sku": "DELL-XPS13", "category_key": "digital"},
            {"name": "Samsung Galaxy S24", "price": 28900, "description": "Android 旗艦手機，AI相機功能，120Hz螢幕", "sku": "SGS24-256", "category_key": "digital"},
            {"name": "Nintendo Switch OLED", "price": 10990, "description": "遊戲主機，7吋OLED螢幕，支援TV和攜帶模式", "sku": "NSW-OLED", "category_key": "digital"}
        ],
        "居家生活": [
            {"name": "Dyson V15 吸塵器", "price": 22900, "description": "無線吸塵器，雷射偵測微塵，強力吸力60分鐘", "sku": "DYS-V15", "category_key": "home"},
            {"name": "飛利浦氣炸鍋", "price": 3990, "description": "健康料理氣炸鍋，5.2L大容量，七種預設模式", "sku": "PHI-AF-5L", "category_key": "home"},
            {"name": "IKEA 北歐風餐桌", "price": 8990, "description": "實木餐桌，簡約北歐設計，可容納4-6人用餐", "sku": "IKE-DT-120", "category_key": "home"},
            {"name": "無印良品收納盒", "price": 590, "description": "透明收納盒組，PP材質，可堆疊設計", "sku": "MUJ-BOX-S", "category_key": "home"},
            {"name": "小米掃地機器人", "price": 12900, "description": "智能掃地機器人，3D避障，自動集塵", "sku": "XIA-ROB-S7", "category_key": "home"},
            {"name": "宜得利床包組", "price": 1290, "description": "純棉床包枕套組，雙人尺寸，多色可選", "sku": "NIT-BED-SET", "category_key": "home"},
            {"name": "3M淨水器", "price": 4990, "description": "家用淨水設備，多重過濾系統，NSF認證", "sku": "3M-WF-AP", "category_key": "home"},
            {"name": "象印電子鍋", "price": 7990, "description": "IH電子鍋，10人份容量，多種烹調模式", "sku": "ZOJ-RC-10", "category_key": "home"}
        ],
        "運動健身": [
            {"name": "Adidas UltraBoost 22", "price": 5990, "description": "專業跑鞋，Boost中底科技，透氣舒適", "sku": "ADI-UB22", "category_key": "sports"},
            {"name": "Nike Dri-FIT 運動衣", "price": 1290, "description": "速乾運動上衣，排汗透氣材質，修身版型", "sku": "NIK-DRI-M", "category_key": "sports"},
            {"name": "Under Armour 運動褲", "price": 1990, "description": "彈性運動長褲，HeatGear科技，四向彈性", "sku": "UA-PANT-L", "category_key": "sports"},
            {"name": "瑜伽墊 Premium", "price": 1590, "description": "環保瑜伽墊，6mm厚度，防滑紋理設計", "sku": "YOG-MAT-PR", "category_key": "sports"},
            {"name": "啞鈴組合", "price": 3990, "description": "可調式啞鈴，5-20kg重量調節，節省空間", "sku": "DUM-SET-20", "category_key": "sports"},
            {"name": "健身球 65cm", "price": 790, "description": "防爆健身球，瑞士球運動，增強核心肌群", "sku": "FIT-BALL-65", "category_key": "sports"},
            {"name": "跳繩專業版", "price": 590, "description": "計數跳繩，軸承設計，可調節長度", "sku": "JUM-ROPE-P", "category_key": "sports"}
        ],
        "美妝保養": [
            {"name": "SK-II 神仙水", "price": 6800, "description": "經典保養精華，Pitera™成分，改善肌膚質感", "sku": "SK2-FTE-230", "category_key": "beauty"},
            {"name": "蘭蔻粉底液", "price": 2300, "description": "持久粉底液，24小時不脫妝，自然遮瑕", "sku": "LAN-FOU-30", "category_key": "beauty"},
            {"name": "雅詩蘭黛眼霜", "price": 3200, "description": "抗老眼部精華，緊緻眼周肌膚，淡化細紋", "sku": "EST-EYE-15", "category_key": "beauty"},
            {"name": "倩碧潔面乳", "price": 1100, "description": "溫和潔面乳，深層清潔，適合敏感肌", "sku": "CLI-CLE-200", "category_key": "beauty"},
            {"name": "MAC 口紅", "price": 990, "description": "霧面唇膏，豐富色彩選擇，持久不沾杯", "sku": "MAC-LIP-M", "category_key": "beauty"},
            {"name": "資生堂防曬乳", "price": 1650, "description": "SPF50+ 防曬，水凝質地，清爽不黏膩", "sku": "SHI-SUN-50", "category_key": "beauty"},
            {"name": "FANCL 卸妝油", "price": 780, "description": "無添加卸妝油，溫和卸除彩妝，不刺激", "sku": "FAN-CLE-120", "category_key": "beauty"}
        ]
    }
    
    products = []
    for category in categories:
        if category.name in products_data:
            category_products = products_data[category.name]
            
            for i, product_data in enumerate(category_products):
                category_key = product_data["category_key"]
                
                # 獲取對應的圖片
                if category_key in product_images and i < len(product_images[category_key]):
                    featured_image = product_images[category_key][i]
                else:
                    featured_image = "/static/images/default-product.jpg"
                
                product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    short_description=product_data["description"][:100] + "..." if len(product_data["description"]) > 100 else product_data["description"],
                    price=Decimal(str(product_data["price"])),
                    sku=product_data["sku"],
                    stock_quantity=random.randint(10, 100),
                    is_active=True,
                    is_featured=random.choice([True, False]),
                    featured_image=featured_image
                )
                product.categories.append(category)
                db.add(product)
                products.append(product)
    
    db.commit()
    print(f"✅ 已建立 {len(products)} 個商品（包含圖片）")
    return products

def create_orders(db: Session, users, products):
    """建立訂單（20張）"""
    print("📦 正在建立訂單...")
    
    orders = []
    for i in range(20):
        # 隨機選擇用戶
        user = random.choice(users)
        
        # 建立訂單
        order = Order(
            order_number=f"ORD{fake.random_int(min=100000, max=999999)}",
            user_id=user.id,
            customer_name=user.full_name,
            customer_email=user.email,
            customer_phone=fake.phone_number(),
            status=random.choice([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]),
            shipping_address=fake.address(),
            subtotal=Decimal('0.00'),
            shipping_fee=Decimal('60.00'),
            total_amount=Decimal('0.00')
        )
        db.add(order)
        db.flush()  # 取得 order.id
        
        # 建立訂單項目（1-5個商品）
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        total_amount = Decimal('0.00')
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            item_price = product.price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_price=item_price,
                quantity=quantity
            )
            db.add(order_item)
            total_amount += Decimal(str(item_price)) * quantity
        
        # 更新訂單總金額
        order.subtotal = total_amount
        order.total_amount = total_amount + order.shipping_fee
        orders.append(order)
    
    db.commit()
    print(f"✅ 已建立 {len(orders)} 張訂單")
    return orders

def create_analytics_data(db: Session):
    """建立分析數據"""
    print("📊 正在建立分析數據...")
    
    # 建立一些瀏覽記錄
    for i in range(50):
        page_view = PageView(
            page_url=random.choice([
                "/", "/blog", "/products", "/about", "/contact",
                "/blog/tech-post-1", "/blog/lifestyle-post-1",
                "/product/1", "/product/2", "/product/3"
            ]),
            page_type=random.choice(["home", "blog", "product", "category", "about"]),
            visitor_ip=fake.ipv4(),
            user_agent=fake.user_agent(),
            device_type=random.choice(["desktop", "mobile", "tablet"])
        )
        db.add(page_view)
    
    db.commit()
    print("✅ 分析數據已建立")

def main():
    """主函數"""
    print("🚀 開始重置數據庫並建立包含圖片的測試數據...")
    print("="*60)
    
    # 1. 確保圖片目錄存在
    ensure_image_directories()
    
    # 2. 生成圖片
    blog_images = generate_blog_images()
    product_images = generate_product_images()
    
    # 3. 清除現有數據
    drop_all_tables()
    
    # 4. 建立資料表結構
    create_all_tables()
    
    # 5. 建立測試數據
    db = SessionLocal()
    try:
        # 建立管理員
        admin = create_admin_user(db)
        
        # 建立分類
        blog_categories = create_blog_categories(db)
        product_categories = create_product_categories(db)
        
        # 建立會員
        users = create_users(db)
        
        # 建立文章（包含圖片）
        posts = create_blog_posts(db, blog_categories, admin, blog_images)
        
        # 建立商品（包含圖片）
        products = create_products(db, product_categories, product_images)
        
        # 建立訂單
        orders = create_orders(db, users, products)
        
        # 建立分析數據
        create_analytics_data(db)
        
        print("="*60)
        print("🎉 包含圖片的測試數據建立完成！")
        print(f"📊 統計資訊：")
        print(f"   👑 管理員：1 個")
        print(f"   📂 部落格分類：{len(blog_categories)} 個")
        print(f"   🛍️  商品分類：{len(product_categories)} 個")
        print(f"   👥 會員：{len(users)} 個")
        print(f"   📝 文章：{len(posts)} 篇（包含圖片）")
        print(f"   🛍️  商品：{len(products)} 個（包含圖片）")
        print(f"   📦 訂單：{len(orders)} 張")
        print(f"   🖼️  部落格圖片：{len(blog_images)} 張")
        print(f"   🖼️  商品圖片：{sum(len(imgs) for imgs in product_images.values())} 張")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 