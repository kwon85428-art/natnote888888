from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentAdmin, DbSession
from app.models import Article, ArticleCategory
from app.schemas import ArticleCategoryCreate, ArticleCategoryOut, ArticleCategoryPageOut, ArticleCategoryUpdate
from app.services.admin_action_log import AdminActionLogDep

router = APIRouter(prefix="/api/admin/article-categories", tags=["admin-article-categories"])


@router.get("", response_model=ArticleCategoryPageOut)
def list_article_categories(
    _admin: CurrentAdmin,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
):
    stmt = db.query(ArticleCategory).order_by(ArticleCategory.sort_order.asc(), ArticleCategory.id.asc())
    total = stmt.count()
    rows = stmt.offset((page - 1) * page_size).limit(page_size).all()
    return ArticleCategoryPageOut(items=rows, total=total, page=page, page_size=page_size)


@router.post("", response_model=ArticleCategoryOut)
def create_article_category(audit: AdminActionLogDep, body: ArticleCategoryCreate, db: DbSession):
    row = ArticleCategory(
        name=body.name,
        icon_key=body.icon_key,
        description=body.description,
        sort_order=body.sort_order,
        enabled=body.enabled,
    )
    db.add(row)
    db.flush()
    audit.record("article_category_create", resource_type="article_category", resource_id=str(row.id))
    db.commit()
    db.refresh(row)
    return row


@router.put("/{cid}", response_model=ArticleCategoryOut)
def update_article_category(audit: AdminActionLogDep, cid: int, body: ArticleCategoryUpdate, db: DbSession):
    row = db.get(ArticleCategory, cid)
    if not row:
        raise HTTPException(status_code=404, detail="文章分类不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    audit.record("article_category_update", resource_type="article_category", resource_id=str(cid))
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{cid}")
def delete_article_category(audit: AdminActionLogDep, cid: int, db: DbSession):
    row = db.get(ArticleCategory, cid)
    if not row:
        raise HTTPException(status_code=404, detail="文章分类不存在")
    if db.query(Article).filter(Article.article_category_id == cid).count() > 0:
        raise HTTPException(status_code=400, detail="分类下仍有文章，无法删除")
    db.delete(row)
    audit.record("article_category_delete", resource_type="article_category", resource_id=str(cid))
    db.commit()
    return {"ok": True}
