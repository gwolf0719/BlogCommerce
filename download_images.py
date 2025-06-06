#!/usr/bin/env python3
"""
下載圖片腳本
從 Unsplash 下載商品和部落格圖片
"""

import os
import requests
import time
from urllib.parse import urlparse

def download_image(url, filename, folder):
    """下載圖片到指定資料夾"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 下載成功: {filename}")
        return True
    except Exception as e:
        print(f"❌ 下載失敗 {filename}: {e}")
        return False

def main():
    # 商品圖片 URLs (從 Unsplash 獲取)
    product_images = {
        # 電子產品
        "iphone-15-pro-256gb.jpg": "https://images.unsplash.com/photo-1696446701796-da61225697cc?w=800&h=600&fit=crop",
        "macbook-air-m3-13inch.jpg": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&h=600&fit=crop",
        "sony-wh1000xm5.jpg": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&h=600&fit=crop",
        "samsung-galaxy-s24-ultra.jpg": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&h=600&fit=crop",
        "ipad-pro-12-9.jpg": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&h=600&fit=crop",
        
        # 服飾配件
        "nike-air-force-1-white.jpg": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&h=600&fit=crop",
        "adidas-ultraboost-22.jpg": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=600&fit=crop",
        "leather-handbag-brown.jpg": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&h=600&fit=crop",
        "mens-casual-shirt.jpg": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=600&fit=crop",
        "womens-denim-jacket.jpg": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&h=600&fit=crop",
        
        # 居家生活
        "coffee-maker-deluxe.jpg": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800&h=600&fit=crop",
        "minimalist-desk-lamp.jpg": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop",
        "ergonomic-office-chair.jpg": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&h=600&fit=crop",
        "smart-home-speaker.jpg": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop",
        "ceramic-dinnerware-set.jpg": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
        
        # 美妝保養
        "skincare-serum-set.jpg": "https://images.unsplash.com/photo-1620916297892-bd66c8f16d67?w=800&h=600&fit=crop",
        "premium-makeup-palette.jpg": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&h=600&fit=crop",
        "organic-face-cream.jpg": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&h=600&fit=crop",
        "luxury-perfume-collection.jpg": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&h=600&fit=crop",
        
        # 運動健身
        "yoga-mat-premium.jpg": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
        "resistance-bands-set.jpg": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
        "fitness-tracker-watch.jpg": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&h=600&fit=crop",
        "protein-powder-vanilla.jpg": "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=800&h=600&fit=crop",
    }
    
    # 部落格圖片 URLs
    blog_images = {
        "tech-trends-2024.jpg": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&h=600&fit=crop",
        "sustainable-fashion.jpg": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&h=600&fit=crop",
        "home-office-setup.jpg": "https://images.unsplash.com/photo-1586227740560-8cf2732c1531?w=800&h=600&fit=crop",
        "skincare-routine.jpg": "https://images.unsplash.com/photo-1556228578-626910a5cd92?w=800&h=600&fit=crop",
        "fitness-motivation.jpg": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
        "coffee-culture.jpg": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800&h=600&fit=crop",
        "digital-minimalism.jpg": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&h=600&fit=crop",
        "healthy-recipes.jpg": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&h=600&fit=crop",
        "travel-essentials.jpg": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=600&fit=crop",
        "productivity-tips.jpg": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&h=600&fit=crop",
    }
    
    # Placeholder 圖片
    placeholder_images = {
        "placeholder-product.jpg": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=600&fit=crop",
        "placeholder-blog.jpg": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&h=600&fit=crop",
    }
    
    # 建立目錄
    os.makedirs("app/static/images/products", exist_ok=True)
    os.makedirs("app/static/images/blog", exist_ok=True)
    
    print("📸 開始下載商品圖片...")
    for filename, url in product_images.items():
        download_image(url, filename, "app/static/images/products")
        time.sleep(1)  # 避免請求過於頻繁
    
    print("\n📰 開始下載部落格圖片...")
    for filename, url in blog_images.items():
        download_image(url, filename, "app/static/images/blog")
        time.sleep(1)
    
    print("\n🖼️ 下載 Placeholder 圖片...")
    for filename, url in placeholder_images.items():
        download_image(url, filename, "app/static/images")
        time.sleep(1)
    
    print("\n✅ 圖片下載完成！")

if __name__ == "__main__":
    main() 