"""应用日志：控制台 + 按大小滚动的文件（access / app）。"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.core.config import Settings

_CONFIGURED = False


def setup_logging(settings: Settings) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = settings.log_file_max_bytes
    backup = settings.log_file_backup_count
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        root.addHandler(sh)

    for name, filename in (("navnote.access", "access.log"), ("navnote", "app.log")):
        path = settings.logs_dir / filename
        lg = logging.getLogger(name)
        lg.setLevel(logging.INFO)
        lg.propagate = False
        if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == str(path) for h in lg.handlers):
            fh = RotatingFileHandler(
                path,
                maxBytes=max_bytes,
                backupCount=backup,
                encoding="utf-8",
            )
            fh.setFormatter(fmt)
            lg.addHandler(fh)

    _CONFIGURED = True
