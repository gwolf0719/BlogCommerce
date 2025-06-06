from PIL import Image, ImageDraw, ImageFont
import os

def create_blog_placeholder_images():
    """創建部落格文章的佔位圖片"""
    
    # 確保目錄存在
    blog_dir = "app/static/images/blog"
    os.makedirs(blog_dir, exist_ok=True)
    
    # 圖片尺寸
    width, height = 800, 400
    
    # 部落格文章主題和顏色
    blog_themes = [
        {"name": "AI科技", "color": "#3B82F6", "bg": "#EFF6FF"},
        {"name": "極簡生活", "color": "#10B981", "bg": "#F0FDF4"},
        {"name": "日本櫻花", "color": "#EC4899", "bg": "#FDF2F8"},
        {"name": "咖啡文化", "color": "#92400E", "bg": "#FEF3C7"},
        {"name": "瑜伽健康", "color": "#7C3AED", "bg": "#F5F3FF"},
        {"name": "職場成長", "color": "#DC2626", "bg": "#FEF2F2"},
        {"name": "歐洲旅行", "color": "#059669", "bg": "#ECFDF5"},
        {"name": "科技趨勢", "color": "#2563EB", "bg": "#DBEAFE"}
    ]
    
    for i, theme in enumerate(blog_themes, 1):
        # 創建圖片
        img = Image.new('RGB', (width, height), theme["bg"])
        draw = ImageDraw.Draw(img)
        
        try:
            # 嘗試使用系統字體
            font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
            font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 30)
        except:
            # 如果沒有找到字體，使用默認字體
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # 繪製標題
        title_bbox = draw.textbbox((0, 0), theme["name"], font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        
        title_x = (width - title_width) // 2
        title_y = height // 2 - title_height - 20
        
        draw.text((title_x, title_y), theme["name"], fill=theme["color"], font=font_large)
        
        # 繪製副標題
        subtitle = "部落格精選文章"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + title_height + 30
        
        draw.text((subtitle_x, subtitle_y), subtitle, fill=theme["color"], font=font_small)
        
        # 繪製裝飾邊框
        border_color = theme["color"]
        draw.rectangle([(10, 10), (width-10, height-10)], outline=border_color, width=3)
        
        # 保存圖片
        img_path = os.path.join(blog_dir, f"blog-{i}.jpg")
        img.save(img_path, "JPEG", quality=90)
        print(f"✅ 創建圖片: {img_path}")
    
    print(f"🎉 完成！創建了 {len(blog_themes)} 張部落格插圖")

if __name__ == "__main__":
    create_blog_placeholder_images() 