"""数据库方言解析冒烟测试（无需真实数据库）。"""

from __future__ import annotations

from app.core.db_dialect import (
    MYSQL_DRIVER_SCHEMES,
    allows_multi_worker,
    database_url_scheme,
    resolve_database_dialect,
)


def test_resolve_database_dialect() -> None:
    assert resolve_database_dialect("sqlite:///./data/navnote.db") == "sqlite"
    assert resolve_database_dialect("mysql+pymysql://u:p@localhost/db") == "mysql"
    assert resolve_database_dialect("mariadb+pymysql://localhost/db") == "mysql"


def test_allows_multi_worker() -> None:
    assert allows_multi_worker("sqlite:///x") is False
    assert allows_multi_worker("mysql+pymysql://x") is True


def test_mysql_driver_schemes() -> None:
    assert database_url_scheme("mysql+pymysql://localhost/navnote") == "mysql+pymysql"
    assert "mysql+pymysql" in MYSQL_DRIVER_SCHEMES


def main() -> None:
    test_resolve_database_dialect()
    test_allows_multi_worker()
    test_mysql_driver_schemes()
    print("test_mysql_dialect: ok")


if __name__ == "__main__":
    main()
