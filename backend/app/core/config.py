from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.db_dialect import resolve_database_dialect


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="NavNote", description="应用显示名称")
    secret_key: str = Field(
        default="change-me-in-production-use-long-random-string",
        description="JWT 签名密钥，生产必须修改",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(default=120, ge=5, le=60 * 24 * 30)

    database_url: str = Field(
        default="sqlite:///./data/navnote.db",
        description="SQLAlchemy 连接串。SQLite 仅单进程；MySQL 可多 Worker（见 docs/CONFIGURATION.md）",
    )

    # 逗号分隔；留空则同源部署不启用 CORS（推荐 Nginx 反代同域）
    cors_origins: str = Field(default="", description="允许的 CORS 来源，逗号分隔")

    # 仅首次 seed 空库时使用；生产部署后请立即改密
    initial_admin_password: str = Field(default="admin123456", min_length=8)

    # backend/ 根目录（本文件位于 app/core/）
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    upload_dir: Path = base_dir / "uploads"
    data_dir: Path = base_dir / "data"

    debug: bool = Field(default=False, description="调试模式（开启 OpenAPI 文档等）")

    # 访问统计批量落库间隔（秒）
    stats_flush_interval_seconds: int = Field(default=30, ge=5, le=600)

    # 滚动日志（backend/data/logs/）
    log_file_max_bytes: int = Field(default=10 * 1024 * 1024, ge=256 * 1024, le=100 * 1024 * 1024)
    log_file_backup_count: int = Field(default=5, ge=1, le=30)

    upload_max_bytes_logo: int = Field(default=5 * 1024 * 1024, ge=1024, le=50 * 1024 * 1024)
    upload_max_bytes_cover: int = Field(default=8 * 1024 * 1024, ge=1024, le=50 * 1024 * 1024)
    upload_max_bytes_article_body: int = Field(default=8 * 1024 * 1024, ge=1024, le=50 * 1024 * 1024)

    remote_fetch_verify_ssl: bool = Field(
        default=True,
        description="抓取远程 favicon 等时是否校验 HTTPS 证书",
    )

    public_site_url: str = Field(
        default="",
        description="公开站点 canonical / sitemap 根 URL（如 https://navnote.example.com），留空则从请求头推断",
    )

    @field_validator("initial_admin_password")
    @classmethod
    def _admin_password_not_empty(cls, v: str) -> str:
        if len(v.strip()) < 8:
            raise ValueError("INITIAL_ADMIN_PASSWORD 至少 8 位")
        return v.strip()

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def database_dialect(self) -> str:
        return resolve_database_dialect(self.database_url)


settings = Settings()
