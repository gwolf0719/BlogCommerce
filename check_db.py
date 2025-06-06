import sqlite3

def check_database():
    """檢查資料庫的內容"""
    conn = sqlite3.connect('blogcommerce.db')
    cursor = conn.cursor()
    
    print("=== Categories ===")
    cursor.execute('SELECT id, name, type FROM categories')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, Name: {row[1]}, Type: {row[2]}')
    
    print("\n=== Tags ===")
    cursor.execute('SELECT id, name, type FROM tags')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, Name: {row[1]}, Type: {row[2]}')
    
    print("\n=== Posts ===")
    cursor.execute('SELECT id, title FROM posts')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, Title: {row[1]}')
    
    conn.close()

if __name__ == "__main__":
    check_database() 