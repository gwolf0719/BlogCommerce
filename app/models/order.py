from sqlalchemy import Column, String, Text, Numeric, Integer, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class OrderStatus(enum.Enum):
    PENDING = "pending"      # 待處理
    CONFIRMED = "confirmed"  # 已確認
    SHIPPED = "shipped"      # 已出貨
    DELIVERED = "delivered"  # 已送達
    CANCELLED = "cancelled"  # 已取消


class PaymentMethod(enum.Enum):
    transfer = "transfer"   # 轉帳
    linepay = "linepay"     # Line Pay
    ecpay = "ecpay"         # 綠界
    paypal = "paypal"       # PayPal


class PaymentStatus(enum.Enum):
    unpaid = "unpaid"           # 未付款
    paid = "paid"               # 已付款
    failed = "failed"           # 付款失敗
    refunded = "refunded"       # 已退款
    pending = "pending"         # 等待付款/確認
    partial = "partial"         # 部分付款


class Order(BaseModel):
    __tablename__ = "orders"
    
    # 訂單編號
    order_number = Column(String(50), unique=True, nullable=False)
    
    # 會員關聯（可選，支援訪客購買）
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 客戶資訊
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    
    # 配送地址
    shipping_address = Column(Text, nullable=False)
    
    # 訂單金額
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)  # 折扣金額
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # 訂單狀態
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # 備註
    notes = Column(Text, nullable=True)
    
    # 金流相關欄位
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    payment_info = Column(JSON, nullable=True)  # 儲存金流回傳資訊
    payment_updated_at = Column(DateTime, nullable=True)
    
    # 關聯
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    promo_usage = relationship("PromoUsage", back_populates="order", uselist=False)
    # 向後相容的別名
    discount_usage = relationship("PromoUsage", back_populates="order", uselist=False, viewonly=True)
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(BaseModel):
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 商品資訊（訂單時的快照）
    product_name = Column(String(200), nullable=False)
    product_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # 關聯
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    @property
    def total_price(self):
        """項目總價"""
        return self.product_price * self.quantity
    
    def __repr__(self):
        return f"<OrderItem {self.product_name} x {self.quantity}>" 