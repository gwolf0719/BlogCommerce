"""
BlogCommerce 測試配置文件
提供測試夾具、資料庫配置和共用設定
"""
import asyncio
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 設定測試環境
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.product import Product
from app.models.post import Post
from app.models.order import Order
from app.models.coupon import Coupon
from app.models.campaign import MarketingCampaign
from app.models.settings import SystemSettings
from app.auth import get_current_user, get_current_admin_user

# 創建測試用的資料庫引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆寫資料庫依賴項"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆寫應用程式的資料庫依賴項
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db():
    """創建測試資料庫"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """創建測試客戶端"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_redis():
    """模擬 Redis 客戶端"""
    with patch('app.database.redis_client') as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        mock_redis.exists.return_value = False
        yield mock_redis


@pytest.fixture
def test_user(db):
    """創建測試用戶"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db):
    """創建測試管理員用戶"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password="$2b$12$test_hashed_password",
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user):
    """創建認證標頭"""
    from app.auth import create_access_token
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(test_admin_user):
    """創建管理員認證標頭"""
    from app.auth import create_access_token
    token = create_access_token(data={"sub": test_admin_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_product(db):
    """創建測試商品"""
    product = Product(
        name="測試商品",
        description="這是一個測試商品",
        price=100.0,
        stock_quantity=50,
        is_active=True,
        slug="test-product"
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def test_post(db):
    """創建測試文章"""
    post = Post(
        title="測試文章",
        content="這是一個測試文章內容",
        excerpt="測試摘要",
        slug="test-post",
        is_published=True
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@pytest.fixture
def test_order(db, test_user):
    """創建測試訂單"""
    from app.models.order import OrderStatus, PaymentMethod
    
    order = Order(
        order_number="TEST-ORDER-001",
        user_id=test_user.id,
        customer_name="測試客戶",
        customer_email="test@example.com",
        shipping_address="測試地址",
        subtotal=100.0,
        total_amount=100.0,
        status=OrderStatus.PENDING,
        payment_method=PaymentMethod.transfer
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture
def test_coupon(db):
    """創建測試優惠券"""
    from datetime import datetime, timezone
    from app.models.coupon import CouponType, DiscountType
    
    coupon = Coupon(
        code="TESTCODE",
        name="測試優惠券",
        coupon_type=CouponType.ORDER_DISCOUNT,
        discount_type=DiscountType.PERCENTAGE,
        discount_value=10.0,
        valid_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
        valid_to=datetime(2024, 12, 31, tzinfo=timezone.utc),
        is_active=True,
        usage_limit=100
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@pytest.fixture
def test_campaign(db):
    """創建測試活動"""
    from datetime import datetime, timezone
    campaign = MarketingCampaign(
        name="測試活動",
        description="測試活動描述",
        coupon_prefix="TEST",
        coupon_type="percentage",
        discount_type="percentage",
        discount_value=10.0,
        campaign_start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        campaign_end=datetime(2024, 12, 31, tzinfo=timezone.utc),
        coupon_valid_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
        coupon_valid_to=datetime(2024, 12, 31, tzinfo=timezone.utc),
        total_coupons=100,
        initial_coupons=50,
        is_active=True
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@pytest.fixture
def test_settings(db):
    """創建測試設定"""
    settings = SystemSettings(
        key="site_name",
        value="測試網站",
        description="網站名稱",
        category="general",
        data_type="string",
        is_public=True
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@pytest.fixture
def mock_current_user(test_user):
    """模擬當前用戶"""
    def _mock_current_user():
        return test_user
    
    with patch.object(app.dependency_overrides, 'get', return_value=_mock_current_user):
        app.dependency_overrides[get_current_user] = _mock_current_user
        yield test_user
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def mock_admin_user(test_admin_user):
    """模擬管理員用戶"""
    def _mock_admin_user():
        return test_admin_user
    
    with patch.object(app.dependency_overrides, 'get', return_value=_mock_admin_user):
        app.dependency_overrides[get_current_admin_user] = _mock_admin_user
        yield test_admin_user
        app.dependency_overrides.pop(get_current_admin_user, None)


@pytest.fixture
def temp_file():
    """創建臨時文件"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_file_upload():
    """模擬文件上傳"""
    return MagicMock()


@pytest.fixture
def mock_payment_service():
    """模擬支付服務"""
    with patch('app.services.payment_service.PaymentService') as mock:
        mock.return_value.process_payment.return_value = {"status": "success", "transaction_id": "test123"}
        yield mock


@pytest.fixture
def mock_email_service():
    """模擬郵件服務"""
    with patch('app.services.email_service.EmailService') as mock:
        mock.return_value.send_email.return_value = True
        yield mock


@pytest.fixture
def mock_ai_service():
    """模擬 AI 服務"""
    with patch('app.services.ai_service.AIService') as mock:
        mock.return_value.generate_content.return_value = "Generated content"
        yield mock


@pytest.fixture(autouse=True)
def cleanup():
    """自動清理測試資料"""
    yield
    # 清理測試後的資料
    if hasattr(app, 'dependency_overrides'):
        app.dependency_overrides.clear()


# 測試用的常數
TEST_CONFIG = {
    "TESTING": True,
    "DATABASE_URL": "sqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "REDIS_URL": "redis://localhost:6379/15",
    "UPLOAD_FOLDER": "/tmp/test_uploads",
    "MAX_FILE_SIZE": 5 * 1024 * 1024,  # 5MB
}


def pytest_configure(config):
    """pytest 配置鉤子"""
    # 設定測試環境變數
    for key, value in TEST_CONFIG.items():
        os.environ[key] = str(value)
    
    # 確保測試目錄存在
    os.makedirs("logs", exist_ok=True)
    os.makedirs("/tmp/test_uploads", exist_ok=True)


def pytest_unconfigure(config):
    """pytest 清理鉤子"""
    # 清理測試環境變數
    for key in TEST_CONFIG.keys():
        os.environ.pop(key, None) 