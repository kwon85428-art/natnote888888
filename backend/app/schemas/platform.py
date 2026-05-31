from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from app.schemas.article import ArticleSummaryOut
from app.schemas.site import SiteOut


class PlatformSettingsOut(BaseModel):
    platform_name: str
    logo_path: str | None
    footer_text: str | None
    contact_info: str | None
    icp_text: str | None = None
    icp_link_url: str | None = None
    show_promoted_sites_on_sites: bool = True
    show_promoted_articles_on_sites: bool = True
    show_promoted_sites_on_articles: bool = False
    show_promoted_articles_on_articles: bool = True
    public_sites_enabled: bool = True
    public_articles_enabled: bool = True
    default_home: Literal["sites", "articles"] = "sites"
    menu_sites_label: str = "网址"
    menu_articles_label: str = "文章"

    @field_validator("menu_sites_label", "menu_articles_label", mode="before")
    @classmethod
    def _coerce_menu_label(cls, v: object, info: ValidationInfo) -> str:
        default = "网址" if info.field_name == "menu_sites_label" else "文章"
        if v is None:
            return default
        s = str(v).strip()
        return s if s else default

    class Config:
        from_attributes = True


class PublicHomeOut(BaseModel):
    """前台网址首页一次返回：减少多分类瀑布式请求。"""

    settings: PlatformSettingsOut
    site_categories: list[dict]
    sites_by_category: dict[str, list[SiteOut]]
    promoted_sites: list[SiteOut] = []
    promoted_articles: list[ArticleSummaryOut] = []


class PlatformSettingsUpdate(BaseModel):
    platform_name: str | None = None
    footer_text: str | None = None
    contact_info: str | None = None
    icp_text: str | None = None
    icp_link_url: str | None = None
    show_promoted_sites_on_sites: bool | None = None
    show_promoted_articles_on_sites: bool | None = None
    show_promoted_sites_on_articles: bool | None = None
    show_promoted_articles_on_articles: bool | None = None
    public_sites_enabled: bool | None = None
    public_articles_enabled: bool | None = None
    default_home: Literal["sites", "articles"] | None = None
    menu_sites_label: str | None = Field(None, min_length=1, max_length=32)
    menu_articles_label: str | None = Field(None, min_length=1, max_length=32)
