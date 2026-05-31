from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentAdmin, DbSession
from app.models import Site, SiteCategory
from app.schemas import SiteCategoryCreate, SiteCategoryOut, SiteCategoryPageOut, SiteCategoryUpdate
from app.services.admin_action_log import AdminActionLogDep

router = APIRouter(prefix="/api/admin/site-categories", tags=["admin-site-categories"])


def _uncategorized(db: Session) -> SiteCategory:
    c = db.query(SiteCategory).filter(SiteCategory.is_system.is_(True)).first()
    if not c:
        raise HTTPException(status_code=500, detail="系统未初始化未分类")
    return c


@router.get("", response_model=SiteCategoryPageOut)
def list_site_categories(
    _admin: CurrentAdmin,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
):
    stmt = db.query(SiteCategory).order_by(SiteCategory.sort_order.asc(), SiteCategory.id.asc())
    total = stmt.count()
    rows = stmt.offset((page - 1) * page_size).limit(page_size).all()
    return SiteCategoryPageOut(items=rows, total=total, page=page, page_size=page_size)


@router.post("", response_model=SiteCategoryOut)
def create_site_category(
    audit: AdminActionLogDep,
    body: SiteCategoryCreate,
    db: DbSession,
):
    row = SiteCategory(
        name=body.name,
        icon_key=body.icon_key,
        description=body.description,
        sort_order=body.sort_order,
        enabled=body.enabled,
        is_system=False,
    )
    db.add(row)
    db.flush()
    audit.record(
        "site_category_create",
        resource_type="site_category",
        resource_id=str(row.id),
        detail=body.name,
    )
    db.commit()
    db.refresh(row)
    return row


@router.put("/{cid}", response_model=SiteCategoryOut)
def update_site_category(
    audit: AdminActionLogDep,
    cid: int,
    body: SiteCategoryUpdate,
    db: DbSession,
):
    row = db.get(SiteCategory, cid)
    if not row:
        raise HTTPException(status_code=404, detail="分类不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    audit.record("site_category_update", resource_type="site_category", resource_id=str(cid))
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{cid}")
def delete_site_category(audit: AdminActionLogDep, cid: int, db: DbSession):
    row = db.get(SiteCategory, cid)
    if not row:
        raise HTTPException(status_code=404, detail="分类不存在")
    if row.is_system:
        raise HTTPException(status_code=400, detail="系统分类不可删除")
    unc = _uncategorized(db)
    db.query(Site).filter(Site.site_category_id == cid).update({Site.site_category_id: unc.id})
    db.delete(row)
    audit.record("site_category_delete", resource_type="site_category", resource_id=str(cid))
    db.commit()
    return {"ok": True}
