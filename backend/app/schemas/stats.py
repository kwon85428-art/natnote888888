from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.core.admin_labels_zh import label_admin_action, label_resource_type


class StatsSummaryOut(BaseModel):
    sites_total: int
    sites_by_category: dict[str, int]
    sites_valid: int
    sites_invalid: int
    articles_total: int
    articles_by_category: dict[str, int]
    articles_by_content_type: dict[str, int]
    visits_total: int
    visits_today: int
    site_clicks_total: int
    article_reads_total: int


class LogActionOption(BaseModel):
    value: str
    label: str


class StatsLogActionsOut(BaseModel):
    items: list[LogActionOption]


class TrendPoint(BaseModel):
    label: str
    count: int


class TrendPageOut(BaseModel):
    items: list[TrendPoint]
    total: int
    page: int
    page_size: int


class AdminLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int | None
    admin_username: str | None = None
    action: str
    resource_type: str | None
    resource_id: str | None
    detail: str | None
    ip: str | None
    created_at: datetime

    @computed_field
    @property
    def action_label(self) -> str:
        return label_admin_action(self.action)

    @computed_field
    @property
    def resource_type_label(self) -> str:
        return label_resource_type(self.resource_type)


class AdminLogPageOut(BaseModel):
    items: list[AdminLogOut]
    total: int
    page: int
    page_size: int
