from fastapi import APIRouter
from app.routes import (
    auth, posts, products, orders,
    admin, cart, analytics, favorites,
    newsletter, settings as settings_router,
    view_tracking, payment, banners, shipping_tiers,
    discount_codes
)

router = APIRouter()
router.include_router(auth.router)
router.include_router(posts.router)
router.include_router(products.router)
router.include_router(orders.router)
router.include_router(admin.router)
router.include_router(cart.router)
router.include_router(analytics.router)
router.include_router(favorites.router)
router.include_router(newsletter.router)
router.include_router(settings_router.router)
router.include_router(view_tracking.router)
router.include_router(payment.router)
router.include_router(banners.router)
router.include_router(shipping_tiers.router)
router.include_router(discount_codes.router)

# 為了向後相容，也加入舊的路由路徑
# 這裡建立一個簡單的別名路由，指向同樣的處理器
discount_codes_compat = APIRouter(prefix="/api/discount-codes", tags=["折扣碼管理 (向後相容)"])
# 添加主要的路由
discount_codes_compat.get("", tags=["折扣碼管理 (向後相容)"])(discount_codes.get_promo_codes)
discount_codes_compat.post("/validate", tags=["折扣碼管理 (向後相容)"])(discount_codes.validate_promo_code)
discount_codes_compat.get("/stats", tags=["折扣碼管理 (向後相容)"])(discount_codes.get_promo_code_stats_simple)
discount_codes_compat.get("/stats/overview", tags=["折扣碼管理 (向後相容)"])(discount_codes.get_promo_code_stats)
discount_codes_compat.get("/{promo_code_id}/usage", tags=["折扣碼管理 (向後相容)"])(discount_codes.get_promo_code_usage)
discount_codes_compat.get("/{promo_code_id}", tags=["折扣碼管理 (向後相容)"])(discount_codes.get_promo_code)
discount_codes_compat.post("", tags=["折扣碼管理 (向後相容)"])(discount_codes.create_promo_code)
discount_codes_compat.put("/{promo_code_id}", tags=["折扣碼管理 (向後相容)"])(discount_codes.update_promo_code)
discount_codes_compat.delete("/{promo_code_id}", tags=["折扣碼管理 (向後相容)"])(discount_codes.delete_promo_code)

router.include_router(discount_codes_compat)
