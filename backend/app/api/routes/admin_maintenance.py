import logging
from datetime import timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, func

from app.api.deps import CurrentAdmin, DbSession
from app.core.config import settings
from app.core.time import utc_now
from app.models import AdminLog, CaptchaChallenge, VisitDailyStat
from app.schemas import (
    AdminLogsCleanupIn,
    AdminLogsCleanupOut,
    CaptchaCleanupOut,
    MaintenanceCountsOut,
    UploadPruneBody,
    UploadPruneResultOut,
    VisitStatsCleanupIn,
    VisitStatsCleanupOut,
)
from app.services.admin_action_log import AdminActionLogDep
from app.services.upload_prune import prune_orphan_uploads
from app.services.visit_stats import delete_stats_before

logger = logging.getLogger("navnote")

router = APIRouter(prefix="/api/admin/maintenance", tags=["admin-maintenance"])


@router.get("/counts", response_model=MaintenanceCountsOut)
def maintenance_counts(_admin: CurrentAdmin, db: DbSession):
    visit_stat_days = db.query(func.count(VisitDailyStat.stat_date)).scalar() or 0
    admin_logs = db.query(func.count(AdminLog.id)).scalar() or 0
    captcha_challenges = db.query(func.count(CaptchaChallenge.id)).scalar() or 0
    return MaintenanceCountsOut(
        visit_stat_days=int(visit_stat_days),
        admin_logs=int(admin_logs),
        captcha_challenges=int(captcha_challenges),
        logs_dir=str(settings.logs_dir),
    )


@router.post("/cleanup/visit-stats", response_model=VisitStatsCleanupOut)
def cleanup_visit_stats(
    audit: AdminActionLogDep,
    body: VisitStatsCleanupIn,
    db: DbSession,
):
    try:
        cutoff = utc_now().date() - timedelta(days=body.older_than_days)
        deleted = delete_stats_before(db, cutoff, commit=False)
        audit.record(
            "maintenance_cleanup_visit_stats",
            resource_type="system",
            detail=f"older_than_days={body.older_than_days}, deleted_days={deleted}",
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("清理访问统计失败")
        raise HTTPException(status_code=500, detail="清理失败，请稍后重试") from exc
    return VisitStatsCleanupOut(visit_stats_deleted=deleted)


@router.post("/cleanup/admin-logs", response_model=AdminLogsCleanupOut)
def cleanup_admin_logs(
    audit: AdminActionLogDep,
    body: AdminLogsCleanupIn,
    db: DbSession,
):
    try:
        cutoff = utc_now() - timedelta(days=body.older_than_days)
        res = db.execute(delete(AdminLog).where(AdminLog.created_at < cutoff))
        deleted = int(res.rowcount or 0)
        audit.record(
            "maintenance_cleanup_admin_logs",
            resource_type="system",
            detail=f"older_than_days={body.older_than_days}, deleted={deleted}",
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("清理操作日志失败")
        raise HTTPException(status_code=500, detail="清理失败，请稍后重试") from exc
    return AdminLogsCleanupOut(admin_logs_deleted=deleted)


@router.post("/cleanup/captcha", response_model=CaptchaCleanupOut)
def cleanup_captcha(audit: AdminActionLogDep, db: DbSession):
    try:
        now = utc_now()
        res = db.execute(delete(CaptchaChallenge).where(CaptchaChallenge.expires_at < now))
        deleted = int(res.rowcount or 0)
        audit.record(
            "maintenance_cleanup_captcha",
            resource_type="system",
            detail=f"captcha_deleted={deleted}",
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("清理验证码记录失败")
        raise HTTPException(status_code=500, detail="清理失败，请稍后重试") from exc
    return CaptchaCleanupOut(captcha_deleted=deleted)


@router.get("/upload-orphans", response_model=UploadPruneResultOut)
def upload_orphans_preview(_admin: CurrentAdmin, db: DbSession):
    r = prune_orphan_uploads(db, execute=False)
    return UploadPruneResultOut(**r)


@router.post("/prune-uploads", response_model=UploadPruneResultOut)
def prune_uploads(
    audit: AdminActionLogDep,
    body: UploadPruneBody,
    db: DbSession,
):
    if body.execute and not body.confirm_delete:
        raise HTTPException(status_code=400, detail="请确认 confirm_delete=true")
    r = prune_orphan_uploads(db, execute=body.execute)
    if body.execute:
        audit.record(
            "upload_prune",
            resource_type="system",
            detail=f"deleted={r['deleted_count']}, freed_bytes={r['freed_bytes']}",
        )
        db.commit()
    return UploadPruneResultOut(**r)
