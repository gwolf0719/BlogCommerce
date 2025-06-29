from fastapi import APIRouter
from app.routes import (
    auth, posts, products, orders,
    admin, cart, analytics, favorites,
    newsletter, settings as settings_router,
    error_logs, view_tracking, payment
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
router.include_router(error_logs.router)
router.include_router(view_tracking.router)
router.include_router(payment.router)
