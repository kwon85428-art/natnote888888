"""管理端操作审计日志。"""

from datetime import datetime

from fastapi import APIRouter, Query

from app.api.deps import CurrentAdmin, DbSession
from app.models import Admin, AdminLog
from app.schemas import AdminLogOut, AdminLogPageOut

router = APIRouter(prefix="/api/admin", tags=["admin-logs"])


def _admin_usernames(db: DbSession, admin_ids: set[int]) -> dict[int, str]:
    if not admin_ids:
        return {}
    rows = db.query(Admin.id, Admin.username).filter(Admin.id.in_(admin_ids)).all()
    return {int(i): u for i, u in rows}


@router.get("/logs", response_model=AdminLogPageOut)
def list_logs(
    _admin: CurrentAdmin,
    db: DbSession,
    action: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    q = db.query(AdminLog)
    if action:
        q = q.filter(AdminLog.action == action)
    if from_ts:
        q = q.filter(AdminLog.created_at >= from_ts)
    if to_ts:
        q = q.filter(AdminLog.created_at <= to_ts)
    total = q.count()
    rows = (
        q.order_by(AdminLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    names = _admin_usernames(db, {r.admin_id for r in rows if r.admin_id})
    items = [
        AdminLogOut.model_validate(row).model_copy(
            update={"admin_username": names.get(row.admin_id) if row.admin_id else None}
        )
        for row in rows
    ]
    return AdminLogPageOut(items=items, total=total, page=page, page_size=page_size)
