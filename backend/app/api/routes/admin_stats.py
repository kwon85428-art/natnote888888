from fastapi import APIRouter, Query
from sqlalchemy import func

from app.api.deps import CurrentAdmin, DbSession
from app.core.admin_labels_zh import admin_action_options, label_content_type
from app.models import Article, ArticleCategory, Site, SiteCategory
from app.schemas import StatsLogActionsOut, StatsSummaryOut, TrendPageOut
from app.services.visit_stats import build_trend_series, visits_today, visits_total

router = APIRouter(prefix="/api/admin", tags=["admin-stats"])


@router.get("/stats/summary", response_model=StatsSummaryOut)
def stats_summary(_admin: CurrentAdmin, db: DbSession):
    sites_total = db.query(Site).count()
    sites_valid = db.query(Site).filter(Site.is_valid.is_(True)).count()
    sites_invalid = db.query(Site).filter(Site.is_valid.is_(False)).count()
    sites_by_category: dict[str, int] = {}
    for name, cnt in (
        db.query(SiteCategory.name, func.count(Site.id))
        .outerjoin(Site, Site.site_category_id == SiteCategory.id)
        .group_by(SiteCategory.id, SiteCategory.name)
        .all()
    ):
        sites_by_category[name] = int(cnt)

    articles_total = db.query(Article).count()
    articles_by_category: dict[str, int] = {}
    for name, cnt in (
        db.query(ArticleCategory.name, func.count(Article.id))
        .outerjoin(Article, Article.article_category_id == ArticleCategory.id)
        .group_by(ArticleCategory.id, ArticleCategory.name)
        .all()
    ):
        articles_by_category[name] = int(cnt)

    articles_by_content_type: dict[str, int] = {}
    for ct, cnt in db.query(Article.content_type, func.count(Article.id)).group_by(Article.content_type).all():
        lbl = label_content_type(str(ct))
        articles_by_content_type[lbl] = articles_by_content_type.get(lbl, 0) + int(cnt)

    site_clicks = int(db.query(func.coalesce(func.sum(Site.visit_count), 0)).scalar() or 0)
    article_reads = int(db.query(func.coalesce(func.sum(Article.visit_count), 0)).scalar() or 0)

    return StatsSummaryOut(
        sites_total=sites_total,
        sites_by_category=sites_by_category,
        sites_valid=sites_valid,
        sites_invalid=sites_invalid,
        articles_total=articles_total,
        articles_by_category=articles_by_category,
        articles_by_content_type=articles_by_content_type,
        visits_total=visits_total(db),
        visits_today=visits_today(db),
        site_clicks_total=site_clicks,
        article_reads_total=article_reads,
    )


@router.get("/stats/log-actions", response_model=StatsLogActionsOut)
def stats_log_actions(_admin: CurrentAdmin):
    return StatsLogActionsOut(items=admin_action_options())


@router.get("/stats/trend", response_model=TrendPageOut)
def stats_trend(
    _admin: CurrentAdmin,
    db: DbSession,
    period: str = Query("day", pattern="^(day|week|month)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
):
    series = build_trend_series(db, period)
    newest_first = list(reversed(series))
    total = len(newest_first)
    start_idx = (page - 1) * page_size
    page_items = newest_first[start_idx : start_idx + page_size]
    return TrendPageOut(items=page_items, total=total, page=page, page_size=page_size)
