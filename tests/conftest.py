import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import uuid
import random

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.product import Product
from app.models.coupon import Coupon, CouponType, DiscountType
from app.auth import create_access_token
from app.config import settings

# 創建測試數據庫
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """數據庫引擎"""
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """測試數據庫會話"""
    Base.metadata.create_all(bind=db_engine)
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
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """測試用戶"""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        hashed_password="$2b$12$fake_hash",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """測試管理員"""
    from app.models.user import UserRole
    unique_id = str(uuid.uuid4())[:8]
    admin = User(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        hashed_password="$2b$12$fake_hash",
        is_active=True,
        is_admin=True,
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_product(db_session):
    """測試商品"""
    unique_id = str(uuid.uuid4())[:8]
    product = Product(
        name=f"測試商品_{unique_id}",
        description="測試商品描述",
        price=Decimal("100.00"),
        stock_quantity=10,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_coupon(db_session):
    """測試優惠券"""
    unique_id = str(uuid.uuid4())[:8]
    coupon = Coupon(
        code=f"TEST{unique_id}",
        name="測試優惠券",
        description="測試優惠券描述",
        coupon_type=CouponType.ORDER_DISCOUNT,
        discount_type=DiscountType.PERCENTAGE,
        discount_value=Decimal("10.00"),
        valid_from=datetime.now(timezone.utc),
        valid_to=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True
    )
    db_session.add(coupon)
    db_session.commit()
    db_session.refresh(coupon)
    return coupon


@pytest.fixture
def test_product_coupon(db_session, test_product):
    """測試商品優惠券"""
    unique_id = str(uuid.uuid4())[:8]
    coupon = Coupon(
        code=f"PRODUCT{unique_id}",
        name="商品優惠券",
        description="商品優惠券描述",
        coupon_type=CouponType.PRODUCT_DISCOUNT,
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("20.00"),
        product_id=test_product.id,
        valid_from=datetime.now(timezone.utc),
        valid_to=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True
    )
    db_session.add(coupon)
    db_session.commit()
    db_session.refresh(coupon)
    return coupon


@pytest.fixture
def test_free_shipping_coupon(db_session):
    """測試免運費優惠券"""
    unique_id = str(uuid.uuid4())[:8]
    coupon = Coupon(
        code=f"FREESHIP{unique_id}",
        name="免運費優惠券",
        description="免運費優惠券描述",
        coupon_type=CouponType.FREE_SHIPPING,
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("0.00"),
        valid_from=datetime.now(timezone.utc),
        valid_to=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True
    )
    db_session.add(coupon)
    db_session.commit()
    db_session.refresh(coupon)
    return coupon


@pytest.fixture
def test_expired_coupon(db_session):
    """測試過期優惠券"""
    unique_id = str(uuid.uuid4())[:8]
    coupon = Coupon(
        code=f"EXPIRED{unique_id}",
        name="過期優惠券",
        description="過期優惠券描述",
        coupon_type=CouponType.ORDER_DISCOUNT,
        discount_type=DiscountType.PERCENTAGE,
        discount_value=Decimal("15.00"),
        valid_from=datetime.now(timezone.utc) - timedelta(days=60),
        valid_to=datetime.now(timezone.utc) - timedelta(days=30),
        is_active=True
    )
    db_session.add(coupon)
    db_session.commit()
    db_session.refresh(coupon)
    return coupon


@pytest.fixture
def admin_token(test_admin):
    """管理員認證令牌"""
    return create_access_token(data={"sub": test_admin.username})


@pytest.fixture
def user_token(test_user):
    """用戶認證令牌"""
    return create_access_token(data={"sub": test_user.username})


@pytest.fixture
def admin_headers(admin_token):
    """管理員認證標頭"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    """用戶認證標頭"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def sample_coupon_data():
    """範例優惠券數據"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "code": f"SAMPLE{unique_id}",
        "name": "範例優惠券",
        "description": "範例優惠券描述",
        "coupon_type": "ORDER_DISCOUNT",
        "discount_type": "PERCENTAGE",
        "discount_value": 15.0,
        "valid_from": datetime.now(timezone.utc).isoformat(),
        "valid_to": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "is_active": True
    }


@pytest.fixture
def sample_product_coupon_data(test_product):
    """範例商品優惠券數據"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "code": f"PRDCT{unique_id}",
        "name": "範例商品優惠券",
        "description": "範例商品優惠券描述",
        "coupon_type": "PRODUCT_DISCOUNT",
        "discount_type": "FIXED",
        "discount_value": 25.0,
        "product_id": test_product.id,
        "valid_from": datetime.now(timezone.utc).isoformat(),
        "valid_to": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "is_active": True
    }


@pytest.fixture
def sample_batch_coupon_data():
    """範例批次優惠券數據"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": "批次優惠券",
        "description": "批次優惠券描述",
        "coupon_type": "ORDER_DISCOUNT",
        "discount_type": "PERCENTAGE",
        "discount_value": 20.0,
        "valid_from": datetime.now(timezone.utc).isoformat(),
        "valid_to": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "is_active": True,
        "quantity": 10
    }


def create_test_coupon(db_session, **kwargs):
    """創建測試優惠券"""
    unique_id = str(uuid.uuid4())[:8]
    defaults = {
        "code": f"TEST{unique_id}",
        "name": "測試優惠券",
        "description": "測試優惠券描述",
        "coupon_type": CouponType.ORDER_DISCOUNT,
        "discount_type": DiscountType.PERCENTAGE,
        "discount_value": Decimal("10.00"),
        "valid_from": datetime.now(timezone.utc),
        "valid_to": datetime.now(timezone.utc) + timedelta(days=30),
        "is_active": True
    }
    defaults.update(kwargs)
    
    coupon = Coupon(**defaults)
    db_session.add(coupon)
    db_session.commit()
    db_session.refresh(coupon)
    return coupon


def create_test_user(db_session, **kwargs):
    """創建測試用戶"""
    from app.models.user import UserRole
    unique_id = str(uuid.uuid4())[:8]
    defaults = {
        "username": f"testuser{unique_id}",
        "email": f"test{unique_id}@example.com",
        "hashed_password": "$2b$12$fake_hash",
        "is_active": True,
        "is_admin": False,
        "role": UserRole.USER
    }
    defaults.update(kwargs)
    
    # 如果是管理員用戶，設置對應的角色
    if defaults.get("is_admin", False):
        defaults["role"] = UserRole.ADMIN
    
    user = User(**defaults)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_product(db_session, **kwargs):
    """創建測試商品"""
    unique_id = str(uuid.uuid4())[:8]
    defaults = {
        "name": f"測試商品{unique_id}",
        "description": "測試商品描述",
        "price": Decimal("100.00"),
        "stock_quantity": 10,
        "is_active": True
    }
    defaults.update(kwargs)
    
    product = Product(**defaults)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """清理測試數據"""
    yield
    # 測試完成後清理數據
    try:
        db_session.query(User).delete()
        db_session.query(Product).delete()
        db_session.query(Coupon).delete()
        db_session.commit()
    except Exception:
        # 如果事務已回滾，先rollback再清理
        db_session.rollback()
        try:
            db_session.query(User).delete()
            db_session.query(Product).delete()
            db_session.query(Coupon).delete()
            db_session.commit()
        except Exception:
            pass 