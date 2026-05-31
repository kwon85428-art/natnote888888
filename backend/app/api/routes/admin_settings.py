from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import CurrentAdmin, DbSession
from app.core.config import settings
from app.schemas import PlatformSettingsOut, PlatformSettingsUpdate
from app.services.admin_action_log import AdminActionLogDep
from app.services.file_storage import normalize_image_extension, save_upload_bytes
from app.services.platform_settings import get_or_create_platform_settings

router = APIRouter(prefix="/api/admin/settings", tags=["admin-settings"])


@router.get("/platform", response_model=PlatformSettingsOut)
def get_platform(_admin: CurrentAdmin, db: DbSession):
    return get_or_create_platform_settings(db)


@router.put("/platform", response_model=PlatformSettingsOut)
def put_platform(
    audit: AdminActionLogDep,
    body: PlatformSettingsUpdate,
    db: DbSession,
):
    row = get_or_create_platform_settings(db)
    if body.platform_name is not None:
        row.platform_name = body.platform_name
    if body.footer_text is not None:
        row.footer_text = body.footer_text
    if body.contact_info is not None:
        row.contact_info = body.contact_info
    if body.icp_text is not None:
        row.icp_text = body.icp_text
    if body.icp_link_url is not None:
        row.icp_link_url = body.icp_link_url
    if body.show_promoted_sites_on_sites is not None:
        row.show_promoted_sites_on_sites = body.show_promoted_sites_on_sites
    if body.show_promoted_articles_on_sites is not None:
        row.show_promoted_articles_on_sites = body.show_promoted_articles_on_sites
    if body.show_promoted_sites_on_articles is not None:
        row.show_promoted_sites_on_articles = body.show_promoted_sites_on_articles
    if body.show_promoted_articles_on_articles is not None:
        row.show_promoted_articles_on_articles = body.show_promoted_articles_on_articles
    if body.public_sites_enabled is not None:
        row.public_sites_enabled = body.public_sites_enabled
    if body.public_articles_enabled is not None:
        row.public_articles_enabled = body.public_articles_enabled
    if body.default_home is not None:
        row.default_home = body.default_home
    if body.menu_sites_label is not None:
        row.menu_sites_label = body.menu_sites_label.strip()
    if body.menu_articles_label is not None:
        row.menu_articles_label = body.menu_articles_label.strip()

    if not row.public_sites_enabled and not row.public_articles_enabled:
        raise HTTPException(status_code=400, detail="网址与文章模块不能同时关闭，请至少保留一项。")
    if row.default_home == "articles" and not row.public_articles_enabled:
        row.default_home = "sites"
    if row.default_home == "sites" and not row.public_sites_enabled:
        row.default_home = "articles"

    audit.record("settings_update", resource_type="platform", detail="platform")
    db.commit()
    db.refresh(row)
    return row


@router.post("/platform/logo")
async def upload_platform_logo(audit: AdminActionLogDep, db: DbSession, file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > settings.upload_max_bytes_logo:
        raise HTTPException(status_code=400, detail="文件过大")
    try:
        suf = normalize_image_extension(file.filename, default=".png")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    rel = await save_upload_bytes("platform", raw, suf)
    row = get_or_create_platform_settings(db)
    row.logo_path = rel
    audit.record("settings_logo", resource_type="platform")
    db.commit()
    return {"path": rel}
