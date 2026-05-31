import random

from fastapi import APIRouter, HTTPException, Request

from app.api.deps import CurrentAdmin, DbSession
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Admin
from app.schemas import CaptchaOut, ChangePasswordIn, LoginIn, TokenOut
from app.services.access_log import log_captcha_failed, log_login_failed
from app.services.admin_action_log import AdminActionLogDep
from app.services.admin_log import write_admin_log
from app.services.captcha import cleanup_expired_captcha, create_captcha, verify_captcha
from app.services.request_context import client_ip

router = APIRouter(prefix="/api/auth", tags=["auth"])





@router.get("/captcha", response_model=CaptchaOut, include_in_schema=False)

def get_captcha(db: DbSession):

    cleanup_expired_captcha(db)

    a = random.randint(1, 9)

    b = random.randint(1, 9)

    op = random.choice(["+", "-"])

    if op == "+":

        ans = str(a + b)

        q = f"{a} + {b} = ?"

    else:

        if a < b:

            a, b = b, a

        ans = str(a - b)

        q = f"{a} - {b} = ?"

    cid = create_captcha(db, ans)

    return CaptchaOut(captcha_id=cid, question=q)





@router.post("/login", response_model=TokenOut, include_in_schema=False)

def login(payload: LoginIn, request: Request, db: DbSession):

    ip = client_ip(request)

    if not verify_captcha(db, payload.captcha_id, payload.captcha_code):

        log_captcha_failed(ip=ip)

        raise HTTPException(status_code=400, detail="验证码错误")

    admin = db.query(Admin).filter(Admin.username == payload.username).first()

    if not admin or not verify_password(payload.password, admin.password_hash):

        log_login_failed(payload.username, ip=ip, reason="bad_credentials")

        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not admin.is_active:

        log_login_failed(payload.username, ip=ip, reason="disabled")

        raise HTTPException(status_code=400, detail="账号已禁用")

    token = create_access_token(admin.id)

    write_admin_log(

        db,

        admin_id=admin.id,

        action="login",

        detail="管理员登录",

        ip=ip,

        commit=True,

    )

    return TokenOut(access_token=token, expires_in=settings.access_token_expire_minutes * 60)





@router.get("/me", include_in_schema=False)

def me(admin: CurrentAdmin):

    return {"id": admin.id, "username": admin.username, "email": admin.email}





@router.post("/change-password", include_in_schema=False)

def change_password(

    payload: ChangePasswordIn,

    audit: AdminActionLogDep,

    db: DbSession,

):

    admin = audit.admin

    if not verify_password(payload.current_password, admin.password_hash):

        raise HTTPException(status_code=400, detail="当前密码错误")

    if payload.new_password == payload.current_password:

        raise HTTPException(status_code=400, detail="新密码不能与当前密码相同")

    admin.password_hash = hash_password(payload.new_password)

    audit.record("password_change", detail="管理员修改登录密码")

    db.commit()

    return {"ok": True}


