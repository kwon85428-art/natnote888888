"""公开文章接口业务逻辑。"""

from fastapi import HTTPException
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.core.url_safe import is_safe_http_url
from app.models import Article, ArticleCategory, ContentType
from app.schemas import ArticleOut, ArticleSummaryOut, ArticleSummaryPageOut
from app.services.access_log import log_article_view
from app.services.markdown import markdown_to_html
from app.services.ordering import article_order
from app.services.stats_buffer import record_article_visit_buffered


def _get_public_article(db: Session, aid: int) -> Article | None:
    return (
        db.query(Article)
        .join(ArticleCategory, Article.article_category_id == ArticleCategory.id)
        .options(contains_eager(Article.article_category))
        .filter(Article.id == aid, ArticleCategory.enabled.is_(True))
        .first()
    )


def list_public_article_categories(db: Session) -> list[dict]:
    rows = (
        db.query(ArticleCategory)
        .filter(ArticleCategory.enabled.is_(True))
        .order_by(ArticleCategory.sort_order.asc(), ArticleCategory.id.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "icon_key": r.icon_key,
        }
        for r in rows
    ]


def paginate_public_articles(
    db: Session,
    *,
    article_category_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> ArticleSummaryPageOut:
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 10), 50))
    stmt = (
        db.query(Article)
        .join(ArticleCategory, Article.article_category_id == ArticleCategory.id)
        .options(contains_eager(Article.article_category))
        .filter(ArticleCategory.enabled.is_(True))
    )
    if article_category_id is not None:
        stmt = stmt.filter(Article.article_category_id == article_category_id)
    stmt = stmt.order_by(*article_order())
    total = stmt.count()
    rows = stmt.offset((page - 1) * page_size).limit(page_size).all()
    return ArticleSummaryPageOut(
        items=[ArticleSummaryOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


def list_public_articles_promoted(db: Session, limit: int = 12) -> list[ArticleSummaryOut]:
    lim = max(1, min(int(limit or 12), 48))
    rows = (
        db.query(Article)
        .options(joinedload(Article.article_category))
        .join(ArticleCategory, Article.article_category_id == ArticleCategory.id)
        .filter(ArticleCategory.enabled.is_(True), Article.is_promoted.is_(True))
        .order_by(*article_order())
        .limit(lim)
        .all()
    )
    return [ArticleSummaryOut.model_validate(r) for r in rows]


def get_public_article_detail(db: Session, aid: int) -> ArticleOut:
    row = _get_public_article(db, aid)
    if not row:
        raise HTTPException(status_code=404, detail="文章不存在")
    record_article_visit_buffered(row.id)
    log_article_view(row.id)
    return row


def resolve_public_read_payload(db: Session, aid: int) -> dict:
    row = _get_public_article(db, aid)
    if not row:
        raise HTTPException(status_code=404, detail="文章不存在")
    if row.content_type == ContentType.external.value:
        url = (row.source_url or "").strip()
        if url and is_safe_http_url(url):
            return {"mode": "redirect", "url": url}
        return {"mode": "inline", "body_html": ""}
    md = (row.body_markdown or "").strip()
    if md:
        return {"mode": "inline", "body_html": markdown_to_html(row.body_markdown or "")}
    return {"mode": "inline", "body_html": row.body_html or ""}
