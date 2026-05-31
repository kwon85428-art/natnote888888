# 发布到 GitHub

本文说明如何将 NavNote 提交到 GitHub 并创建 **v1.0.0** Release。

**官方仓库：** [https://github.com/zouming123/NavNote](https://github.com/zouming123/NavNote)  
**克隆地址：** `https://github.com/zouming123/NavNote.git`

---

## 发布前检查

### 不要提交的内容

以下已在 [.gitignore](../.gitignore) 中，提交前请确认未被 `git add`：

| 路径 | 原因 |
|------|------|
| `backend/.env` | 密钥与数据库密码 |
| `backend/.venv/` | Python 虚拟环境 |
| `backend/data/`、`*.db` | 本地数据库、日志与锁文件 |
| `backend/uploads/` | 用户上传的图片与附件 |
| `frontend/node_modules/` | 依赖目录 |
| `frontend/dist/` | 构建产物（在服务器或 CI 构建） |
| `frontend/.env.local`、`.env.production` | 本地 / 生产前端密钥 |
| `*.zip`、`*.log` | 本地打包备份与运行日志 |

### 建议本地验证

与 [README.md](../README.md#开发检查) 及 [CI](../.github/workflows/ci.yml) 保持一致。

---

## 首次提交并推送

在项目根目录（含 `README.md`、`backend/`、`frontend/` 的目录）：

```bash
git init
git branch -M main
git add .
git status   # 确认无 .env、node_modules、dist、.venv、*.db
git commit -m "$(cat <<'EOF'
Initial release: NavNote v1.0.0

网址导航 + 文章阅读 + 管理后台，FastAPI + Vue 3。
EOF
)"
git remote add origin https://github.com/zouming123/NavNote.git
git push -u origin main
```

若远程仓库已存在且为新建空仓库，直接执行 `remote add` 与 `push` 即可。

若本地已有其它 `origin`，可改用：

```bash
git remote set-url origin https://github.com/zouming123/NavNote.git
git push -u origin main
```

---

## 创建 Release（v1.0.0）

1. 打开 [Releases](https://github.com/zouming123/NavNote/releases) → **Draft a new release**
2. **Choose a tag**：`v1.0.0`（Create new tag on `main`）
3. **Release title**：`NavNote v1.0.0`
4. **Description** 可使用下方模板
5. 点击 **Publish release**

### Release 说明模板

```markdown
## NavNote v1.0.0

首个开源版本：网址导航 + 文章阅读 + 管理后台。

### 功能

- 网址分类导航、推荐站点、站点卡片
- 文章列表 / 详情、原创 Markdown 与外链
- 管理后台 CRUD、平台设置、访问统计、操作日志
- SEO（sitemap、robots）、文章分享与二维码

### 快速开始

见 [README.md](https://github.com/zouming123/NavNote/blob/main/README.md)

### 部署

见 [deploy/README.md](https://github.com/zouming123/NavNote/blob/main/deploy/README.md)

### 配置

见 [docs/CONFIGURATION.md](https://github.com/zouming123/NavNote/blob/main/docs/CONFIGURATION.md)
```

---

## 仓库信息建议

在 GitHub 仓库 **Settings → General** 中可填写：

**Description（简介）**

```
NavNote — 网址导航与文章阅读平台，含 Vue 3 前台与管理后台，FastAPI 后端，支持 MySQL / SQLite。
```

**Homepage（可选）**

你的演示站地址（如有）。

**Topics（标签）**

```
vue3, vite, fastapi, sqlalchemy, navigation, blog, cms, self-hosted, element-plus, python
```

---

## 后续版本

1. 在 [CHANGELOG.md](../CHANGELOG.md) 追加新版本条目
2. 合并到 `main` 后打 tag：`git tag v1.1.0 && git push origin v1.1.0`
3. 在 [Releases](https://github.com/zouming123/NavNote/releases) 创建对应 Release，并更新 CHANGELOG 底部链接

---

## 常见问题

**Q：能否只上传 backend，不包含 frontend 源码？**  
开源发布建议保留完整仓库；生产只需上传 `frontend/dist/` 与 `backend/`，见 [deploy/README.md](../deploy/README.md)。

**Q：默认管理员密码会泄露吗？**  
仅空库首次启动时使用 `INITIAL_ADMIN_PASSWORD`；生产必须在 `.env` 设强密码并在后台改密。勿将 `.env` 提交到 Git。

**Q：CI 失败怎么办？**  
本地执行与 [ci.yml](../.github/workflows/ci.yml) 相同命令；常见原因为未提交 `package-lock.json` 或 Ruff 检查未通过。

**Q：仓库名大小写？**  
GitHub 地址为 `zouming123/NavNote`；克隆后目录名通常为 `NavNote`，与文档中 `cd NavNote` 一致。
