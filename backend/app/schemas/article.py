from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field, computed_field

from app.core.admin_labels_zh import label_content_type


class ArticleCategoryCreate(BaseModel):
    name: str
    icon_key: str | None = None
    description: str | None = None
    sort_order: int = 0
    enabled: bool = True


class ArticleCategoryUpdate(BaseModel):
    name: str | None = None
    icon_key: str | None = None
    description: str | None = None
    sort_order: int | None = None
    enabled: bool | None = None


class ArticleCategoryOut(BaseModel):
    id: int
    name: str
    icon_key: str | None
    description: str | None
    sort_order: int
    enabled: bool

    class Config:
        from_attributes = True


class ArticleCategoryPageOut(BaseModel):
    items: list[ArticleCategoryOut]
    total: int
    page: int
    page_size: int


class ArticleCreate(BaseModel):
    title: str
    summary: str | None = None
    article_category_id: int
    tags: list[str] | None = None
    published_at: datetime
    cover_path: str | None = None
    source_url: str | None = None
    content_type: str = "external"
    body_html: str | None = None
    body_markdown: str | None = None
    is_pinned: bool = False
    pin_order: int | None = None
    is_promoted: bool = False


class ArticleUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    article_category_id: int | None = None
    tags: list[str] | None = None
    published_at: datetime | None = None
    cover_path: str | None = None
    source_url: str | None = None
    content_type: str | None = None
    body_html: str | None = None
    body_markdown: str | None = None
    is_pinned: bool | None = None
    pin_order: int | None = None
    is_promoted: bool | None = None


class ArticleSummaryOut(BaseModel):
    """公开列表 / 首页预览：不含正文，减小 payload。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None
    article_category_id: int
    article_category_name: str | None = Field(
        default=None,
        validation_alias=AliasPath("article_category", "name"),
    )
    tags: list[str] | None
    published_at: datetime
    cover_path: str | None
    source_url: str | None
    content_type: str
    is_pinned: bool
    pin_order: int | None
    is_promoted: bool
    visit_count: int

    @computed_field
    @property
    def content_type_label(self) -> str:
        return label_content_type(self.content_type)


class ArticleSummaryPageOut(BaseModel):
    items: list[ArticleSummaryOut]
    total: int
    page: int
    page_size: int


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None
    article_category_id: int
    article_category_name: str | None = Field(
        default=None,
        validation_alias=AliasPath("article_category", "name"),
    )
    tags: list[str] | None
    published_at: datetime
    cover_path: str | None
    source_url: str | None
    content_type: str
    body_html: str | None
    body_markdown: str | None
    is_pinned: bool
    pin_order: int | None
    is_promoted: bool
    visit_count: int
    created_at: datetime
    updated_at: datetime | None

    @computed_field
    @property
    def content_type_label(self) -> str:
        return label_content_type(self.content_type)


class ArticlePageOut(BaseModel):
    items: list[ArticleOut]
    total: int
    page: int
    page_size: int
