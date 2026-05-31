"""数据库连接串解析与方言判断（SQLite / MySQL / MariaDB）。"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

logger = logging.getLogger("navnote")

MYSQL_DRIVER_SCHEMES = frozenset({"mysql+pymysql", "mariadb+pymysql"})


def allows_multi_worker(database_url: str) -> bool:
    """SQLite 不支持多进程 Worker；MySQL/MariaDB 等支持。"""
    return resolve_database_dialect(database_url) != "sqlite"


def resolve_database_dialect(database_url: str) -> str:
    u = database_url.strip().lower()
    if u.startswith("sqlite"):
        return "sqlite"
    if u.startswith("mysql") or u.startswith("mariadb"):
        return "mysql"
    if u.startswith("postgresql") or u.startswith("postgres"):
        return "postgresql"
    return u.split(":", 1)[0].split("+", 1)[0]


def database_url_scheme(database_url: str) -> str:
    parsed = urlparse(database_url.strip())
    return (parsed.scheme or "").lower()


def check_database_url(database_url: str, *, debug: bool) -> None:
    scheme = database_url_scheme(database_url)
    dialect = resolve_database_dialect(database_url)

    if dialect == "sqlite":
        logger.info("当前为 SQLite：仅单进程；多 Worker 请改用 MySQL。")

    if dialect == "mysql":
        if scheme not in MYSQL_DRIVER_SCHEMES:
            logger.warning(
                "MySQL/MariaDB 建议使用 mysql+pymysql:// 或 mariadb+pymysql:// 连接串（已安装 pymysql）；"
                "当前 scheme=%s，若启动报驱动错误请按 backend/.env.example 修改。",
                scheme or "(空)",
            )
        if "charset=" not in database_url.lower():
            logger.warning(
                "MySQL 连接串建议附带 charset=utf8mb4（示例见 backend/.env.example），避免中文乱码。"
            )
