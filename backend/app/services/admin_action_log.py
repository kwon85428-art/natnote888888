from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import CurrentAdmin, DbSession
from app.models import Admin
from app.services.admin_log import write_admin_log
from app.services.request_context import client_ip


class AdminActionLog:
    __slots__ = ("_db", "_admin", "_request")

    def __init__(self, db: Session, admin: Admin, request: Request) -> None:
        self._db = db
        self._admin = admin
        self._request = request

    @property
    def admin(self) -> Admin:
        return self._admin

    def record(
        self,
        action: str,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        detail: str | None = None,
    ) -> None:
        write_admin_log(
            self._db,
            admin_id=self._admin.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip=client_ip(self._request),
            commit=False,
        )


def get_admin_action_log(
    admin: CurrentAdmin,
    request: Request,
    db: DbSession,
) -> AdminActionLog:
    return AdminActionLog(db, admin, request)


AdminActionLogDep = Annotated[AdminActionLog, Depends(get_admin_action_log)]
