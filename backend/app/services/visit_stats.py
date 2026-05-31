"""前台访问按日聚合统计（不记录路径明细）。"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models import VisitDailyStat
from app.schemas import TrendPoint

TREND_DAY_BUCKETS = 180
TREND_WEEK_BUCKETS = 52
TREND_MONTH_BUCKETS = 36

logger = logging.getLogger("navnote")


def flush_daily_page_views(db: Session, increments: dict[date, int]) -> None:
    """将缓冲的 PV 增量批量写入 visit_daily_stats。"""
    if not increments:
        return
    try:
        for stat_date, delta in increments.items():
            if delta <= 0:
                continue
            row = db.get(VisitDailyStat, stat_date)
            if row:
                row.page_views = int(row.page_views or 0) + delta
            else:
                db.add(VisitDailyStat(stat_date=stat_date, page_views=delta))
        db.commit()
    except Exception:
        logger.exception("批量写入 PV 统计失败")
        db.rollback()
        raise


def visits_total(db: Session) -> int:
    return int(db.query(func.coalesce(func.sum(VisitDailyStat.page_views), 0)).scalar() or 0)


def visits_today(db: Session) -> int:
    today = utc_now().date()
    row = db.get(VisitDailyStat, today)
    return int(row.page_views) if row else 0


def _daily_map(db: Session, start: date, end: date) -> dict[date, int]:
    rows = (
        db.query(VisitDailyStat.stat_date, VisitDailyStat.page_views)
        .filter(VisitDailyStat.stat_date >= start, VisitDailyStat.stat_date <= end)
        .all()
    )
    return {r.stat_date: int(r.page_views or 0) for r in rows}


def build_trend_series(db: Session, period: str) -> list[TrendPoint]:
    """从日聚合表生成趋势序列（周/月在应用层汇总，兼容 MySQL）。"""
    today = utc_now().date()
    series: list[TrendPoint]

    if period == "day":
        start = today - timedelta(days=TREND_DAY_BUCKETS - 1)
        m = _daily_map(db, start, today)
        series = []
        for i in range(TREND_DAY_BUCKETS - 1, -1, -1):
            d = today - timedelta(days=i)
            series.append(TrendPoint(label=d.isoformat(), count=m.get(d, 0)))
    elif period == "week":
        start = today - timedelta(days=7 * TREND_WEEK_BUCKETS + 6)
        m: dict[str, int] = defaultdict(int)
        for d, cnt in _daily_map(db, start, today).items():
            iso = d.isocalendar()
            lbl = f"{iso.year}-W{iso.week:02d}"
            m[lbl] += cnt
        series = []
        for i in range(TREND_WEEK_BUCKETS - 1, -1, -1):
            d = today - timedelta(weeks=i)
            iso = d.isocalendar()
            lbl = f"{iso.year}-W{iso.week:02d}"
            series.append(TrendPoint(label=lbl, count=m.get(lbl, 0)))
    else:
        start = today - timedelta(days=31 * TREND_MONTH_BUCKETS)
        m_month: dict[str, int] = defaultdict(int)
        for d, cnt in _daily_map(db, start, today).items():
            m_month[f"{d.year:04d}-{d.month:02d}"] += cnt
        series = []
        y, mo = today.year, today.month
        for _ in range(TREND_MONTH_BUCKETS):
            lbl = f"{y:04d}-{mo:02d}"
            series.insert(0, TrendPoint(label=lbl, count=m_month.get(lbl, 0)))
            mo -= 1
            if mo == 0:
                mo = 12
                y -= 1

    return series


def delete_stats_before(db: Session, cutoff_date: date, *, commit: bool = True) -> int:
    res = db.query(VisitDailyStat).filter(VisitDailyStat.stat_date < cutoff_date).delete()
    if commit:
        db.commit()
    return int(res or 0)
