from pydantic import BaseModel


class SiteCategoryCreate(BaseModel):
    name: str
    icon_key: str | None = None
    description: str | None = None
    sort_order: int = 0
    enabled: bool = True


class SiteCategoryUpdate(BaseModel):
    name: str | None = None
    icon_key: str | None = None
    description: str | None = None
    sort_order: int | None = None
    enabled: bool | None = None


class SiteCategoryOut(BaseModel):
    id: int
    name: str
    icon_key: str | None
    description: str | None
    sort_order: int
    enabled: bool
    is_system: bool

    class Config:
        from_attributes = True


class SiteCategoryPageOut(BaseModel):
    items: list[SiteCategoryOut]
    total: int
    page: int
    page_size: int
