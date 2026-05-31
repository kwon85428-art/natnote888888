import logging
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.deps import DbSession
from app.api.routes import (
    admin_article_categories,
    admin_articles,
    admin_logs,
    admin_maintenance,
    admin_settings,
    admin_site_categories,
    admin_sites,
    admin_stats,
    auth,
    public,
    seo,
)
from app.core.config import settings
from app.core.db_dialect import resolve_database_dialect
from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.lifespan_boot import shutdown_application, startup_application
from app.middleware.public_cache import PublicCacheMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

logger = logging.getLogger("navnote")


@asynccontextmanager
async def lifespan(_: FastAPI):
    flush_task = await startup_application(settings)

    yield

    await shutdown_application(flush_task)


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(SecurityHeadersMiddleware)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(PublicCacheMiddleware)

app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")

app.include_router(auth.router)
app.include_router(admin_site_categories.router)
app.include_router(admin_sites.router)
app.include_router(admin_article_categories.router)
app.include_router(admin_articles.router)
app.include_router(admin_settings.router)
app.include_router(admin_stats.router)
app.include_router(admin_logs.router)
app.include_router(admin_maintenance.router)
app.include_router(public.router)
app.include_router(seo.router)


@app.get("/api/health")
def health(db: DbSession):
    dialect = resolve_database_dialect(settings.database_url)
    try:
        db.execute(text("SELECT 1"))
        db_status = "up"
    except Exception:
        logger.exception("数据库健康检查失败")
        db_status = "down"
    status = "ok" if db_status == "up" else "degraded"
    return {
        "status": status,
        "app": settings.app_name,
        "database": db_status,
        "database_dialect": dialect,
    }
