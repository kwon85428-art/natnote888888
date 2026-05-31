"""访问与安全相关事件写入 access 日志文件（不入库）。"""

from __future__ import annotations

import logging

_access = logging.getLogger("navnote.access")


def log_page_view() -> None:
    _access.info("event=page_view")


def log_site_click(site_id: int) -> None:
    _access.info("event=site_click site_id=%s", site_id)


def log_article_view(article_id: int) -> None:
    _access.info("event=article_view article_id=%s", article_id)


def log_login_failed(username: str, *, ip: str | None, reason: str) -> None:
    _access.info(
        "event=login_failed username=%s ip=%s reason=%s",
        username,
        ip or "-",
        reason,
    )


def log_captcha_failed(*, ip: str | None) -> None:
    _access.info("event=captcha_failed ip=%s", ip or "-")
