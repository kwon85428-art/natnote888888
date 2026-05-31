"""SEO robots / sitemap 纯函数测试（无需数据库）。"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.seo_sitemap import build_robots_txt, resolve_public_base_url


def test_resolve_public_base_url_prefers_configured() -> None:
    url = resolve_public_base_url(
        configured="https://navnote.example.com/",
        request_scheme="http",
        request_host="localhost:8000",
    )
    assert url == "https://navnote.example.com"


def test_build_robots_txt_contains_sitemap() -> None:
    text = build_robots_txt("https://navnote.example.com")
    assert "Disallow: /admin/" in text
    assert "Allow: /articles" in text
    assert "Sitemap: https://navnote.example.com/sitemap.xml" in text


def main() -> None:
    test_resolve_public_base_url_prefers_configured()
    test_build_robots_txt_contains_sitemap()
    print("test_seo_sitemap: ok")


if __name__ == "__main__":
    main()
