from slugify import slugify
import uuid
import os
from datetime import datetime

def create_slug(text: str) -> str:
    """建立 URL slug"""
    return slugify(text, allow_unicode=True)

def generate_unique_filename(original_filename: str) -> str:
    """產生唯一檔案名稱"""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"

def generate_order_number() -> str:
    """產生訂單編號"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:6].upper()
    return f"ORD{timestamp}{random_suffix}"

def format_currency(amount: float, currency: str = "TWD") -> str:
    """格式化貨幣"""
    if currency == "TWD":
        return f"NT$ {amount:,.0f}"
    elif currency == "USD":
        return f"$ {amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_shipping_cost(total_amount: float, threshold: float = 1000.0, shipping_cost: float = 100.0) -> float:
    """計算運費"""
    if total_amount >= threshold:
        return 0.0
    return shipping_cost

def truncate_text(text: str, max_length: int = 150) -> str:
    """截斷文字"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """驗證檔案類型"""
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1]
    return file_ext in [ext.lower() for ext in allowed_types]

def get_file_size_mb(file_size_bytes: int) -> float:
    """轉換檔案大小為 MB"""
    return file_size_bytes / (1024 * 1024) 