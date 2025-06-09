#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新數據庫中的圖片路徑
"""

import os
import sys

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Post, Product

def update_blog_images():
    """更新部落格文章圖片路徑"""
    db = SessionLocal()
    try:
        posts = db.query(Post).all()
        
        for i, post in enumerate(posts):
            image_path = f"/static/images/blog/blog-{i+1}.jpg"
            post.featured_image = image_path
            
            # 更新文章內容中的圖片
            if post.content and "blog_images[" in post.content:
                post.content = post.content.replace(
                    f"![{post.title}](blog_images[{i}])", 
                    f"![{post.title}]({image_path})"
                )
            
            print(f"✅ 更新文章圖片: {post.title} -> {image_path}")
        
        db.commit()
        print(f"✅ 已更新 {len(posts)} 篇文章的圖片")
        
    except Exception as e:
        print(f"❌ 更新文章圖片失敗: {e}")
        db.rollback()
    finally:
        db.close()

def update_product_images():
    """更新商品圖片路徑"""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        
        for i, product in enumerate(products):
            image_path = f"/static/images/products/product-{i+1}.jpg"
            product.featured_image = image_path
            
            print(f"✅ 更新商品圖片: {product.name} -> {image_path}")
        
        db.commit()
        print(f"✅ 已更新 {len(products)} 個商品的圖片")
        
    except Exception as e:
        print(f"❌ 更新商品圖片失敗: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函數"""
    print("🔄 開始更新數據庫中的圖片路徑...")
    
    update_blog_images()
    update_product_images()
    
    print("✅ 圖片路徑更新完成！")

if __name__ == "__main__":
    main() 