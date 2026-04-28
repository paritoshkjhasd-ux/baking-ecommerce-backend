"""
app/api/v1/__init__.py
----------------------
Central router for API version 1.
Uncomment each router as the week's feature is built.
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

# ── Week 2: Auth ──────────────────────────────────────────────
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# ── Week 3: Admin / Products ──────────────────────────────────
# from app.api.v1.admin import router as admin_router
# api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

# ── Week 5: Public Products & Cart ───────────────────────────
# from app.api.v1.products import router as products_router
# api_router.include_router(products_router, prefix="/products", tags=["Products"])

# from app.api.v1.cart import router as cart_router
# api_router.include_router(cart_router, prefix="/cart", tags=["Cart"])

# ── Week 6: Orders ────────────────────────────────────────────
# from app.api.v1.orders import router as orders_router
# api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])

# ── Week 7: Reviews ───────────────────────────────────────────
# from app.api.v1.reviews import router as reviews_router
# api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
