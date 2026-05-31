from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas import (
    ArticleOut,
    ArticleSummaryOut,
    ArticleSummaryPageOut,
    PlatformSettingsOut,
    PublicHomeOut,
    SiteOut,
)
from app.services.access_log import log_page_view, log_site_click
from app.services.platform_settings import get_or_create_platform_settings
from app.services.public_access import ensure_public_articles_enabled, ensure_public_sites_enabled
from app.services.public_articles import (
    get_public_article_detail,
    list_public_article_categories,
    list_public_articles_promoted,
    paginate_public_articles,
    resolve_public_read_payload,
)
from app.services.public_home import build_public_home
from app.services.public_sites import (
    get_public_sites_for_category,
    list_public_site_categories,
    list_public_sites_hot,
    list_public_sites_latest,
    list_public_sites_promoted,
    record_site_visit_buffered,
)
from app.services.stats_buffer import record_page_view_buffered

router = APIRouter(prefix="/api/public", tags=["public"])


@router.post("/visit")
def track_visit():
    record_page_view_buffered()
    log_page_view()
    return {"ok": True}


@router.get("/settings", response_model=PlatformSettingsOut)
def public_settings(db: DbSession):
    return get_or_create_platform_settings(db)


@router.get("/home", response_model=PublicHomeOut)
def public_home(db: DbSession):
    return build_public_home(db)


@router.get("/site-categories", response_model=list[dict])
def public_site_categories(db: DbSession):
    ensure_public_sites_enabled(db)
    return list_public_site_categories(db)


@router.get("/sites/latest", response_model=list[SiteOut])
def public_sites_latest(db: DbSession, limit: int = 12):
    ensure_public_sites_enabled(db)
    return list_public_sites_latest(db, limit)


@router.get("/sites/hot", response_model=list[SiteOut])
def public_sites_hot(db: DbSession, limit: int = 12):
    ensure_public_sites_enabled(db)
    return list_public_sites_hot(db, limit)


@router.get("/sites/promoted", response_model=list[SiteOut])
def public_sites_promoted(db: DbSession, limit: int = 12):
    ensure_public_sites_enabled(db)
    return list_public_sites_promoted(db, limit)


@router.post("/sites/{site_id}/visit")
def public_site_visit(site_id: int, db: DbSession):
    ensure_public_sites_enabled(db)
    record_site_visit_buffered(db, site_id)
    log_site_click(site_id)
    return {"ok": True}


@router.get("/sites", response_model=list[SiteOut])
def public_sites(site_category_id: int, db: DbSession):
    ensure_public_sites_enabled(db)
    return get_public_sites_for_category(db, site_category_id)


@router.get("/article-categories", response_model=list[dict])
def public_article_categories(db: DbSession):
    ensure_public_articles_enabled(db)
    return list_public_article_categories(db)


@router.get("/articles/promoted", response_model=list[ArticleSummaryOut])
def public_articles_promoted(db: DbSession, limit: int = 12):
    ensure_public_articles_enabled(db)
    return list_public_articles_promoted(db, limit)


@router.get("/articles", response_model=ArticleSummaryPageOut)
def public_articles(
    db: DbSession,
    article_category_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
):
    ensure_public_articles_enabled(db)
    return paginate_public_articles(
        db,
        article_category_id=article_category_id,
        page=page,
        page_size=page_size,
    )


@router.get("/articles/{aid}", response_model=ArticleOut)
def public_article_detail(aid: int, db: DbSession):
    ensure_public_articles_enabled(db)
    return get_public_article_detail(db, aid)


@router.get("/articles/{aid}/read")
def public_read_url(aid: int, db: DbSession):
    ensure_public_articles_enabled(db)
    return resolve_public_read_payload(db, aid)
