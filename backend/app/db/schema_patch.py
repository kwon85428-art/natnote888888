"""轻量 schema 补丁：create_all 不修改已有表时，补列、迁移旧字段并清理废弃结构。"""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.session import engine

logger = logging.getLogger("navnote")

_PLATFORM_BOOL_COLUMNS: tuple[tuple[str, bool], ...] = (
    ("show_promoted_sites_on_sites", True),
    ("show_promoted_articles_on_sites", True),
    ("show_promoted_sites_on_articles", False),
    ("show_promoted_articles_on_articles", True),
    ("public_sites_enabled", True),
    ("public_articles_enabled", True),
)

_PLATFORM_STRING_COLUMNS: tuple[tuple[str, str, str, bool], ...] = (
    ("default_home", "sites", "VARCHAR(16)", False),
    ("menu_sites_label", "网址", "VARCHAR(32)", False),
    ("menu_articles_label", "文章", "VARCHAR(32)", False),
    ("icp_text", "", "VARCHAR(128)", True),
    ("icp_link_url", "", "VARCHAR(512)", True),
)

_ADMIN_LEGACY_COLUMNS = ("reset_token", "reset_token_expires")
_LEGACY_TABLES = ("categories", "visit_logs")
_TABLES_WITH_LOGICAL_FKS = ("sites", "articles", "admin_logs")


def _bool_default_sql(default: bool) -> str:
    return "1" if default else "0"


def _add_bool_column(conn, dialect: str, table: str, column: str, default: bool) -> None:
    bit = _bool_default_sql(default)
    if dialect == "mysql":
        sql = f"ALTER TABLE {table} ADD COLUMN {column} TINYINT(1) NOT NULL DEFAULT {bit}"
    else:
        sql = f"ALTER TABLE {table} ADD COLUMN {column} BOOLEAN NOT NULL DEFAULT {bit}"
    conn.execute(text(sql))


def _add_string_column(
    conn,
    dialect: str,
    table: str,
    column: str,
    col_type: str,
    default: str,
    *,
    nullable: bool,
) -> None:
    safe_default = default.replace("'", "''")
    if dialect == "mysql":
        null_sql = "NULL" if nullable else "NOT NULL"
        default_sql = f"DEFAULT '{safe_default}'" if not nullable or default else "DEFAULT NULL"
        if nullable and not default:
            default_sql = "DEFAULT NULL"
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type} {null_sql} {default_sql}"
    elif nullable:
        sql = f"ALTER TABLE {table} ADD COLUMN {column} TEXT"
    else:
        sql = f"ALTER TABLE {table} ADD COLUMN {column} TEXT NOT NULL DEFAULT '{safe_default}'"
    conn.execute(text(sql))


def _quote_table(dialect: str, table: str) -> str:
    return f"`{table}`" if dialect == "mysql" else f'"{table}"'


def patch_admins_drop_legacy_columns() -> None:
    insp = inspect(engine)
    if not insp.has_table("admins"):
        return
    existing = {c["name"] for c in insp.get_columns("admins")}
    to_drop = [c for c in _ADMIN_LEGACY_COLUMNS if c in existing]
    if not to_drop:
        return
    with engine.begin() as conn:
        for column in to_drop:
            try:
                conn.execute(text(f"ALTER TABLE admins DROP COLUMN {column}"))
                logger.info("已删除旧列 admins.%s", column)
            except Exception:
                logger.exception("删除旧列失败: admins.%s", column)


def patch_platform_settings_columns() -> None:
    insp = inspect(engine)
    if not insp.has_table("platform_settings"):
        return
    existing = {c["name"] for c in insp.get_columns("platform_settings")}
    dialect = settings.database_dialect
    had_show_home_articles = "show_home_articles" in existing
    with engine.begin() as conn:
        for column, default in _PLATFORM_BOOL_COLUMNS:
            if column in existing:
                continue
            try:
                _add_bool_column(conn, dialect, "platform_settings", column, default)
                logger.info("已补列 platform_settings.%s", column)
            except Exception:
                logger.exception("补列失败: platform_settings.%s", column)
        for column, default, col_type, nullable in _PLATFORM_STRING_COLUMNS:
            if column in existing:
                continue
            try:
                _add_string_column(
                    conn, dialect, "platform_settings", column, col_type, default, nullable=nullable
                )
                logger.info("已补列 platform_settings.%s", column)
            except Exception:
                logger.exception("补列失败: platform_settings.%s", column)
        if had_show_home_articles:
            try:
                conn.execute(
                    text(
                        "UPDATE platform_settings "
                        "SET show_promoted_articles_on_sites = show_home_articles"
                    )
                )
            except Exception:
                logger.exception("迁移 show_home_articles 失败")


