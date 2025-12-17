# Deploy 目录说明

本目录包含 Feishu HR Translator 的完整部署配置。

## 文件清单

### Docker 配置
- **`Dockerfile.backend`** - 后端服务 Docker 镜像配置
- **`Dockerfile.frontend`** - 前端服务 Docker 镜像配置（含 Nginx）
- **`docker-compose.production.yml`** - 生产环境 Docker Compose 编排文件
- **`nginx.conf`** - Nginx 配置（反向代理、静态文件服务）

### 部署脚本
- **`deploy.sh`** - 一键部署脚本（自动检查依赖、构建、启动）
- **`update.sh`** - 快速更新脚本（拉取代码、重新部署）
- **`check-health.sh`** - 健康检查脚本（检查服务状态、容器、端口）

### 配置模板
- **`.env.production`** - 生产环境配置模板（需复制为 `../.env`）

### 文档
- **`DEPLOYMENT.md`** - 详细部署指南（系统要求、步骤、故障排查）
- **`QUICK_REFERENCE.md`** - 常用命令快速参考
- **`README.md`** - 本文件

---

## 快速开始

### 1. 准备工作

确保服务器满足以下要求：
- Linux 系统（Ubuntu 20.04+, CentOS 7+ 等）
- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 内存、2 核 CPU、20GB 磁盘

### 2. 部署步骤

```bash
# 克隆或上传代码到服务器（推荐使用用户主目录）
cd ~/feishu-hr-translator

# 配置环境变量（必须在项目根目录）
cp deploy/.env.production .env
vim .env  # 修改必要的配置项

# 执行部署
cd deploy
chmod +x *.sh
./deploy.sh
```

**重要说明**：
- 环境变量文件必须放在**项目根目录** `~/feishu-hr-translator/.env`
- `deploy/.env` 仅用于 docker-compose 变量替换（如 WEB_PORT）
- 默认Web端口是 **8888**（可通过 WEB_PORT 修改）

### 3. 验证部署

```bash
# 查看容器状态
docker ps

# 执行健康检查
./check-health.sh

# 访问 Web UI
curl http://localhost
```

访问 `http://服务器IP` 即可使用。

---

## 架构说明

部署后的服务架构：

```
用户浏览器
    ↓
[Nginx (Frontend Container) :8888]
    ├─ 静态文件服务 (React SPA)
    ├─ API 反向代理 (/api/*) → [Backend Container :8080]
    └─ Webhook 代理 (/webhook/*) → [Backend Container :8080]
                                        ↓
                                    FastAPI 应用
                                        ↓
                                数据持久化 (data/ 目录)
```

**容器说明：**
- **feishu-hr-frontend**: Nginx + React 构建产物（提供静态文件和反向代理）
- **feishu-hr-backend**: Python + FastAPI + Uvicorn（Web API + 飞书 Webhook 处理）

**网络：**
- 前后端在同一 Docker 网络 (`app-network`) 中通信
- 仅前端容器暴露 8888 端口（可配置）到宿主机
- 后端容器不直接暴露端口，仅通过 Nginx 反向代理访问
- Webhook 请求通过 Nginx 转发到 backend 的 `/webhook/` 路由

---

## 配置说明

### 必须修改的配置项

在 `.env` 文件中：

```ini
# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=xxxxxxxx
FEISHU_BOT_VERIFICATION_TOKEN=xxxxxxxx
FEISHU_DEFAULT_CHAT_ID=oc_xxxxxxxx

# AI 配置
DASHSCOPE_API_KEY=sk-xxxxxxxx

# 安全配置
JWT_SECRET_KEY=请修改为随机字符串
DEFAULT_ADMIN_PASSWORD=请修改为安全密码

# 服务器地址
APP_BASE_URL=http://your-server-ip
```

### 可选配置项

```ini
# 自定义端口（默认 80）
WEB_PORT=8080

# 启用自动同步
AUTO_SYNC_ENABLED=true
AUTO_SYNC_TIME=02:00
```

---

## 常用操作

### 查看日志

```bash
docker-compose -f docker-compose.production.yml logs -f
```

### 重启服务

**注意**：如果修改了 `.env` 文件，必须使用 `down` + `up` 而不是 `restart`！

```bash
# 常规重启（不重新加载 .env）
docker-compose -f docker-compose.production.yml restart

# 重新加载环境变量（修改 .env 后必须使用）
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
```

### 停止服务

```bash
docker-compose -f docker-compose.production.yml down
```

### 更新部署

```bash
./update.sh
```

### 健康检查

```bash
./check-health.sh
```

---

## 数据持久化

以下目录挂载到宿主机，实现数据持久化：

- **`../data/reports_slim.csv`** - 报告数据
- **`../data/okr_cache.json`** - OKR 缓存
- **`../secrets/`** - 敏感凭证（如 Google Service Account JSON）

**备份建议：**

```bash
# 定期备份 data 目录
tar -czf backup-$(date +%Y%m%d).tar.gz ../data/
```

---

## 端口说明

| 服务 | 容器内端口 | 宿主机端口 | 说明 |
|------|-----------|-----------|------|
| Frontend (Nginx) | 80 | 8888 (可配置 WEB_PORT) | Web UI 访问 |
| Backend (FastAPI) | 8080 | - (不暴露) | 仅内部通过 Nginx 代理 |

**Nginx 路由说明：**
- `/` → 前端静态文件
- `/api/*` → 后端 API（`http://backend:8080/api/*`）
- `/webhook/*` → 飞书 Webhook（`http://backend:8080/webhook/*`）
- `/healthz` → 后端健康检查

---

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose -f docker-compose.production.yml logs

# 检查配置
cat ../.env | grep -E "FEISHU|DASHSCOPE"
```

### API 访问失败

```bash
# 测试后端健康
docker exec feishu-hr-backend curl http://localhost:8080/healthz

# 测试 Nginx 代理
curl http://localhost/api/healthz
```

### 前端页面空白

```bash
# 检查前端容器内的文件
docker exec feishu-hr-frontend ls -la /usr/share/nginx/html

# 重新构建前端
docker-compose -f docker-compose.production.yml build --no-cache frontend
docker-compose -f docker-compose.production.yml up -d frontend
```

更多故障排查，请参考 [DEPLOYMENT.md](DEPLOYMENT.md)。

---

## 安全建议

1. **修改默认密码** - 首次登录后立即修改
2. **保护 .env 文件** - 确保权限为 `600`，不要提交到 Git
3. **使用 HTTPS** - 生产环境建议配置 SSL 证书
4. **限制访问** - 通过防火墙限制 IP 白名单
5. **定期备份** - 自动化备份 data 目录
6. **更新依赖** - 定期更新 Docker 镜像和系统包

---

## 文档索引

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 详细部署指南（包含系统要求、详细步骤、故障排查）
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 常用命令快速参考
- **[../README.md](../README.md)** - 项目整体说明

---

## 支持

如遇到问题：
1. 查看本目录的文档
2. 执行 `./check-health.sh` 检查服务状态
3. 查看 Docker 日志排查问题
4. 提交 Issue 到项目仓库

---

**祝使用顺利！**
