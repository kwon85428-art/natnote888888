"""UTC 时间工具（数据库存储为 naive UTC，与历史数据兼容）。"""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