def patch_article_categories_columns() -> None:
    insp = inspect(engine)
    if not insp.has_table("article_categories"):
        return
    existing = {c["name"] for c in insp.get_columns("article_categories")}
    dialect = settings.database_dialect
    with engine.begin() as conn:
        if "description" not in existing:
            try:
                sql = (
                    "ALTER TABLE article_categories ADD COLUMN description TEXT NULL"
                    if dialect == "mysql"
                    else "ALTER TABLE article_categories ADD COLUMN description TEXT"
                )
                conn.execute(text(sql))
                logger.info("已补列 article_categories.description")
            except Exception:
                logger.exception("补列失败: article_categories.description")
        if "sort_order" not in existing:
            try:
                sql = (
                    "ALTER TABLE article_categories ADD COLUMN sort_order INT NOT NULL DEFAULT 0"
                    if dialect == "mysql"
                    else "ALTER TABLE article_categories ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
                )
                conn.execute(text(sql))
                logger.info("已补列 article_categories.sort_order")
            except Exception:
                logger.exception("补列失败: article_categories.sort_order")


def _sqlite_column_ddl(col: dict, *, pk_cols: list[str]) -> str:
    name = col["name"]
    parts = [f'"{name}"', str(col["type"])]
    if not col.get("nullable", True):
        parts.append("NOT NULL")
    default = col.get("default")
    if default is not None:
        parts.append(f"DEFAULT {default}" if isinstance(default, str) else f"DEFAULT {default!r}")
    if name in pk_cols and len(pk_cols) == 1:
        parts.append("PRIMARY KEY")
        if col.get("autoincrement"):
            parts.append("AUTOINCREMENT")
    return " ".join(parts)


def _sqlite_recreate_table_without_fks(conn, table: str) -> None:
    insp = inspect(engine)
    if not insp.get_foreign_keys(table):
        return
    cols = insp.get_columns(table)
    pk_cols = list(insp.get_pk_constraint(table).get("constrained_columns") or [])
    indexes = insp.get_indexes(table)
    col_defs = [_sqlite_column_ddl(c, pk_cols=pk_cols) for c in cols]
    if len(pk_cols) > 1:
        pk_sql = ", ".join(f'"{c}"' for c in pk_cols)
        col_defs.append(f"PRIMARY KEY ({pk_sql})")
    temp = f"_navnote_{table}_new"
    quoted_temp, quoted_table = f'"{temp}"', f'"{table}"'
    col_names = ", ".join(f'"{c["name"]}"' for c in cols)
    conn.execute(text("PRAGMA foreign_keys=OFF"))
    conn.execute(text(f"CREATE TABLE {quoted_temp} ({', '.join(col_defs)})"))
    conn.execute(text(f"INSERT INTO {quoted_temp} SELECT {col_names} FROM {quoted_table}"))
    conn.execute(text(f"DROP TABLE {quoted_table}"))
    conn.execute(text(f"ALTER TABLE {quoted_temp} RENAME TO {quoted_table}"))
    for idx in indexes:
        idx_name = idx.get("name")
        idx_cols = idx.get("column_names") or []
        if not idx_name or not idx_cols:
            continue
        cols_sql = ", ".join(f'"{c}"' for c in idx_cols)
        unique = "UNIQUE " if idx.get("unique") else ""
        conn.execute(text(f'CREATE {unique}INDEX "{idx_name}" ON {quoted_table} ({cols_sql})'))
    logger.info("已重建 SQLite 表 %s（移除物理外键）", table)


def _drop_mysql_foreign_keys(conn, table: str) -> None:
    quoted = _quote_table("mysql", table)
    for fk in inspect(engine).get_foreign_keys(table):
        name = fk.get("name")
        if name:
            conn.execute(text(f"ALTER TABLE {quoted} DROP FOREIGN KEY `{name}`"))
            logger.info("已删除外键 %s.%s", table, name)


def patch_drop_foreign_key_constraints() -> None:
    insp = inspect(engine)
    dialect = settings.database_dialect
    tables = [t for t in _TABLES_WITH_LOGICAL_FKS if insp.has_table(t)]
    if not tables:
        return
    with engine.begin() as conn:
        for table in tables:
            if not insp.get_foreign_keys(table):
                continue
            try:
                if dialect == "mysql":
                    _drop_mysql_foreign_keys(conn, table)
                elif dialect == "sqlite":
                    _sqlite_recreate_table_without_fks(conn, table)
                else:
                    logger.warning("未实现 %s 方言的外键清理: %s", dialect, table)
            except Exception:
                logger.exception("删除外键失败: %s", table)


def patch_drop_legacy_tables() -> None:
    insp = inspect(engine)
    dialect = settings.database_dialect
    with engine.begin() as conn:
        for table in _LEGACY_TABLES:
            if not insp.has_table(table):
                continue
            try:
                conn.execute(text(f"DROP TABLE {_quote_table(dialect, table)}"))
                logger.info("已删除旧表 %s", table)
            except Exception:
                logger.exception("删除旧表失败: %s", table)


def apply_schema_patches() -> None:
    patch_drop_foreign_key_constraints()
    patch_drop_legacy_tables()
    patch_admins_drop_legacy_columns()
    patch_platform_settings_columns()
    patch_article_categories_columns()
