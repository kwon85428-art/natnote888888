from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field


class SiteCreate(BaseModel):
    name: str
    url: str
    site_category_id: int
    tags: list[str] | None = None
    description: str | None = None
    favicon_path: str | None = None
    logo_path: str | None = None
    is_valid: bool = True
    sort_order: int = 0
    is_promoted: bool = False


class SiteUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    site_category_id: int | None = None
    tags: list[str] | None = None
    description: str | None = None
    favicon_path: str | None = None
    logo_path: str | None = None
    is_valid: bool | None = None
    invalid_note: str | None = None
    sort_order: int | None = None
    is_promoted: bool | None = None


class SiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    site_category_id: int
    site_category_name: str | None = Field(
        default=None, validation_alias=AliasPath("site_category", "name")
    )
    tags: list[str] | None
    description: str | None
    favicon_path: str | None
    logo_path: str | None
    is_valid: bool
    invalid_note: str | None
    sort_order: int
    is_promoted: bool
    visit_count: int
    created_at: datetime
    updated_at: datetime | None


class SitePageOut(BaseModel):
    items: list[SiteOut]
    total: int
    page: int
    page_size: int


class SiteFetchIn(BaseModel):
    url: str


class SiteFetchOut(BaseModel):
    title: str
    description: str | None
    favicon_url: str | None
    resolved_url: str


class SiteCheckOut(BaseModel):
    site_id: int
    ok: bool
    message: str | None = None
