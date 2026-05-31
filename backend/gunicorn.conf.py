"""Gunicorn 配置（ASGI：UvicornWorker）。

在 backend/ 目录执行：
  gunicorn -c gunicorn.conf.py app.main:app

或通过 start.sh：NAVNOTE_SERVER=gunicorn ./start.sh

环境变量（见 backend/.env.example 与 docs/CONFIGURATION.md）：
  GUNICORN_BIND          监听地址，默认 127.0.0.1:8000
  GUNICORN_HOST          与 GUNICORN_PORT 组合 bind（GUNICORN_BIND 优先）
  GUNICORN_PORT
  GUNICORN_WORKERS       Worker 数；MySQL 可 >1；SQLite 在本文件中强制为 1
  GUNICORN_TIMEOUT       请求超时（秒），默认 120
  GUNICORN_GRACEFUL_TIMEOUT
  GUNICORN_KEEPALIVE
  GUNICORN_PRELOAD       true/false，默认 false
  GUNICORN_LOG_LEVEL     默认 info
  GUNICORN_ACCESS_LOG    默认 -（stdout）
  GUNICORN_ERROR_LOG     默认 -（stderr）
"""

from __future__ import annotations

import multiprocessing
import os

_bind_host = os.getenv("GUNICORN_HOST") or os.getenv("UVICORN_HOST", "127.0.0.1")
_bind_port = os.getenv("GUNICORN_PORT") or os.getenv("UVICORN_PORT", "8000")
bind = os.getenv("GUNICORN_BIND", f"{_bind_host}:{_bind_port}")

_database_url = os.getenv("DATABASE_URL", "sqlite:///./data/navnote.db")
_is_sqlite = _database_url.strip().lower().startswith("sqlite")

_workers = os.getenv("GUNICORN_WORKERS", "").strip()
if _is_sqlite:
    workers = 1
elif _workers:
    workers = max(1, int(_workers))
else:
    workers = min((multiprocessing.cpu_count() or 1) * 2 + 1, 4)

worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
preload_app = os.getenv("GUNICORN_PRELOAD", "false").lower() in ("1", "true", "yes")

accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
capture_output = True
