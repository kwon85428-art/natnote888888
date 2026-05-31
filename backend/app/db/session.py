from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base

__all__ = ["Base", "engine", "SessionLocal", "get_db", "make_engine"]


def make_engine(database_url: str | None = None):
    url = database_url or settings.database_url
    kwargs: dict = {"pool_pre_ping": True}
    u = url.lower()
    if u.startswith("sqlite"):
        # timeout：sqlite3 busy_timeout（秒），多进程/热重载时避免无限阻塞
        kwargs["connect_args"] = {"check_same_thread": False, "timeout": 10}
    elif u.startswith("mysql") or u.startswith("mariadb"):
        # 避免 MySQL wait_timeout 导致的长连接失效
        kwargs["pool_recycle"] = 3600
    return create_engine(url, **kwargs)


def _register_sqlite_pragmas(db_engine) -> None:
    if db_engine.dialect.name != "sqlite":
        return

    @event.listens_for(db_engine, "connect")
    def _sqlite_disable_foreign_keys(dbapi_connection, _connection_record) -> None:
        """不启用 SQLite 物理外键检查；关联由应用层逻辑维护。"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()


engine = make_engine()
_register_sqlite_pragmas(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
