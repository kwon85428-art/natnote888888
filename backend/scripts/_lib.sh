#!/usr/bin/env bash
# 后端公共函数：虚拟环境、.env 读取
set -euo pipefail

env_var() {
  local key="$1" default="${2:-}"
  local file="${BACKEND_DIR:?BACKEND_DIR}/.env"
  [[ -f "$file" ]] || { echo "$default"; return; }
  local line
  line="$(grep -E "^[[:space:]]*${key}=" "$file" 2>/dev/null | tail -n1 || true)"
  [[ -n "$line" ]] || { echo "$default"; return; }
  local val="${line#*=}"
  val="${val#"${val%%[![:space:]]*}"}"
  val="${val%"${val##*[![:space:]]}"}"
  val="${val#\"}"; val="${val%\"}"; val="${val#\'}"; val="${val%\'}"
  echo "$val"
}

database_url() { env_var DATABASE_URL "sqlite:///./data/navnote.db"; }
is_sqlite() { [[ "$(database_url)" == sqlite:* ]]; }

clamp_workers() {
  local want="$1"
  if is_sqlite && [[ "$want" -gt 1 ]]; then
    echo "SQLite 仅支持单进程，workers=1（原值 ${want}）" >&2
    echo 1
  else
    echo "$want"
  fi
}

backend_host() { env_var UVICORN_HOST "127.0.0.1"; }
backend_port() { env_var UVICORN_PORT "8000"; }

ensure_venv() {
  cd "$BACKEND_DIR"
  local py="${PYTHON:-}"
  if [[ -z "$py" ]]; then
    command -v python3 >/dev/null && py=python3 || py=python
  fi
  [[ -d .venv ]] || "$py" -m venv .venv
  if [[ -x .venv/bin/python ]]; then
    export VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
  else
    export VENV_PYTHON="$BACKEND_DIR/.venv/Scripts/python.exe"
  fi
  if [[ "${SKIP_PIP_INSTALL:-0}" != "1" ]]; then
    "$VENV_PYTHON" -m pip install -q -U pip setuptools wheel
    "$VENV_PYTHON" -m pip install -q -r requirements.txt
  fi
  mkdir -p data uploads .run
  for d in logos favicons covers platform article-content; do mkdir -p "uploads/$d"; done
}
