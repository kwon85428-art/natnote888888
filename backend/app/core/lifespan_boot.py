"""应用启动步骤：各模块失败互不影响（关键配置校验除外）。"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable
from typing import TypeVar

from app.core.config import Settings
from app.core.logging_setup import setup_logging
from app.core.startup import ensure_runtime_dirs, validate_settings
from app.db.init_db import init_models, seed_if_empty
from app.services.stats_buffer import stats_flush_loop

logger = logging.getLogger("navnote")

T = TypeVar("T")


def _run_boot_step(name: str, fn: Callable[..., T], *args, critical: bool = False, **kwargs) -> T | None:
    try:
        return fn(*args, **kwargs)
    except SystemExit:
        raise
    except Exception:
        logger.exception("启动步骤失败（已跳过）: %s", name)
        if critical:
            raise
        return None


async def startup_application(settings: Settings) -> asyncio.Task | None:
    """执行启动流程；返回统计落库后台任务。"""
    _run_boot_step("runtime_dirs", ensure_runtime_dirs, settings, critical=True)
    _run_boot_step("logging", setup_logging, settings, critical=True)
    _run_boot_step("validate_settings", validate_settings, settings, critical=True)
    _run_boot_step("init_models", init_models, critical=True)
    _run_boot_step("seed_if_empty", seed_if_empty)

    return asyncio.create_task(stats_flush_loop(settings.stats_flush_interval_seconds))


async def shutdown_application(flush_task: asyncio.Task | None) -> None:
    if flush_task is None:
        return
    flush_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await flush_task
