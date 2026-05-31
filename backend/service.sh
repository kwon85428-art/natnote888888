#!/usr/bin/env bash
# 后端后台启停
# 用法：cd backend && ./service.sh start [dev|prod|stop|status]
#
#   dev  — run.py（开发）
#   prod — Gunicorn（生产）
#
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BACKEND_DIR
# shellcheck disable=SC1091
source "$BACKEND_DIR/scripts/_lib.sh"

RUN_DIR="$BACKEND_DIR/.run"
PIDFILE="$RUN_DIR/backend.pid"
LOGFILE="$RUN_DIR/backend.log"
MODE_FILE="$RUN_DIR/backend.mode"

usage() {
  cat <<EOF
用法：$0 <start|stop|status> [dev|prod]

  start [dev|prod]   后台启动（默认 dev）
  stop               停止并释放端口
  status             查看状态

前台调试：python run.py
生产前台：NAVNOTE_SERVER=gunicorn ./start.sh
EOF
}

stop_service() {
  local port; port="$(backend_port)"
  if [[ -f "$PIDFILE" ]]; then
    local pid; pid="$(cat "$PIDFILE")"
    kill "$pid" 2>/dev/null || true
    sleep 1
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$PIDFILE" "$MODE_FILE"
    echo "==> 已停止 PID $pid"
  fi
  command -v fuser >/dev/null && fuser -k "${port}/tcp" 2>/dev/null || true
}

start_service() {
  local mode="${1:-dev}"
  [[ "$mode" == "dev" || "$mode" == "prod" ]] || { echo "模式须为 dev 或 prod"; exit 1; }

  ensure_venv
  mkdir -p "$RUN_DIR"

  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "已在运行，先执行：$0 stop"; exit 1
  fi

  local host port
  host="$(backend_host)"; port="$(backend_port)"
  cd "$BACKEND_DIR"

  if [[ "$mode" == "dev" ]]; then
    nohup "$VENV_PYTHON" run.py >>"$LOGFILE" 2>&1 &
  else
    export NAVNOTE_SERVER="${NAVNOTE_SERVER:-gunicorn}"
    nohup bash start.sh >>"$LOGFILE" 2>&1 &
  fi
  echo $! >"$PIDFILE"
  echo "$mode" >"$MODE_FILE"
  echo "==> [$mode] http://${host}:${port}/ PID=$(cat "$PIDFILE")  日志：$LOGFILE"
}

case "${1:-}" in
  start) start_service "${2:-dev}" ;;
  stop) stop_service ;;
  status)
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "运行中 PID=$(cat "$PIDFILE") mode=$(cat "$MODE_FILE" 2>/dev/null) http://$(backend_host):$(backend_port)/"
    else
      echo "未运行"; exit 1
    fi
    ;;
  *) usage ;;
esac
