"""前台与后台共用的列表排序子句。"""

from sqlalchemy import func

from app.models import Article, Site


def article_order():
    return (
        Article.is_promoted.desc(),
        Article.is_pinned.desc(),
        func.coalesce(Article.pin_order, -1).desc(),
        Article.published_at.desc(),
        Article.id.desc(),
    )


def site_public_order():
    return (
        Site.is_promoted.desc(),
        Site.sort_order.desc(),
        Site.id.desc(),
    )
