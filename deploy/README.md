# 生产部署

推荐架构：**Nginx** + **Gunicorn** + **MySQL 8**。

- 源码仓库：[github.com/zouming123/NavNote](https://github.com/zouming123/NavNote)
- 本地开发：[backend/README.md](../backend/README.md)、[frontend/README.md](../frontend/README.md)
- 环境变量：[docs/CONFIGURATION.md](../docs/CONFIGURATION.md)
- 首次推送 GitHub：[docs/GITHUB.md](../docs/GITHUB.md)

---

## 流程

```
git clone https://github.com/zouming123/NavNote.git   # 或在服务器上传构建产物

本机 npm run build  →  上传 backend/、frontend/dist/、deploy/
                    →  服务器 cd backend && ./install.sh --prod
                    →  编辑 .env，配置 Nginx
                    →  ./service.sh start prod
```

**勿上传：** `node_modules`、`.venv`、`backend/.env`、本地 `*.db`、`backend/uploads/` 中的私有文件。

---

## 清单

- [ ] MySQL 建库（见下）
- [ ] 本机 `cd frontend && npm ci && npm run typecheck && npm run build`
- [ ] 上传 `frontend/dist/`、`backend/`、`deploy/`
- [ ] `cd backend && ./install.sh --prod`，编辑 `.env`
- [ ] 配置 Nginx（`nginx-navnote.conf.example`）
- [ ] `./service.sh start prod`
- [ ] 登录后台并**立即修改默认密码**
- [ ] （可选）systemd（`navnote-backend.service.example`）

---

## MySQL

```sql
CREATE DATABASE navnote CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'navnote'@'127.0.0.1' IDENTIFIED BY '强密码';
GRANT ALL PRIVILEGES ON navnote.* TO 'navnote'@'127.0.0.1';
FLUSH PRIVILEGES;
```

`.env` 最小配置见 [docs/CONFIGURATION.md](../docs/CONFIGURATION.md) 或 `backend/.env.production.example`。

---

## Nginx

1. 复制 `nginx-navnote.conf.example`，替换 `__NAVNOTE_ROOT__` 和 `server_name`
2. `root` 指向 `NAVNOTE_ROOT/frontend/dist`
3. 反代 `/api/`、`/uploads/`、`/robots.txt`、`/sitemap.xml` 到 Gunicorn（默认 `127.0.0.1:8000`）

```bash
nginx -t && systemctl reload nginx
```

---

## 启停

```bash
cd backend
./service.sh start prod
./service.sh stop
./service.sh status
```

日志：`backend/.run/backend.log`

---

## 验证

```bash
curl https://域名/api/health
curl https://域名/robots.txt
```

---

## 更新

| 变更 | 操作 |
|------|------|
| 前端 | 本机 build → 覆盖 `frontend/dist/` |
| 后端 | `pip install -r requirements.txt` → `./service.sh stop && ./service.sh start prod` |
| 配置 | 改 `.env` 后重启后端 |

---

## SEO

- 设置 `PUBLIC_SITE_URL`
- Nginx 反代 `/robots.txt`、`/sitemap.xml`
- 后台上传 Logo 作为分享图
