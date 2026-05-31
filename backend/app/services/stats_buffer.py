"""访问统计内存缓冲，定时批量落库。"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import defaultdict
from datetime import date

from app.core.time import utc_now
from app.db.session import SessionLocal
from app.models import Article, Site
from app.services.visit_stats import flush_daily_page_views

logger = logging.getLogger("navnote")

_lock = threading.Lock()
_pending_pv: dict[date, int] = defaultdict(int)
_pending_site: dict[int, int] = defaultdict(int)
_pending_article: dict[int, int] = defaultdict(int)


def record_page_view_buffered() -> None:
    today = utc_now().date()
    with _lock:
        _pending_pv[today] += 1


def record_site_visit_buffered(site_id: int) -> None:
    with _lock:
        _pending_site[site_id] += 1


def record_article_visit_buffered(article_id: int) -> None:
    with _lock:
        _pending_article[article_id] += 1


def _drain() -> tuple[dict[date, int], dict[int, int], dict[int, int]]:
    with _lock:
        pv = dict(_pending_pv)
        sites = dict(_pending_site)
        articles = dict(_pending_article)
        _pending_pv.clear()
        _pending_site.clear()
        _pending_article.clear()
    return pv, sites, articles


def flush_stats_buffers() -> None:
    pv, sites, articles = _drain()
    if not pv and not sites and not articles:
        return

    db = SessionLocal()
    try:
        if pv:
            flush_daily_page_views(db, pv)
        for sid, delta in sites.items():
            row = db.get(Site, sid)
            if row:
                row.visit_count = int(row.visit_count or 0) + delta
        for aid, delta in articles.items():
            row = db.get(Article, aid)
            if row:
                row.visit_count = int(row.visit_count or 0) + delta
        if sites or articles:
            db.commit()
    except Exception:
        logger.exception("统计缓冲落库失败")
        db.rollback()
        with _lock:
            for d, n in pv.items():
                _pending_pv[d] += n
            for sid, n in sites.items():
                _pending_site[sid] += n
            for aid, n in articles.items():
                _pending_article[aid] += n
    finally:
        db.close()


async def stats_flush_loop(interval_seconds: int) -> None:
    interval = max(5, int(interval_seconds))
    logger.info("访问统计批量落库任务已启动，间隔 %s 秒", interval)
    try:
        while True:
            await asyncio.sleep(interval)
            await asyncio.to_thread(flush_stats_buffers)
    except asyncio.CancelledError:
        await asyncio.to_thread(flush_stats_buffers)
        logger.info("访问统计批量落库任务已停止（已执行末次 flush）")
        raise
