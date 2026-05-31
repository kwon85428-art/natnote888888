"""远程页面元数据抓取（标题、描述、favicon）。"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.url_safe import assert_safe_public_http_url as assert_safe_fetch_url

# 仅解析 <head> 即可；重型 SPA 首页可能数 MB，但 meta 通常在头部
HEAD_SCAN_BYTES = 768 * 1024
FETCH_TIMEOUT = 8.0

_HEAD_END = b"</head>"
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _normalize_http_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


async def _read_html_head_bytes(resp: httpx.Response, *, max_bytes: int) -> bytes:
    """流式读取，遇到 </head> 或达到上限即停止，避免拉取整页。"""
    buf = bytearray()
    async for chunk in resp.aiter_bytes(8192):
        buf.extend(chunk)
        if len(buf) > max_bytes:
            return bytes(buf[:max_bytes])
        idx = buf.lower().find(_HEAD_END)
        if idx != -1:
            return bytes(buf[: idx + len(_HEAD_END)])
    return bytes(buf)


def _parse_html_metadata(html: str, final_url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    desc = None
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"].strip()
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        desc = og_desc["content"].strip()

    if not title:
        title = _regex_meta(html, r"<title[^>]*>([^<]+)</title>", re.I)
    if not desc:
        desc = _regex_meta(
            html,
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            re.I,
        ) or _regex_meta(
            html,
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
            re.I,
        )

    favicon_url = None
    for link in soup.find_all("link", href=True):
        rel = link.get("rel")
        if isinstance(rel, list):
            rel_attr = " ".join(rel).lower()
        else:
            rel_attr = (rel or "").lower()
        if "icon" in rel_attr and "mask-icon" not in rel_attr:
            favicon_url = urljoin(final_url, link["href"])
            break
    if not favicon_url:
        favicon_url = _guess_favicon(final_url)

    return {
        "title": title or urlparse(final_url).netloc,
        "description": desc,
        "favicon_url": favicon_url,
        "resolved_url": final_url,
    }


def _regex_meta(html: str, pattern: str, flags: int) -> str | None:
    m = re.search(pattern, html, flags)
    if not m:
        return None
    return m.group(1).strip() or None


async def fetch_site_metadata(url: str, timeout: float = FETCH_TIMEOUT) -> dict:
    url = _normalize_http_url(url)
    assert_safe_fetch_url(url)

    headers = {"User-Agent": _USER_AGENT}

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=timeout,
        headers=headers,
        verify=settings.remote_fetch_verify_ssl,
    ) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            final_url = str(resp.url)
            assert_safe_fetch_url(final_url)
            content_type = resp.headers.get("content-type", "")
            if "html" not in content_type.lower() and "text/plain" not in content_type.lower():
                await resp.aclose()
                title = urlparse(final_url).netloc or final_url
                return {
                    "title": title,
                    "description": None,
                    "favicon_url": _guess_favicon(final_url),
                    "resolved_url": final_url,
                }

            raw = await _read_html_head_bytes(resp, max_bytes=HEAD_SCAN_BYTES)
            encoding = resp.charset_encoding or "utf-8"
            html = raw.decode(encoding, errors="replace")
            return _parse_html_metadata(html, final_url)


def _guess_favicon(page_url: str) -> str:
    parsed = urlparse(page_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


async def check_url_reachable(url: str, timeout: float = 5.0) -> tuple[bool, str | None]:
    url = _normalize_http_url(url)
    try:
        assert_safe_fetch_url(url)
    except ValueError as e:
        return False, str(e)
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            verify=settings.remote_fetch_verify_ssl,
        ) as client:
            r = await client.head(url)
            if r.status_code >= 400:
                r = await client.get(url)
            if r.status_code < 400:
                return True, None
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)[:200]
