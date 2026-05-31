"""管理端文章 CRUD 与校验。"""

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import Article, ArticleCategory, ContentType
from app.schemas import ArticleCreate, ArticleOut, ArticlePageOut, ArticleUpdate
from app.services.admin_action_log import AdminActionLog
from app.services.ordering import article_order


def pinned_count(db: Session, exclude_id: int | None = None) -> int:
    q = db.query(Article).filter(Article.is_pinned.is_(True))
    if exclude_id is not None:
        q = q.filter(Article.id != exclude_id)
    return q.count()


def ensure_pin_allowed(db: Session, want_pin: bool, exclude_id: int | None = None) -> None:
    if not want_pin:
        return
    if pinned_count(db, exclude_id) >= 3:
        raise HTTPException(status_code=400, detail="最多置顶 3 条文章")


def validate_article_body(content_type: str, body_markdown: str | None, body_html: str | None) -> None:
    if content_type == ContentType.original.value:
        has_md = bool((body_markdown or "").strip())
        has_html = bool((body_html or "").strip())
        if not has_md and not has_html:
            raise HTTPException(status_code=400, detail="原创文章需要 Markdown 正文或 HTML 正文")


def list_admin_articles(
    db: Session,
    *,
    q: str | None = None,
    article_category_id: int | None = None,
    content_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> ArticlePageOut:
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 20), 100))
    stmt = db.query(Article).options(joinedload(Article.article_category))
    if q:
        stmt = stmt.filter(Article.title.contains(q))
    if article_category_id is not None:
        stmt = stmt.filter(Article.article_category_id == article_category_id)
    if content_type:
        stmt = stmt.filter(Article.content_type == content_type)
    total = stmt.count()
    rows = (
        stmt.order_by(*article_order())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ArticlePageOut(items=rows, total=total, page=page, page_size=page_size)


def create_admin_article(db: Session, audit: AdminActionLog, body: ArticleCreate) -> ArticleOut:
    if not db.get(ArticleCategory, body.article_category_id):
        raise HTTPException(status_code=400, detail="文章分类不存在")
    validate_article_body(body.content_type, body.body_markdown, body.body_html)
    if body.content_type == ContentType.external.value and not (body.source_url or "").strip():
        raise HTTPException(status_code=400, detail="外部文章需要原文链接")
    ensure_pin_allowed(db, body.is_pinned)
    row = Article(
        title=body.title,
        summary=body.summary,
        article_category_id=body.article_category_id,
        tags=body.tags,
        published_at=body.published_at,
        cover_path=body.cover_path,
        source_url=body.source_url,
        content_type=body.content_type,
        body_html=body.body_html,
        body_markdown=body.body_markdown,
        is_pinned=body.is_pinned,
        pin_order=body.pin_order,
        is_promoted=body.is_promoted,
        visit_count=0,
    )
    db.add(row)
    db.flush()
    audit.record("article_create", resource_type="article", resource_id=str(row.id), detail=body.title)
    db.commit()
    db.refresh(row)
    return row


def update_admin_article(db: Session, audit: AdminActionLog, aid: int, body: ArticleUpdate) -> ArticleOut:
    row = db.get(Article, aid)
    if not row:
        raise HTTPException(status_code=404, detail="文章不存在")
    data = body.model_dump(exclude_unset=True)
    will_pin = data.get("is_pinned", row.is_pinned)
    if will_pin:
        ensure_pin_allowed(db, True, exclude_id=aid)
    if "article_category_id" in data and data["article_category_id"] is not None:
        if not db.get(ArticleCategory, data["article_category_id"]):
            raise HTTPException(status_code=400, detail="文章分类不存在")
    new_ct = data.get("content_type", row.content_type)
    new_md = data["body_markdown"] if "body_markdown" in data else row.body_markdown
    new_html = data["body_html"] if "body_html" in data else row.body_html
    validate_article_body(new_ct, new_md, new_html)
    for k, v in data.items():
        setattr(row, k, v)
    audit.record("article_update", resource_type="article", resource_id=str(aid))
    db.commit()
    db.refresh(row)
    return row


def delete_admin_article(db: Session, audit: AdminActionLog, aid: int) -> dict:
    row = db.get(Article, aid)
    if not row:
        raise HTTPException(status_code=404, detail="文章不存在")
    db.delete(row)
    audit.record("article_delete", resource_type="article", resource_id=str(aid))
    db.commit()
    return {"ok": True}
