from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.api.deps import CurrentAdmin, DbSession
from app.core.config import settings
from app.schemas import ArticleCreate, ArticleOut, ArticlePageOut, ArticleUpdate
from app.services.admin_action_log import AdminActionLogDep
from app.services.admin_articles import (
    create_admin_article,
    delete_admin_article,
    list_admin_articles,
    update_admin_article,
)
from app.services.file_storage import normalize_image_extension, save_upload_bytes

router = APIRouter(prefix="/api/admin/articles", tags=["admin-articles"])


@router.get("", response_model=ArticlePageOut)
def list_articles(
    _admin: CurrentAdmin,
    db: DbSession,
    q: str | None = None,
    article_category_id: int | None = None,
    content_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return list_admin_articles(
        db,
        q=q,
        article_category_id=article_category_id,
        content_type=content_type,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ArticleOut)
def create_article(audit: AdminActionLogDep, body: ArticleCreate, db: DbSession):
    return create_admin_article(db, audit, body)


@router.put("/{aid}", response_model=ArticleOut)
def update_article(audit: AdminActionLogDep, aid: int, body: ArticleUpdate, db: DbSession):
    return update_admin_article(db, audit, aid, body)


@router.delete("/{aid}")
def delete_article(audit: AdminActionLogDep, aid: int, db: DbSession):
    return delete_admin_article(db, audit, aid)


@router.post("/upload-cover")
async def upload_cover(_admin: CurrentAdmin, file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > settings.upload_max_bytes_cover:
        raise HTTPException(status_code=400, detail="文件过大")
    try:
        suf = normalize_image_extension(file.filename, default=".jpg")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    rel = await save_upload_bytes("covers", raw, suf)
    return {"path": rel}


@router.post("/upload-body-image")
async def upload_body_image(_admin: CurrentAdmin, file: UploadFile = File(...)):
    """正文 Markdown 内嵌图片，与封面分目录存放。"""
    raw = await file.read()
    if len(raw) > settings.upload_max_bytes_article_body:
        raise HTTPException(status_code=400, detail="文件过大")
    try:
        suf = normalize_image_extension(file.filename, default=".png")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    rel = await save_upload_bytes("article-content", raw, suf)
    return {"path": rel}
