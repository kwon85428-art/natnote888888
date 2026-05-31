# 前端（Vue 3 + Vite）

NavNote 单页应用：公开页（网址 / 文章）+ 管理后台。环境变量见 [docs/CONFIGURATION.md](../docs/CONFIGURATION.md)。

## 快速开始

```bash
npm install
npm run dev
```

开发地址：http://127.0.0.1:5173（需同时启动后端，见 [backend/README.md](../backend/README.md)）

## 命令

| 命令 | 说明 |
|------|------|
| `npm run dev` | 开发服务器 |
| `npm run build` | 生产构建 → `dist/` |
| `npm run preview` | 预览构建产物 |
| `npm run typecheck` | TypeScript 检查 |

## 部署

```bash
npm ci && npm run typecheck && npm run build
```

将 `dist/` 上传至服务器。`dist/`、`node_modules/` **勿提交 Git**。详见 [deploy/README.md](../deploy/README.md)。
