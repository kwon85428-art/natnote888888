#!/usr/bin/env bash
# 安装 Python 依赖与虚拟环境
# 用法：cd backend && ./install.sh          # 本地开发
#       cd backend && ./install.sh --prod  # 生产服务器
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BACKEND_DIR
# shellcheck disable=SC1091
source "$BACKEND_DIR/scripts/_lib.sh"

ensure_venv

if [[ ! -f .env ]]; then
  if [[ "${1:-}" == "--prod" ]] && [[ -f .env.production.example ]]; then
    cp .env.production.example .env
    echo "已创建 .env（来自 .env.production.example），请编辑后启动。"
  elif [[ -f .env.example ]]; then
    cp .env.example .env
    echo "已创建 .env（来自 .env.example），请编辑后启动。"
  fi
fi

echo "==> 后端依赖就绪：$VENV_PYTHON"
