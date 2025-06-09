#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復商品的slug欄位
"""

import os
import sys
import re

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Product

def generate_slug(name):
    """生成slug"""
    # 移除特殊字符，保留中文、英文、數字和空格
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', name)
    # 將空格替換為短橫線
    slug = re.sub(r'\s+', '-', slug.strip())
    # 轉為小寫
    slug = slug.lower()
    return slug

def fix_product_slugs():
    """修復商品slug"""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        
        for product in products:
            if product.slug is None:
                new_slug = generate_slug(product.name)
                product.slug = new_slug
                print(f"✅ 修復商品 slug: {product.name} -> {new_slug}")
        
        db.commit()
        print(f"✅ 已修復 {len(products)} 個商品的 slug")
        
    except Exception as e:
        print(f"❌ 修復商品slug失敗: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函數"""
    print("🔧 開始修復商品slug...")
    fix_product_slugs()
    print("✅ 商品slug修復完成！")

if __name__ == "__main__":
    main() 