from pydantic import BaseModel, Field


class MaintenanceCountsOut(BaseModel):
    visit_stat_days: int
    admin_logs: int
    captcha_challenges: int
    logs_dir: str = Field(description="滚动日志目录（相对 backend 或绝对路径）")


class VisitStatsCleanupIn(BaseModel):
    older_than_days: int = Field(..., ge=1, le=3650, description="删除早于此天数的按日 PV 汇总")


class AdminLogsCleanupIn(BaseModel):
    older_than_days: int = Field(..., ge=1, le=3650, description="删除早于此天数的管理操作日志")


class VisitStatsCleanupOut(BaseModel):
    visit_stats_deleted: int


class AdminLogsCleanupOut(BaseModel):
    admin_logs_deleted: int


class CaptchaCleanupOut(BaseModel):
    captcha_deleted: int


class UploadPruneBody(BaseModel):
    execute: bool = False
    confirm_delete: bool = False


class UploadPruneResultOut(BaseModel):
    dry_run: bool
    orphan_count: int
    total_bytes: int
    deleted_count: int
    freed_bytes: int
    sample_paths: list[str]
