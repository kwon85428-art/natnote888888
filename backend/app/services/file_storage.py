import re
import uuid
from pathlib import Path

import aiofiles
import httpx

from app.core.config import settings

ALLOWED_UPLOAD_SUBDIRS = frozenset(
    {"logos", "favicons", "covers", "platform", "article-content"},
)
ALLOWED_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"})


def safe_filename(name: str) -> str:
    name = Path(name).name
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name)[:180]


def assert_upload_subdir(subdir: str) -> str:
    """校验上传子目录，防止路径穿越。"""
    key = subdir.strip().replace("\\", "/").strip("/")
    if not key or ".." in key or "/" in key or key not in ALLOWED_UPLOAD_SUBDIRS:
        raise ValueError("非法上传目录")
    return key


def normalize_image_extension(filename: str | None, *, default: str = ".png") -> str:
    """从文件名解析并白名单校验图片扩展名。"""
    ext = safe_filename(filename or "")
    suf = "." + ext.rsplit(".", 1)[-1].lower() if "." in ext else default
    if suf == ".jpeg":
        suf = ".jpg"
    if suf not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {suf}")
    return suf


def detect_image_ext(data: bytes, content_type: str = "", default: str = ".ico") -> str:
    """按文件头识别扩展名，避免 Content-Type 与真实格式不一致导致前台无法显示。"""
    if len(data) >= 8:
        if data[:4] == b"\x89PNG":
            return ".png"
        if data[:3] == b"\xff\xd8\xff":
            return ".jpg"
        if data[:4] == b"GIF8":
            return ".gif"
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return ".webp"
        if data[:4] == b"\x00\x00\x01\x00":
            return ".ico"
        head = data[:512].lstrip()
        if head.startswith(b"<") and (b"<svg" in head.lower() or b"<?xml" in head.lower()):
            return ".svg"
    ct = (content_type or "").lower()
    if "png" in ct:
        return ".png"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    if "svg" in ct:
        return ".svg"
    if "webp" in ct:
        return ".webp"
    if "icon" in ct or "ico" in ct:
        return ".ico"
    return default


async def save_upload_bytes(subdir: str, data: bytes, ext: str | None = None) -> str:
    safe_sub = assert_upload_subdir(subdir)
    sub = settings.upload_dir / safe_sub
    sub.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex
    suf = ext if ext else ""
    if suf and not suf.startswith("."):
        suf = "." + suf
    if suf and suf not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {suf}")
    path = sub / f"{uid}{suf}"
    async with aiofiles.open(path, "wb") as f:
        await f.write(data)
    rel = f"{safe_sub}/{path.name}"
    return rel.replace("\\", "/")


async def save_remote_to_uploads(url: str, subdir: str, default_ext: str = ".ico") -> str | None:
    try:
        from app.core.url_safe import assert_safe_public_http_url as assert_safe_fetch_url

        assert_safe_fetch_url(url)
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=3.0,
            verify=settings.remote_fetch_verify_ssl,
        ) as client:
            r = await client.get(url)
            if r.status_code >= 400:
                return None
            ct = r.headers.get("content-type", "")
            ext = detect_image_ext(r.content, ct, default_ext)
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                return None
            return await save_upload_bytes(subdir, r.content, ext)
    except Exception:
        return None
