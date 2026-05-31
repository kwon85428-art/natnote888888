"""平台设置：保证存在单行配置并可被公开/管理接口复用。"""

from sqlalchemy.orm import Session

from app.models import PlatformSettings


def get_or_create_platform_settings(db: Session) -> PlatformSettings:
    row = db.query(PlatformSettings).first()
    if row is None:
        row = PlatformSettings(platform_name="NavNote")
        db.add(row)
        db.commit()
        db.refresh(row)
    return row
