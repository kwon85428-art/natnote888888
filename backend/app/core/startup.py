"""应用启动时的目录初始化与配置校验。"""

from __future__ import annotations

import logging
import sys

from app.core.config import Settings
from app.core.db_dialect import check_database_url

logger = logging.getLogger("navnote")

_DEFAULT_SECRET = "change-me-in-production-use-long-random-string"
_UPLOAD_SUBDIRS = ("logos", "favicons", "covers", "platform", "article-content")


def ensure_runtime_dirs(settings: Settings) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    for sub in _UPLOAD_SUBDIRS:
        (settings.upload_dir / sub).mkdir(parents=True, exist_ok=True)


def validate_settings(settings: Settings) -> None:
    if settings.debug:
        return
    if settings.secret_key.strip() == _DEFAULT_SECRET:
        logger.error("生产环境必须设置非默认 SECRET_KEY（见 backend/.env.example）")
        sys.exit(1)
    check_database_url(settings.database_url, debug=settings.debug)
