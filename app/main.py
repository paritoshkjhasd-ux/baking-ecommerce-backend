"""
app/main.py
-----------
FastAPI application factory.

This file:
  1. Creates the FastAPI instance with metadata
  2. Registers startup / shutdown lifecycle hooks (DB connect / disconnect)
  3. Adds CORS middleware
  4. Mounts the versioned API router
  5. Exposes a public health-check endpoint
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import connect_db, close_db
from app.api.v1 import api_router

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (replaces deprecated @app.on_event) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code before `yield` runs on startup.
    Code after  `yield` runs on shutdown.
    """
    # ── Startup ──
    logger.info("🚀  Starting %s v%s …", settings.APP_NAME, settings.APP_VERSION)
    await connect_db()
    yield
    # ── Shutdown ──
    logger.info("🛑  Shutting down …")
    await close_db()


# ── Application instance ──────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend API for a baking e-commerce platform. "
        "Supports customer browsing, shopping cart, order management, "
        "and a full admin panel."
    ),
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc UI
    lifespan=lifespan,
)


# ── CORS middleware ────────────────────────────────────────────────────────────
# Allows the frontend (running on a different port / domain) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],   # Authorization, Content-Type, etc.
)


# ── Versioned API router ───────────────────────────────────────────────────────
# All /api/v1/... routes are handled by the central api_router.
app.include_router(api_router, prefix="/api/v1")


# ── Root / Health-check endpoints ─────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint — confirms the server is running.
    No authentication required.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health-check endpoint used by monitoring tools and deployment pipelines.

    Returns
    -------
    status   : "ok" when everything is healthy
    database : connection status
    """
    from app.database.connection import get_client

    db_status = "disconnected"
    try:
        # A cheap command to verify the DB is reachable
        await get_client().admin.command("ping")
        db_status = "connected"
    except Exception as exc:
        logger.error("DB ping failed: %s", exc)

    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
    }
