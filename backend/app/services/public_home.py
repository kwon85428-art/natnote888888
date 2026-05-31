"""前台网址首页聚合数据。"""

from sqlalchemy.orm import Session, joinedload

from app.models import Site, SiteCategory
from app.schemas import PlatformSettingsOut, PublicHomeOut, SiteOut
from app.services.ordering import site_public_order
from app.services.platform_settings import get_or_create_platform_settings
from app.services.public_articles import list_public_articles_promoted
from app.services.public_sites import list_public_site_categories, list_public_sites_promoted

PROMOTED_PREVIEW_LIMIT = 12


def build_public_home(db: Session) -> PublicHomeOut:
    settings = get_or_create_platform_settings(db)
    settings_out = PlatformSettingsOut.model_validate(settings)

    site_categories: list[dict] = []
    sites_by_category: dict[str, list[SiteOut]] = {}
    promoted_sites: list[SiteOut] = []
    promoted_articles = []

    if settings.public_sites_enabled:
        site_categories = list_public_site_categories(db)
        cat_ids = [c["id"] for c in site_categories]
        sites_by_category = {str(cid): [] for cid in cat_ids}
        if cat_ids:
            all_sites = (
                db.query(Site)
                .options(joinedload(Site.site_category))
                .join(SiteCategory, Site.site_category_id == SiteCategory.id)
                .filter(
                    Site.site_category_id.in_(cat_ids),
                    Site.is_valid.is_(True),
                    SiteCategory.enabled.is_(True),
                    SiteCategory.is_system.is_(False),
                )
                .order_by(Site.site_category_id.asc(), *site_public_order())
                .all()
            )
            for s in all_sites:
                sites_by_category[str(s.site_category_id)].append(SiteOut.model_validate(s))
        if settings.show_promoted_sites_on_sites:
            promoted_sites = [
                SiteOut.model_validate(x)
                for x in list_public_sites_promoted(db, limit=PROMOTED_PREVIEW_LIMIT)
            ]

    if settings.public_articles_enabled and settings.show_promoted_articles_on_sites:
        promoted_articles = list_public_articles_promoted(db, limit=PROMOTED_PREVIEW_LIMIT)

    return PublicHomeOut(
        settings=settings_out,
        site_categories=site_categories,
        sites_by_category=sites_by_category,
        promoted_sites=promoted_sites,
        promoted_articles=promoted_articles,
    )
