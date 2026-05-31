# 配置说明

NavNote 的配置分为：**后端 `.env`**、**前端 Vite 环境变量**、**部署层（Nginx / systemd）**。  
生效规则：后端**仅**识别 `app/core/config.py` 中 `Settings` 声明的变量，其它键会被忽略。

项目仓库：[github.com/zouming123/NavNote](https://github.com/zouming123/NavNote)

模板文件：

| 文件 | 用途 |
|------|------|
| [backend/.env.example](../backend/.env.example) | 本地开发 |
| [backend/.env.production.example](../backend/.env.production.example) | 生产服务器 |
| [frontend/.env.example](../frontend/.env.example) | 前端分域开发（可选） |
| [frontend/.env.production.example](../frontend/.env.production.example) | 前端分域构建（可选） |

---

## 后端环境变量

### 必填（生产）

| 变量 | 说明 |
|------|------|
| `SECRET_KEY` | JWT 签名密钥。生产用 `openssl rand -hex 32` 生成，勿使用占位值 |
| `DEBUG` | 生产必须为 `false`（关闭 `/docs` 等调试接口） |
| `DATABASE_URL` | 生产使用 MySQL，见 [deploy/README.md](../deploy/README.md) |
| `INITIAL_ADMIN_PASSWORD` | 空库首次创建 `admin` 的密码（≥8 位）；部署后请立即在后台改密 |

### 常用（可选）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_NAME` | `NavNote` | 应用显示名称 |
| `JWT_ALGORITHM` | `HS256` | JWT 算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | 登录 Token 有效期（5～43200） |
| `CORS_ORIGINS` | （空） | 前后端分域时的 Origin，逗号分隔；同源 Nginx 反代留空 |
| `PUBLIC_SITE_URL` | （空） | 站点 HTTPS 根 URL，用于 sitemap / 分享绝对链接 |
| `STATS_FLUSH_INTERVAL_SECONDS` | `30` | 访问 PV 批量落库间隔（秒） |
| `REMOTE_FETCH_VERIFY_SSL` | `true` | 抓取远程 favicon / 页面 meta 时是否校验 HTTPS 证书 |
| `LOG_FILE_MAX_BYTES` | `10485760` | 滚动日志单文件上限 |
| `LOG_FILE_BACKUP_COUNT` | `5` | 日志保留份数 |

### 上传大小上限（字节）

| 变量 | 默认值 |
|------|--------|
| `UPLOAD_MAX_BYTES_LOGO` | 5242880（5MB） |
| `UPLOAD_MAX_BYTES_COVER` | 8388608（8MB） |
| `UPLOAD_MAX_BYTES_ARTICLE_BODY` | 8388608（8MB） |

### 数据库

| 场景 | `DATABASE_URL` 示例 |
|------|---------------------|
| 本地 SQLite | `sqlite:///./data/navnote.db` |
| 生产 MySQL | `mysql+pymysql://navnote:密码@127.0.0.1:3306/navnote?charset=utf8mb4` |

SQLite **仅单进程**；Gunicorn 检测到 SQLite 时强制 `workers=1`。

### 进程参数（一般无需改）

由 `backend/service.sh` / `start.sh` 读取：

| 变量 | 说明 |
|------|------|
| `NAVNOTE_SERVER` | `uvicorn`（开发）或 `gunicorn`（生产） |
| `GUNICORN_BIND` | 默认 `127.0.0.1:8000` |
| `GUNICORN_WORKERS` | MySQL 可 >1；SQLite 强制 1 |
| `UVICORN_HOST` / `UVICORN_PORT` | 开发监听地址 |

---

## 前端环境变量

| 变量 | 何时需要 |
|------|----------|
| `VITE_API_BASE_URL` | 前后端**分域**时，指向 API 根地址（无末尾 `/`） |

**同源部署**（Nginx 同一域名反代 `/api`）：无需任何前端 env 文件，直接 `npm run build`。

---

## 部署配置

### Nginx

示例：[deploy/nginx-navnote.conf.example](../deploy/nginx-navnote.conf.example)

| 占位符 | 替换为 |
|--------|--------|
| `__NAVNOTE_ROOT__` | 仓库在服务器上的绝对路径 |
| `server_name` | 你的域名 |

需反代：`/api/`、`/uploads/`、`/robots.txt`、`/sitemap.xml`；静态根目录指向 `frontend/dist/`。

### systemd（可选）

示例：[deploy/navnote-backend.service.example](../deploy/navnote-backend.service.example)

替换 `__NAVNOTE_ROOT__`，并按环境修改 `User` / `Group`。

---

## 管理员密码

| 方式 | 说明 |
|------|------|
| 后台改密 | 登录后右上角 → 修改密码 |
| 运维重置 | `python scripts/hash_admin_password.py '新密码'`（在 `backend/` 目录） |

无邮件找回；详见 [backend/README.md](../backend/README.md)。

---

## 数据库 schema

- 表定义唯一来源：`backend/app/models/tables.py`
- 逻辑外键：`site_category_id`、`article_category_id`、`admin_id` 等，**无数据库物理外键**
- 新库：`create_all` 自动建表
- 旧库：启动时 `schema_patch.apply_schema_patches()` 补列并清理废弃结构
