"""公开 HTTP URL 校验与远程抓取目标限制。"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


def is_safe_http_url(url: str) -> bool:
    """仅允许带 host 的 http/https 链接（用于外链跳转等）。"""
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.netloc or not parsed.hostname:
        return False
    if parsed.username or parsed.password:
        return False
    return True


def _hostname_blocked(hostname: str) -> bool:
    host = (hostname or "").strip().lower().rstrip(".")
    if not host:
        return True
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return True
    try:
        ip = ipaddress.ip_address(host)
        return bool(
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        )
    except ValueError:
        return False


def assert_safe_public_http_url(url: str) -> str:
    """校验并返回规范化后的 URL；不合法时抛出 ValueError。"""
    raw = (url or "").strip()
    if not is_safe_http_url(raw):
        raise ValueError("仅支持 http/https 链接")
    parsed = urlparse(raw)
    if _hostname_blocked(parsed.hostname or ""):
        raise ValueError("不允许访问该主机")
    return raw
