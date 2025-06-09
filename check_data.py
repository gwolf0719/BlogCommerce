#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查數據庫中的商品和分類數據
"""

import os
import sys

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Post, Product, Category

def check_products():
    """檢查商品數據"""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        print(f"📦 商品總數: {len(products)}")
        
        for i, product in enumerate(products[:5]):  # 只顯示前5個
            print(f"   {i+1}. {product.name}")
            print(f"      ID: {product.id}")
            print(f"      SKU: {product.sku}")
            print(f"      Slug: {product.slug}")
            print(f"      Price: {product.price}")
            print(f"      Image: {product.featured_image}")
            print()
            
    except Exception as e:
        print(f"❌ 檢查商品失敗: {e}")
    finally:
        db.close()

def check_categories():
    """檢查分類數據"""
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        print(f"📂 分類總數: {len(categories)}")
        
        for category in categories:
            print(f"   - {category.name} ({category.type})")
            print(f"     Slug: {category.slug}")
            print()
            
    except Exception as e:
        print(f"❌ 檢查分類失敗: {e}")
    finally:
        db.close()

def check_posts():
    """檢查文章數據"""
    db = SessionLocal()
    try:
        posts = db.query(Post).all()
        print(f"📝 文章總數: {len(posts)}")
        
        for i, post in enumerate(posts[:3]):  # 只顯示前3個
            print(f"   {i+1}. {post.title}")
            print(f"      Slug: {post.slug}")
            print(f"      Image: {post.featured_image}")
            print()
            
    except Exception as e:
        print(f"❌ 檢查文章失敗: {e}")
    finally:
        db.close()

def main():
    """主函數"""
    print("🔍 檢查數據庫內容...")
    print("="*50)
    
    check_products()
    check_categories()
    check_posts()

if __name__ == "__main__":
    main() 