import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.post import Post
from app.models.product import Product
from werkzeug.security import generate_password_hash


# 測試資料庫 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 建立測試資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 建立測試會話工廠
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """建立測試資料庫引擎"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """建立測試資料庫會話"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """建立測試客戶端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """建立測試用戶"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=generate_password_hash("testpassword"),
        full_name="Test User",
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """建立管理員用戶"""
    user = User(
        username="admin",
        email="admin@example.com", 
        password_hash=generate_password_hash("adminpassword"),
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_post(db_session):
    """建立範例文章"""
    post = Post(
        title="測試文章",
        content="這是一篇測試文章的內容",
        excerpt="測試文章摘要",
        is_published=True
    )
    post.slug = post.generate_slug(post.title)
    
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def sample_product(db_session):
    """建立範例商品"""
    product = Product(
        name="測試商品",
        description="這是一個測試商品",
        short_description="測試商品簡述",
        price=1000,
        stock_quantity=10,
        sku="TEST-001",
        is_active=True
    )
    product.slug = product.generate_slug(product.name)
    
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product 