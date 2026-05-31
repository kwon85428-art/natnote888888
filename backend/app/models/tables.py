from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import JSON, Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.core.time import utc_now
from app.db.base import Base


class ContentType(StrEnum):
    external = "external"
    original = "original"


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class CaptchaChallenge(Base):
    __tablename__ = "captcha_challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    answer: Mapped[str] = mapped_column(String(32))
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class SiteCategory(Base):
    __tablename__ = "site_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    icon_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    sites: Mapped[list[Site]] = relationship(
        back_populates="site_category",
        primaryjoin=lambda: SiteCategory.id == foreign(Site.site_category_id),
        foreign_keys=lambda: [Site.site_category_id],
    )


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    site_category_id: Mapped[int] = mapped_column(Integer, index=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    favicon_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    logo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    invalid_note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_promoted: Mapped[bool] = mapped_column(Boolean, default=False)
    visit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    site_category: Mapped[SiteCategory] = relationship(
        back_populates="sites",
        primaryjoin=lambda: foreign(Site.site_category_id) == SiteCategory.id,
        foreign_keys=[site_category_id],
    )


class ArticleCategory(Base):
    __tablename__ = "article_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    icon_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    articles: Mapped[list[Article]] = relationship(
        back_populates="article_category",
        primaryjoin=lambda: ArticleCategory.id == foreign(Article.article_category_id),
        foreign_keys=lambda: [Article.article_category_id],
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    article_category_id: Mapped[int] = mapped_column(Integer, index=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    cover_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    content_type: Mapped[str] = mapped_column(String(32), default=ContentType.external.value)
    body_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    pin_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_promoted: Mapped[bool] = mapped_column(Boolean, default=False)
    visit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    article_category: Mapped[ArticleCategory] = relationship(
        back_populates="articles",
        primaryjoin=lambda: foreign(Article.article_category_id) == ArticleCategory.id,
        foreign_keys=[article_category_id],
    )


class PlatformSettings(Base):
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform_name: Mapped[str] = mapped_column(String(255), default="NavNote")
    logo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    footer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    icp_text: Mapped[str | None] = mapped_column(String(128), nullable=True)
    icp_link_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    show_promoted_sites_on_sites: Mapped[bool] = mapped_column(Boolean, default=True)
    show_promoted_articles_on_sites: Mapped[bool] = mapped_column(Boolean, default=True)
    show_promoted_sites_on_articles: Mapped[bool] = mapped_column(Boolean, default=False)
    show_promoted_articles_on_articles: Mapped[bool] = mapped_column(Boolean, default=True)
    public_sites_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    public_articles_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    default_home: Mapped[str] = mapped_column(String(16), default="sites")
    menu_sites_label: Mapped[str] = mapped_column(String(32), default="网址", nullable=False)
    menu_articles_label: Mapped[str] = mapped_column(String(32), default="文章", nullable=False)


class VisitDailyStat(Base):
    """前台访问按自然日聚合的 PV，不记录路径明细。"""

    __tablename__ = "visit_daily_stats"

    stat_date: Mapped[date] = mapped_column(Date, primary_key=True)
    page_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)
