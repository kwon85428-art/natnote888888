"""管理端网站 CRUD、抓取与可达性检查。"""

from fastapi import HTTPException
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Site, SiteCategory
from app.schemas import SiteCheckOut, SiteCreate, SiteFetchIn, SiteFetchOut, SiteOut, SitePageOut, SiteUpdate
from app.services.admin_action_log import AdminActionLog
from app.services.file_storage import save_remote_to_uploads
from app.services.ordering import site_public_order
from app.services.scrape import check_url_reachable, fetch_site_metadata


def list_admin_sites(
    db: Session,
    *,
    q: str | None = None,
    site_category_id: int | None = None,
    tag: str | None = None,
    valid_only: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> SitePageOut:
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 20), 100))
    stmt = db.query(Site).options(joinedload(Site.site_category))
    if q:
        stmt = stmt.filter(or_(Site.name.contains(q), Site.url.contains(q)))
    if site_category_id is not None:
        stmt = stmt.filter(Site.site_category_id == site_category_id)
    if tag:
        stmt = stmt.filter(cast(Site.tags, String).like(f'%"{tag}"%'))
    if valid_only is True:
        stmt = stmt.filter(Site.is_valid.is_(True))
    elif valid_only is False:
        stmt = stmt.filter(Site.is_valid.is_(False))
    total = stmt.count()
    rows = (
        stmt.order_by(*site_public_order())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return SitePageOut(items=rows, total=total, page=page, page_size=page_size)


def create_admin_site(db: Session, audit: AdminActionLog, body: SiteCreate) -> SiteOut:
    if not db.get(SiteCategory, body.site_category_id):
        raise HTTPException(status_code=400, detail="分类不存在")
    row = Site(
        name=body.name,
        url=body.url,
        site_category_id=body.site_category_id,
        tags=body.tags,
        description=body.description,
        favicon_path=body.favicon_path,
        logo_path=body.logo_path,
        is_valid=body.is_valid,
        sort_order=body.sort_order,
        is_promoted=body.is_promoted,
        visit_count=0,
    )
    db.add(row)
    db.flush()
    audit.record("site_create", resource_type="site", resource_id=str(row.id), detail=body.name)
    db.commit()
    db.refresh(row)
    return row


def update_admin_site(db: Session, audit: AdminActionLog, sid: int, body: SiteUpdate) -> SiteOut:
    row = db.get(Site, sid)
    if not row:
        raise HTTPException(status_code=404, detail="站点不存在")
    if body.site_category_id is not None and not db.get(SiteCategory, body.site_category_id):
        raise HTTPException(status_code=400, detail="分类不存在")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    audit.record("site_update", resource_type="site", resource_id=str(sid))
    db.commit()
    db.refresh(row)
    return row


def delete_admin_site(db: Session, audit: AdminActionLog, sid: int) -> dict:
    row = db.get(Site, sid)
    if not row:
        raise HTTPException(status_code=404, detail="站点不存在")
    db.delete(row)
    audit.record("site_delete", resource_type="site", resource_id=str(sid))
    db.commit()
    return {"ok": True}


async def fetch_site_meta(body: SiteFetchIn) -> SiteFetchOut:
    try:
        meta = await fetch_site_metadata(body.url)
        return SiteFetchOut(**meta)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"抓取失败: {str(e)[:200]}") from e


async def apply_site_fetch(db: Session, audit: AdminActionLog, sid: int, body: SiteFetchIn) -> SiteOut:
    row = db.get(Site, sid)
    if not row:
        raise HTTPException(status_code=404, detail="站点不存在")
    try:
        meta = await fetch_site_metadata(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"抓取失败: {str(e)[:200]}") from e
    row.name = meta["title"][:250]
    row.url = meta["resolved_url"]
    row.description = meta.get("description")
    if meta.get("favicon_url"):
        path = await save_remote_to_uploads(meta["favicon_url"], "favicons")
        if path:
            row.favicon_path = path
    audit.record("site_refetch", resource_type="site", resource_id=str(sid))
    db.commit()
    db.refresh(row)
    return SiteOut.model_validate(row)


async def check_admin_site(db: Session, audit: AdminActionLog, sid: int) -> SiteCheckOut:
    row = db.get(Site, sid)
    if not row:
        raise HTTPException(status_code=404, detail="站点不存在")
    ok, msg = await check_url_reachable(row.url)
    row.is_valid = ok
    row.invalid_note = None if ok else msg
    audit.record("site_check", resource_type="site", resource_id=str(sid), detail="ok" if ok else msg)
    db.commit()
    return SiteCheckOut(site_id=sid, ok=ok, message=msg)


async def check_admin_sites_batch(db: Session, audit: AdminActionLog, ids: list[int]) -> list[SiteCheckOut]:
    out: list[SiteCheckOut] = []
    for sid in ids:
        row = db.get(Site, sid)
        if not row:
            continue
        ok, msg = await check_url_reachable(row.url)
        row.is_valid = ok
        row.invalid_note = None if ok else msg
        out.append(SiteCheckOut(site_id=sid, ok=ok, message=msg))
    audit.record("site_check_batch", detail=f"count={len(out)}")
    db.commit()
    return out
