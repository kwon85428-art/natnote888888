# NavNote

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-%3E%3D20-green.svg)](https://nodejs.org/)
[![CI](https://github.com/zouming123/NavNote/actions/workflows/ci.yml/badge.svg)](https://github.com/zouming123/NavNote/actions/workflows/ci.yml)

网址导航与文章阅读平台，含 Vue 3 前台与管理后台，FastAPI 后端。适合个人或团队快速搭建导航站与文章聚合页。

| | |
|---|---|
| **版本** | v1.0.0 |
| **演示** | [navnote.cn](https://navnote.cn) |
| **仓库** | [github.com/zouming123/NavNote](https://github.com/zouming123/NavNote) |
| **许可证** | [MIT](LICENSE) |

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [文档](#文档)
- [生产部署](#生产部署)
- [数据库](#数据库)
- [开发与测试](#开发与测试)
- [安全说明](#安全说明)
- [贡献](#贡献)
- [致谢](#致谢)
- [联系与交流](#联系与交流)

## 功能特性

| 模块 | 说明 |
|------|------|
| 网址导航 | 分类侧栏 / Dock、推荐网址、站点卡片（图标、简介、标签） |
| 文章阅读 | 分类标签页、分页、外链跳转与原创 Markdown 正文 |
| 管理后台 | 网址 / 文章 / 分类 CRUD、平台设置、访问统计、操作日志 |
| SEO | 动态 meta、`sitemap.xml`、`robots.txt` |
| 分享 | 文章详情复制本站链接、生成阅读二维码 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3、Vite、Element Plus、Pinia、Vue Router |
| 后端 | FastAPI、SQLAlchemy、Pydantic |
| 数据库 | MySQL（生产）/ SQLite（本地开发） |
| 部署 | Nginx、Gunicorn、Uvicorn |

## 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11 |
| Node.js | ≥ 20 |
| MySQL | 8.x（仅生产环境） |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/zouming123/NavNote.git
cd NavNote
```

### 2. 启动后端

```bash
cp backend/.env.example backend/.env
cd backend
./install.sh
./service.sh start dev
```

Windows PowerShell：

```powershell
Copy-Item backend\.env.example backend\.env
cd backend
.\install.ps1
.\service.ps1 start dev
```

### 3. 启动前端

新开终端：

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问地址

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:5173 | 前台（Vite 代理 `/api`、`/uploads`） |
| http://127.0.0.1:5173/admin/login | 管理后台 |
| http://127.0.0.1:8000/api/health | API 健康检查 |

**默认管理员**（仅空库首次启动时创建）：`admin` / `admin123456`  
登录后请立即在后台修改密码。生产环境务必设置强 `SECRET_KEY` 与 `INITIAL_ADMIN_PASSWORD`。

## 项目结构

```
NavNote/
├── backend/              # FastAPI 应用、数据模型、API
│   ├── app/              # 业务代码
│   ├── scripts/          # 运维脚本（如密码重置）
│   └── tests/            # 冒烟测试
├── frontend/             # Vue 3 SPA（dist/ 为构建产物，勿提交）
├── deploy/               # Nginx / systemd 示例与部署说明
├── docs/                 # 配置说明、GitHub 发布指南
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## 文档

| 文档 | 说明 |
|------|------|
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | 环境变量与部署配置 |
| [deploy/README.md](deploy/README.md) | 生产部署清单（Nginx + Gunicorn + MySQL） |
| [backend/README.md](backend/README.md) | 后端启停、数据模型、密码重置 |
| [frontend/README.md](frontend/README.md) | 前端开发、构建 |
| [docs/GITHUB.md](docs/GITHUB.md) | 首次推送 GitHub 与 Release |
| [CHANGELOG.md](CHANGELOG.md) | 版本更新记录 |

配置模板：`backend/.env.example`、`backend/.env.production.example`

## 生产部署

1. 设置 `DEBUG=false`，`SECRET_KEY` 使用 `openssl rand -hex 32` 生成
2. 使用 **MySQL**（SQLite 仅适合单进程本地开发）
3. 配置 `PUBLIC_SITE_URL` 以启用 sitemap 与分享绝对链接
4. 本机构建前端：`cd frontend && npm ci && npm run typecheck && npm run build`
5. 上传 `backend/`、`frontend/dist/`、`deploy/` 至服务器

完整步骤见 [deploy/README.md](deploy/README.md)。

## 数据库

- 表结构唯一来源：`backend/app/models/tables.py`
- 采用**逻辑外键**（无物理 `FOREIGN KEY` 约束），便于迁移与手工维护
- 新库：`create_all` 自动建表；旧库：启动时 `schema_patch` 补列并清理废弃结构
- 无 Alembic；大版本升级建议新库或自行迁移

详见 [docs/CONFIGURATION.md#数据库-schema](docs/CONFIGURATION.md#数据库-schema)。

## 开发与测试

提交前请在本地执行与 [CI](.github/workflows/ci.yml) 相同的检查：

```bash
# 前端
cd frontend && npm run typecheck && npm run build

# 后端
cd backend
python -m tests.test_mysql_dialect
python -m tests.test_scrape
python -m tests.test_seo_sitemap
python -c "from app.main import app; print('ok')"
```

CI 另包含 Ruff 静态检查（`ruff check app run.py`）。

## 安全说明

- 管理 API 需 JWT 鉴权；登录接口带图形验证码
- 无法登录时：运行 `backend/scripts/hash_admin_password.py` 重置密码；已登录可在后台改密
- 原创文章 HTML 由 Markdown 转换，生产环境请仅信任管理员发布的内容
- 公开 `visit` 接口无鉴权，如需防刷可在 Nginx / 网关层限速

## 贡献

欢迎提交 [Issue](https://github.com/zouming123/NavNote/issues) 与 [Pull Request](https://github.com/zouming123/NavNote/pulls)。提交前请确保 CI 检查通过。

## 致谢

演示站点 [navnote.cn](https://navnote.cn) 由**重庆北言文化传播有限公司**提供域名、服务器等资源支持。

## 联系与交流

<p align="center">
  <img src=".github/wechat-qr.png" width="220" alt="微信二维码" />
</p>

<p align="center">
  微信号：<code>zouming_610239882</code> · 请注明「NavNote」
</p>
