import logging
import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models import CaptchaChallenge

logger = logging.getLogger("navnote")


def create_captcha(db: Session, answer: str, ttl_seconds: int = 300) -> str:
    cid = str(uuid.uuid4())
    row = CaptchaChallenge(
        id=cid,
        answer=answer.strip().lower(),
        expires_at=utc_now() + timedelta(seconds=ttl_seconds),
    )
    db.add(row)
    db.commit()
    return cid


def verify_captcha(db: Session, captcha_id: str, user_input: str) -> bool:
    if not captcha_id or user_input is None:
        return False
    row = db.get(CaptchaChallenge, captcha_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    if row.expires_at < utc_now():
        return False
    return row.answer == user_input.strip().lower()


def cleanup_expired_captcha(db: Session) -> None:
    """删除过期验证码；失败仅记日志，不影响登录流程。"""
    try:
        now = utc_now()
        db.query(CaptchaChallenge).filter(CaptchaChallenge.expires_at < now).delete()
        db.commit()
    except Exception:
        logger.exception("清理过期验证码失败")
        db.rollback()
