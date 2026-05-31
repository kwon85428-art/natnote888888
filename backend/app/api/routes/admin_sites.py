from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile

from app.api.deps import CurrentAdmin, DbSession
from app.core.config import settings
from app.schemas import SiteCheckOut, SiteCreate, SiteFetchIn, SiteFetchOut, SiteOut, SitePageOut, SiteUpdate
from app.services.admin_action_log import AdminActionLogDep
from app.services.admin_sites import (
    apply_site_fetch,
    check_admin_site,
    check_admin_sites_batch,
    create_admin_site,
    delete_admin_site,
    fetch_site_meta,
    list_admin_sites,
    update_admin_site,
)
from app.services.file_storage import normalize_image_extension, save_remote_to_uploads, save_upload_bytes

router = APIRouter(prefix="/api/admin/sites", tags=["admin-sites"])


@router.get("", response_model=SitePageOut)
def list_sites(
    _admin: CurrentAdmin,
    db: DbSession,
    q: str | None = None,
    site_category_id: int | None = None,
    tag: str | None = None,
    valid_only: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return list_admin_sites(
        db,
        q=q,
        site_category_id=site_category_id,
        tag=tag,
        valid_only=valid_only,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=SiteOut)
def create_site(audit: AdminActionLogDep, body: SiteCreate, db: DbSession):
    return create_admin_site(db, audit, body)


@router.put("/{sid}", response_model=SiteOut)
def update_site(audit: AdminActionLogDep, sid: int, body: SiteUpdate, db: DbSession):
    return update_admin_site(db, audit, sid, body)


@router.delete("/{sid}")
def delete_site(audit: AdminActionLogDep, sid: int, db: DbSession):
    return delete_admin_site(db, audit, sid)


@router.post("/fetch-meta", response_model=SiteFetchOut)
async def fetch_meta(_admin: CurrentAdmin, body: SiteFetchIn):
    return await fetch_site_meta(body)


@router.post("/{sid}/apply-fetch", response_model=SiteOut)
async def apply_fetch(audit: AdminActionLogDep, sid: int, body: SiteFetchIn, db: DbSession):
    return await apply_site_fetch(db, audit, sid, body)


@router.post("/{sid}/check", response_model=SiteCheckOut)
async def check_one(audit: AdminActionLogDep, sid: int, db: DbSession):
    return await check_admin_site(db, audit, sid)


@router.post("/check-batch", response_model=list[SiteCheckOut])
async def check_batch(
    audit: AdminActionLogDep,
    db: DbSession,
    ids: list[int] = Body(...),
):
    return await check_admin_sites_batch(db, audit, ids)


@router.post("/upload-logo")
async def upload_logo(_admin: CurrentAdmin, file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > settings.upload_max_bytes_logo:
        raise HTTPException(status_code=400, detail="文件过大")
    try:
        suf = normalize_image_extension(file.filename, default=".png")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    rel = await save_upload_bytes("logos", raw, suf)
    return {"path": rel}


@router.post("/upload-favicon-from-url")
async def upload_favicon_from_url(_admin: CurrentAdmin, body: SiteFetchIn):
    path = await save_remote_to_uploads(body.url, "favicons")
    if not path:
        raise HTTPException(status_code=400, detail="下载图标失败")
    return {"path": path}
