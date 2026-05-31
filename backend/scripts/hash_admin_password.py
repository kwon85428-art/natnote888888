#!/usr/bin/env python3
"""生成管理员 password_hash（bcrypt），用于运维重置密码时手动更新数据库。

用法（在 backend/ 目录）:
  .venv/bin/python scripts/hash_admin_password.py '你的新密码'

Windows:
  .venv\\Scripts\\python.exe scripts\\hash_admin_password.py "你的新密码"

将输出的哈希复制到 admins.password_hash 字段；算法与线上一致（bcrypt, 12 rounds）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.security import hash_password  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate bcrypt password_hash for the admins table",
    )
    parser.add_argument(
        "password",
        help="New plain text password (minimum 8 characters)",
    )
    parser.add_argument(
        "--username",
        default="admin",
        help="Admin username for sample SQL (default: admin)",
    )
    args = parser.parse_args()

    pwd = args.password
    if len(pwd) < 8:
        print("错误：密码至少 8 位", file=sys.stderr)
        return 1

    hashed = hash_password(pwd)
    user = args.username.replace("'", "''")

    print(hashed)
    print()
    print("将上述哈希写入 admins.password_hash，例如：")
    print(f"  UPDATE admins SET password_hash = '{hashed}' WHERE username = '{user}';")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
