from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class AdminStatsResponse(BaseModel):
    total_users: int
    total_posts: int
    published_posts: int
    total_products: int
    active_products: int
    total_orders: int
    pending_orders: int
    total_sales: Decimal
    today_orders: int
    today_revenue: Decimal
    active_sessions: int
    total_discount_codes: int
    active_discount_codes: int
    total_discount_usage: int
    today_discount_usage: int
    calculated_at: datetime
