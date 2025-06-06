from app.database import get_db
from app.models.category import Category
from app.models.tag import Tag

def fix_enum_types():
    """修正資料庫中的 Enum 類型為大寫格式"""
    db = next(get_db())
    
    try:
        # 更新所有 category 的 type 為大寫
        categories = db.query(Category).all()
        for cat in categories:
            if cat.type and cat.type.lower() == 'blog':
                cat.type = 'BLOG'
            elif cat.type and cat.type.lower() == 'product':
                cat.type = 'PRODUCT'

        # 更新所有 tag 的 type 為大寫  
        tags = db.query(Tag).all()
        for tag in tags:
            if tag.type and tag.type.lower() == 'blog':
                tag.type = 'BLOG'
            elif tag.type and tag.type.lower() == 'product':
                tag.type = 'PRODUCT'

        db.commit()
        print('✅ 更新資料庫類型為大寫格式')
        
    except Exception as e:
        db.rollback()
        print(f'❌ 更新失敗: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    fix_enum_types() 