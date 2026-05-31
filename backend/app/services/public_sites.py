"""前台网址列表查询（公开端点与首页聚合共用）。"""

from fastapi import HTTPException
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models import Site, SiteCategory
from app.services.ordering import site_public_order


def public_site_base_query(db: Session):
    return (
        db.query(Site)
        .join(SiteCategory, Site.site_category_id == SiteCategory.id)
        .options(contains_eager(Site.site_category))
        .filter(
            SiteCategory.enabled.is_(True),
            SiteCategory.is_system.is_(False),
            Site.is_valid.is_(True),
        )
    )


def list_sites_by_site_category(db: Session, site_category_id: int):
    return (
        db.query(Site)
        .options(joinedload(Site.site_category))
        .filter(Site.site_category_id == site_category_id, Site.is_valid.is_(True))
        .order_by(*site_public_order())
        .all()
    )


def list_public_site_categories(db: Session) -> list[dict]:
    rows = (
        db.query(SiteCategory)
        .filter(SiteCategory.enabled.is_(True), SiteCategory.is_system.is_(False))
        .order_by(SiteCategory.sort_order.asc(), SiteCategory.id.asc())
        .all()
    )
    return [{"id": r.id, "name": r.name, "description": r.description, "icon_key": r.icon_key} for r in rows]


def _clamp_limit(limit: int | None, default: int = 12, max_lim: int = 48) -> int:
    return max(1, min(int(limit or default), max_lim))


def list_public_sites_latest(db: Session, limit: int = 12):
    lim = _clamp_limit(limit)
    return public_site_base_query(db).order_by(Site.created_at.desc(), Site.id.desc()).limit(lim).all()


def list_public_sites_hot(db: Session, limit: int = 12):
    lim = _clamp_limit(limit)
    return (
        public_site_base_query(db)
        .order_by(Site.visit_count.desc(), Site.created_at.desc(), Site.id.desc())
        .limit(lim)
        .all()
    )


def list_public_sites_promoted(db: Session, limit: int = 12):
    lim = _clamp_limit(limit)
    return (
        public_site_base_query(db)
        .filter(Site.is_promoted.is_(True))
        .order_by(Site.visit_count.desc(), Site.created_at.desc(), Site.id.desc())
        .limit(lim)
        .all()
    )


def record_site_visit_buffered(db: Session, site_id: int) -> None:
    """校验站点存在后写入点击缓冲。"""
    row = db.get(Site, site_id)
    if not row or not row.is_valid:
        raise HTTPException(status_code=404, detail="网站不存在")
    from app.services.stats_buffer import record_site_visit_buffered as buf

    buf(site_id)


def get_public_sites_for_category(db: Session, site_category_id: int):
    cat = db.get(SiteCategory, site_category_id)
    if not cat or not cat.enabled or cat.is_system:
        raise HTTPException(status_code=404, detail="分类不存在")
    return list_sites_by_site_category(db, site_category_id)
