# 后端（FastAPI）

NavNote API：公开读接口、管理写接口、文件上传、SEO 路由。完整配置见 [docs/CONFIGURATION.md](../docs/CONFIGURATION.md)。

## 快速开始

```bash
cp .env.example .env
./install.sh
./service.sh start dev   # 或 python run.py 前台调试
```

Windows：`.\install.ps1` → `.\service.ps1 start dev`

- API：http://127.0.0.1:8000
- 健康检查：`GET /api/health`
- OpenAPI：`/docs`（仅 `DEBUG=true`）

## 常用命令

| 命令 | 说明 |
|------|------|
| `./install.sh` | 创建 venv、安装依赖 |
| `./install.sh --prod` | 复制 `.env.production.example` → `.env` |
| `./service.sh start dev` | 后台 Uvicorn |
| `./service.sh start prod` | 后台 Gunicorn |
| `python run.py` | 前台开发 |

## 数据与目录

- 表结构：`app/models/tables.py`（逻辑外键，无物理 `FOREIGN KEY`）
- 运行时：`data/`（SQLite、日志）、`uploads/`（用户上传）— 勿提交 Git
- 启动：`create_all` + `schema_patch`（旧库补列）

## 管理员密码

- 已登录：后台右上角修改密码
- 无法登录：`python scripts/hash_admin_password.py '新密码'`，将哈希写入 `admins.password_hash`

## 测试

```bash
python -m tests.test_mysql_dialect
python -m tests.test_scrape
python -m tests.test_seo_sitemap
python -c "from app.main import app; print('ok')"
```

CI 见 [.github/workflows/ci.yml](../.github/workflows/ci.yml)。
