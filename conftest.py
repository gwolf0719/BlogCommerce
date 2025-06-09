import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 確保使用測試環境
os.environ["TESTING"] = "true"

from app.main import app
from app.database import get_db
from app.models.base import Base
from app.models.user import User
from app.models.post import Post
from app.models.product import Product
from app.models.category import Category, CategoryType
from app.models.tag import Tag, TagType
from app.models.order import Order, OrderItem, OrderStatus
from app.auth import get_password_hash, create_access_token
from datetime import datetime, timedelta
from decimal import Decimal

# 測試數據庫設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """數據庫引擎"""
    Base.metadata.create_all(bind=engine)
    yield engine
    # 測試後清理
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("./test.db")
    except FileNotFoundError:
        pass


@pytest.fixture(scope="function")
def db_session(db_engine):
    """測試數據庫會話"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """測試客戶端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """管理員用戶"""
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """普通用戶"""
    user = User(
        username="testuser",
        email="user@test.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """管理員令牌"""
    return create_access_token(data={"sub": admin_user.username})


@pytest.fixture
def user_token(regular_user):
    """用戶令牌"""
    return create_access_token(data={"sub": regular_user.username})


@pytest.fixture
def blog_category(db_session):
    """部落格分類"""
    category = Category(
        name="技術文章",
        slug="technology",
        type=CategoryType.BLOG,
        description="技術相關文章"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def product_category(db_session):
    """商品分類"""
    category = Category(
        name="電子產品",
        slug="electronics",
        type=CategoryType.PRODUCT,
        description="電子商品分類"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def blog_tag(db_session):
    """部落格標籤"""
    tag = Tag(
        name="Python",
        slug="python",
        type=TagType.BLOG
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture
def sample_post(db_session, blog_category, blog_tag):
    """範例文章"""
    post = Post(
        title="測試文章",
        slug="test-post",
        content="這是一篇測試文章的內容",
        excerpt="測試文章摘要",
        is_published=True,
        meta_title="測試文章",
        meta_description="測試文章描述"
    )
    post.categories.append(blog_category)
    post.tags.append(blog_tag)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def sample_product(db_session, product_category):
    """範例商品"""
    product = Product(
        name="測試商品",
        slug="test-product",
        description="這是一個測試商品",
        price=Decimal("999.00"),
        stock_quantity=10,
        is_active=True,
        is_featured=False
    )
    product.categories.append(product_category)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_order(db_session, regular_user, sample_product):
    """範例訂單"""
    order = Order(
        user_id=regular_user.id,
        order_number=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        customer_name=regular_user.username,
        customer_email=regular_user.email,
        customer_phone="0912345678",
        shipping_address="測試地址",
        total_amount=Decimal("999.00"),
        status=OrderStatus.PENDING
    )
    db_session.add(order)
    db_session.flush()
    
    # 添加訂單項目
    order_item = OrderItem(
        order_id=order.id,
        product_id=sample_product.id,
        product_name=sample_product.name,
        product_price=sample_product.price,
        quantity=1,
        total_price=sample_product.price
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def auth_headers(admin_token):
    """認證標頭"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_auth_headers(user_token):
    """用戶認證標頭"""
    return {"Authorization": f"Bearer {user_token}"} 