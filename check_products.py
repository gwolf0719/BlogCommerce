from app.database import get_db
from app.models.product import Product
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///./blogcommerce.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

products = db.query(Product).all()
print(f'總共有 {len(products)} 個商品')
for p in products[:10]:
    print(f'ID: {p.id}, 名稱: {p.name}, 是否啟用: {p.is_active}, 價格: {p.price}')
db.close() 