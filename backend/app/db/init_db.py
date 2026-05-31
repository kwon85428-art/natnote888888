import logging

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.schema_patch import apply_schema_patches
from app.db.session import SessionLocal, engine
from app.models.tables import Admin, ArticleCategory, PlatformSettings, SiteCategory

logger = logging.getLogger("navnote")


def init_models() -> None:
    Base.metadata.create_all(bind=engine)
    apply_schema_patches()


def seed_if_empty() -> None:
    db = SessionLocal()
    try:
        if db.query(PlatformSettings).first() is None:
            db.add(PlatformSettings(platform_name="NavNote", footer_text="© NavNote", contact_info=""))
            db.commit()

        if db.query(SiteCategory).filter(SiteCategory.is_system.is_(True)).first() is None:
            db.add(
                SiteCategory(
                    name="未分类",
                    description="系统保留分类，删除其他分类后站点将归入此处",
                    sort_order=9999,
                    enabled=True,
                    is_system=True,
                )
            )
            db.commit()

        if db.query(ArticleCategory).first() is None:
            db.add(ArticleCategory(name="综合", sort_order=0, enabled=True))
            db.commit()

        if db.query(Admin).first() is None:
            db.add(
                Admin(
                    username="admin",
                    password_hash=hash_password(settings.initial_admin_password),
                    email="admin@example.com",
                    is_active=True,
                )
            )
            db.commit()
    except Exception:
        logger.exception("数据库种子数据初始化失败")
        db.rollback()
    finally:
        db.close()
