"""公开 API 模块开关与访问控制。"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.platform_settings import get_or_create_platform_settings


def ensure_public_sites_enabled(db: Session) -> None:
    settings = get_or_create_platform_settings(db)
    if not settings.public_sites_enabled:
        raise HTTPException(status_code=404, detail="网址模块未开放")


def ensure_public_articles_enabled(db: Session) -> None:
    settings = get_or_create_platform_settings(db)
    if not settings.public_articles_enabled:
        raise HTTPException(status_code=404, detail="文章模块未开放")
