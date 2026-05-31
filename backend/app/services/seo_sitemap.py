"""生成 robots.txt 与 sitemap.xml（公开页 SEO）。"""

from __future__ import annotations

from datetime import UTC, datetime
from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from app.models import Article, ArticleCategory, PlatformSettings


def resolve_public_base_url(*, configured: str | None, request_scheme: str, request_host: str) -> str:
    if configured and configured.strip():
        return configured.strip().rstrip("/")
    host = (request_host or "").strip()
    if not host:
        return ""
    scheme = (request_scheme or "https").split(",")[0].strip() or "https"
    return f"{scheme}://{host}".rstrip("/")


def _fmt_lastmod(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt.strftime("%Y-%m-%d")


def build_robots_txt(base_url: str) -> str:
    sitemap_line = f"Sitemap: {base_url}/sitemap.xml" if base_url else "Sitemap: /sitemap.xml"
    return "\n".join(
        [
            "# NavNote 公开页允许抓取；管理端不收录。",
            "User-agent: *",
            "Allow: /",
            "Allow: /sites",
            "Allow: /articles",
            "Disallow: /admin/",
            "Disallow: /api/",
            sitemap_line,
            "",
        ]
    )


def build_sitemap_xml(db: Session, base_url: str) -> str:
    settings = db.query(PlatformSettings).first()
    sites_enabled = settings.public_sites_enabled if settings else True
    articles_enabled = settings.public_articles_enabled if settings else True

    entries: list[tuple[str, str | None]] = []
    today = _fmt_lastmod(datetime.now(UTC))

    if sites_enabled and articles_enabled:
        entries.append((f"{base_url}/", today))
    if sites_enabled:
        entries.append((f"{base_url}/sites", today))
    if articles_enabled:
        entries.append((f"{base_url}/articles", today))
        rows = (
            db.query(Article.id, Article.updated_at, Article.published_at)
            .join(ArticleCategory, Article.article_category_id == ArticleCategory.id)
            .filter(ArticleCategory.enabled.is_(True))
            .order_by(Article.id.asc())
            .all()
        )
        for aid, updated_at, published_at in rows:
            entries.append((f"{base_url}/articles/{aid}", _fmt_lastmod(updated_at or published_at)))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen: set[str] = set()
    for loc, lastmod in entries:
        if loc in seen:
            continue
        seen.add(loc)
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"
