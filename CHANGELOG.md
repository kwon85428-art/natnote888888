# 更新日志

本文件记录 NavNote 的版本变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.0.0] - 2026-05-24

首个开源版本。

### 新增

- 网址导航：分类侧栏 / Dock、推荐网址、站点卡片（图标、简介、标签）
- 文章阅读：分类标签页、分页、外链跳转与原创 Markdown 正文
- 管理后台：网址 / 文章 / 分类 CRUD、平台设置、访问统计、操作日志
- SEO：`sitemap.xml`、`robots.txt`、动态 meta
- 文章分享：复制本站链接、阅读二维码
- 管理端网址维护：URL 自动抓取标题 / 描述 / favicon（流式读取，适配大型 SPA 首页）
- 运维脚本：`backend/scripts/hash_admin_password.py` 重置管理员密码

### 说明

- 数据库采用**逻辑外键**（无物理 `FOREIGN KEY` 约束），便于迁移与手工维护
- 启动时 `schema_patch` 为旧库补列，并清理废弃表 / 列 / 物理外键
- 无 Alembic；大版本升级建议新库或自行迁移

### 修复

- SQLite 旧版 libsqlite3 下 PV 统计落库兼容（ORM 累加，避免 `ON CONFLICT` 语法错误）
- Vite 开发环境预构建 Element Plus 依赖，减少 dev 反复 optimize / reload

### 技术栈

- 前端：Vue 3、Vite、Element Plus、Pinia
- 后端：FastAPI、SQLAlchemy、MySQL / SQLite
- 部署：Nginx + Gunicorn（示例见 `deploy/`）

[1.0.0]: https://github.com/zouming123/NavNote/releases/tag/v1.0.0
