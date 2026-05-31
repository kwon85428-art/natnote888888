"""本地开发：单进程 Uvicorn。生产请用 ./start.sh 或 ./service.sh start prod。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent
os.chdir(_backend_root)


def _venv_python() -> Path | None:
    if sys.platform == "win32":
        p = _backend_root / ".venv" / "Scripts" / "python.exe"
    else:
        p = _backend_root / ".venv" / "bin" / "python"
    return p if p.is_file() else None


def _import_uvicorn():
    try:
        import uvicorn

        return uvicorn
    except ModuleNotFoundError:
        vp = _venv_python()
        if vp is not None and vp.resolve() != Path(sys.executable).resolve():
            script = Path(__file__).resolve()
            os.execv(str(vp), [str(vp), str(script), *sys.argv[1:]])
        print(
            "错误：未安装 uvicorn。请在 backend/.venv 中执行：pip install -r requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


uvicorn = _import_uvicorn()  # noqa: E402

if __name__ == "__main__":
    host = os.environ.get("UVICORN_HOST", "127.0.0.1")
    port = int(os.environ.get("UVICORN_PORT", "8000"))
    reload = os.environ.get("UVICORN_RELOAD", "false").lower() in ("1", "true", "yes")

    kwargs: dict = {
        "host": host,
        "port": port,
        "reload": reload,
        "timeout_graceful_shutdown": 5,
    }
    if reload:
        kwargs["reload_dirs"] = [str(_backend_root / "app")]
        kwargs["reload_excludes"] = ["data", "data/*", "uploads", "uploads/*", "*.db", "*.db-wal", "*.db-shm"]

    try:
        uvicorn.run("app.main:app", **kwargs)
    except KeyboardInterrupt:
        pass
