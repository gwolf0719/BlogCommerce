from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 建立資料庫引擎
engine = create_engine(
    settings.database_url,
    # SQLite 專用設定
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# 建立 Session 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立 Base 類別
Base = declarative_base()


# 資料庫 Session 依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 初始化資料庫
def init_db():
    Base.metadata.create_all(bind=engine) 