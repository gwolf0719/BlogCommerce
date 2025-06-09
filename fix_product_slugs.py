#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復商品的slug欄位
"""

import asyncio
import sys
from pathlib import Path
import re

# 添加專案路徑
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.product import Product
from app.utils.logger import db_logger

def generate_slug(name: str) -> str:
    """從商品名稱生成 slug"""
    # 移除特殊字符，保留中文、英文、數字
    slug = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', name)
    # 將空格和多個連字符替換為單個連字符
    slug = re.sub(r'[\s-]+', '-', slug)
    # 移除開頭和結尾的連字符
    slug = slug.strip('-').lower()
    
    # 如果 slug 為空或過短，使用預設格式
    if not slug or len(slug) < 2:
        slug = f"product-{abs(hash(name)) % 100000}"
    
    return slug

async def fix_product_slugs():
    """修復商品 slug 問題"""
    print("🔧 開始修復商品 slug 問題...")
    
    db = SessionLocal()
    try:
        # 查詢所有 slug 為 None 的商品
        products = db.query(Product).filter(Product.slug.is_(None)).all()
        
        if not products:
            print("✅ 沒有發現 slug 為 None 的商品")
            return
        
        print(f"🔍 找到 {len(products)} 個需要修復的商品")
        
        # 修復每個商品的 slug
        for i, product in enumerate(products, 1):
            original_name = product.name
            new_slug = generate_slug(original_name)
            
            # 確保 slug 唯一性
            base_slug = new_slug
            counter = 1
            
            while True:
                # 檢查是否已存在相同的 slug
                existing = db.query(Product).filter(
                    Product.slug == new_slug,
                    Product.id != product.id
                ).first()
                
                if not existing:
                    break
                
                # 如果存在，添加數字後綴
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            
            product.slug = new_slug
            print(f"   {i}. {original_name} -> {new_slug}")
        
        # 提交變更
        db.commit()
        print(f"✅ 成功修復 {len(products)} 個商品的 slug")
        
        # 驗證修復結果
        null_slugs = db.query(Product).filter(Product.slug.is_(None)).count()
        empty_slugs = db.query(Product).filter(Product.slug == "").count()
        
        print(f"修復完成:")
        print(f"- 修復了 {len(products)} 個商品的slug")
        print(f"- 仍有 {null_slugs} 個null slug")
        print(f"- 仍有 {empty_slugs} 個空字符串slug")
        
        if null_slugs == 0 and empty_slugs == 0:
            print("✅ 所有商品都有有效的slug")
        else:
            print("❌ 仍有商品沒有有效的slug")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 修復過程中發生錯誤: {e}")
        raise
    finally:
        db.close()

def main():
    """主函數"""
    print("🛠️  商品 Slug 修復工具")
    print("=" * 40)
    
    try:
        asyncio.run(fix_product_slugs())
        print("\n🎉 修復完成！")
        
    except Exception as e:
        print(f"\n❌ 程式執行時發生錯誤: {e}")

if __name__ == "__main__":
    main() 