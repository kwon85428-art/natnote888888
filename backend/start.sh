#!/usr/bin/env bash
# 生产进程入口（Gunicorn / Uvicorn，前台运行）
# 用法：cd backend && NAVNOTE_SERVER=gunicorn ./start.sh
# 后台启动：./service.sh start prod
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BACKEND_DIR
cd "$BACKEND_DIR"

# shellcheck disable=SC1091
source "$BACKEND_DIR/scripts/_lib.sh"
ensure_venv

if [[ ! -f .env ]]; then
  echo "错误：缺少 .env，请先执行 ./install.sh" >&2
  exit 1
fi

if is_sqlite; then
  echo "==> SQLite（单进程）"
else
  echo "==> MySQL"
fi

server="${NAVNOTE_SERVER:-uvicorn}"
server="${server,,}"

case "$server" in
  gunicorn)
    echo "==> Gunicorn（worker 数见 gunicorn.conf.py）"
    exec "$VENV_PYTHON" -m gunicorn -c gunicorn.conf.py app.main:app
    ;;
  uvicorn)
    host="$(backend_host)"
    port="$(backend_port)"
    workers="$(clamp_workers "${UVICORN_WORKERS:-1}")"
    args=(-m uvicorn app.main:app --host "$host" --port "$port")
    [[ "$workers" != "1" ]] && args+=(--workers "$workers")
    echo "==> Uvicorn http://${host}:${port}/ workers=$workers"
    exec "$VENV_PYTHON" "${args[@]}"
    ;;
  *)
    echo "错误：NAVNOTE_SERVER=$NAVNOTE_SERVER（支持 gunicorn | uvicorn）" >&2
    exit 1
    ;;
esac
