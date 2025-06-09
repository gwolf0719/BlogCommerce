#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立圖片佔位符文件
"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_placeholder_image(filepath, width, height, text, bg_color="#f0f0f0", text_color="#666666"):
    """創建佔位符圖片"""
    try:
        # 建立圖片
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # 嘗試使用系統字體
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 取得文字大小
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 計算文字位置（置中）
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # 繪製文字
        draw.text((x, y), text, fill=text_color, font=font)
        
        # 儲存圖片
        img.save(filepath, 'JPEG', quality=95)
        return True
        
    except Exception as e:
        print(f"建立圖片失敗 {filepath}: {e}")
        return False

def create_blog_images():
    """建立部落格文章佔位符圖片"""
    print("📸 正在建立部落格圖片佔位符...")
    
    blog_topics = [
        "AI Technology",
        "5G Innovation", 
        "Blockchain",
        "Cloud Computing",
        "Quantum Computing",
        "Remote Work",
        "Home Fitness",
        "Home Office",
        "Digital Life",
        "Sustainable Living"
    ]
    
    for i, topic in enumerate(blog_topics):
        filename = f"blog-{i+1}.jpg"
        filepath = f"app/static/images/blog/{filename}"
        
        if create_placeholder_image(filepath, 800, 600, topic, "#e3f2fd", "#1976d2"):
            print(f"✅ 部落格圖片已建立: {filename}")

def create_product_images():
    """建立商品佔位符圖片"""
    print("🛍️  正在建立商品圖片佔位符...")
    
    # 3C數位
    digital_products = [
        "iPhone 15 Pro", "MacBook Air M3", "iPad Pro", "AirPods Pro",
        "Apple Watch", "Dell XPS 13", "Galaxy S24", "Nintendo Switch"
    ]
    
    # 居家生活
    home_products = [
        "Dyson V15", "Air Fryer", "Dining Table", "Storage Box",
        "Robot Vacuum", "Bed Sheets", "Water Filter", "Rice Cooker"
    ]
    
    # 運動健身
    sports_products = [
        "Running Shoes", "Sports Shirt", "Yoga Pants", "Yoga Mat",
        "Dumbbell Set", "Exercise Ball", "Jump Rope"
    ]
    
    # 美妝保養
    beauty_products = [
        "SK-II Essence", "Foundation", "Eye Cream", "Cleanser",
        "MAC Lipstick", "Sunscreen", "Cleansing Oil"
    ]
    
    all_products = [
        (digital_products, "digital", "#f3e5f5"),
        (home_products, "home", "#e8f5e8"),
        (sports_products, "sports", "#fff3e0"),
        (beauty_products, "beauty", "#fce4ec")
    ]
    
    counter = 1
    for products, category, bg_color in all_products:
        for product in products:
            filename = f"product-{counter}.jpg"
            filepath = f"app/static/images/products/{filename}"
            
            if create_placeholder_image(filepath, 600, 600, product, bg_color, "#424242"):
                print(f"✅ 商品圖片已建立: {filename}")
            
            counter += 1

def main():
    """主函數"""
    print("🎨 開始建立圖片佔位符...")
    
    # 確保目錄存在
    Path("app/static/images/blog").mkdir(parents=True, exist_ok=True)
    Path("app/static/images/products").mkdir(parents=True, exist_ok=True)
    
    # 建立圖片
    create_blog_images()
    create_product_images()
    
    print("✅ 所有圖片佔位符已建立完成！")

if __name__ == "__main__":
    main() 