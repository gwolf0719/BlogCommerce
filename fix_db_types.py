import sqlite3

def fix_database_types():
    """修正資料庫中的小寫類型值為大寫"""
    conn = sqlite3.connect('blogcommerce.db')
    cursor = conn.cursor()
    
    try:
        # 修正 categories 表中的類型
        cursor.execute("UPDATE categories SET type = 'BLOG' WHERE type = 'blog'")
        cursor.execute("UPDATE categories SET type = 'PRODUCT' WHERE type = 'product'")
        
        # 修正 tags 表中的類型
        cursor.execute("UPDATE tags SET type = 'BLOG' WHERE type = 'blog'")
        cursor.execute("UPDATE tags SET type = 'PRODUCT' WHERE type = 'product'")
        
        conn.commit()
        print('✅ 修正資料庫類型值成功')
        
        # 檢查修正結果
        cursor.execute("SELECT DISTINCT type FROM categories")
        print('Categories 類型:', [row[0] for row in cursor.fetchall()])
        
        cursor.execute("SELECT DISTINCT type FROM tags")
        print('Tags 類型:', [row[0] for row in cursor.fetchall()])
        
    except Exception as e:
        conn.rollback()
        print(f'❌ 修正失敗: {e}')
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_types() 