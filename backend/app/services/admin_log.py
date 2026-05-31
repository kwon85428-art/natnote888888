from sqlalchemy.orm import Session

from app.models import AdminLog


def write_admin_log(
    db: Session,
    *,
    admin_id: int | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    detail: str | None = None,
    ip: str | None = None,
    commit: bool = False,
) -> None:
    """写入一条管理操作日志；默认与业务变更同一事务 commit。"""
    db.add(
        AdminLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip=ip,
        )
    )
    if commit:
        db.commit()
