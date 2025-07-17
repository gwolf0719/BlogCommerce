import uuid
from datetime import datetime

def generate_order_number() -> str:
    """
    生成一個唯一的訂單編號。
    格式: ORD-YYYYMMDD-8位隨機字符
    """
    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:8].upper()
    return f"ORD{date_part}-{random_part}"

def generate_slug(text: str) -> str:
    """
    根據給定的文字生成一個 URL-friendly 的 slug。
    (此功能為可選，但放在 helpers 中很常見)
    """
    import re
    # 轉換為小寫，並用連字號替換非字母數字字符
    slug = text.lower().strip()
    slug = re.sub(r'[\s\W-]+', '-', slug)
    return slug

