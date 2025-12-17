# Feishu HR Translator - Linux 服务器部署指南

本指南详细说明如何在 Linux 测试/生产服务器上部署 Feishu HR Translator（包含 Web UI 和 Backend）。

## 目录

- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [运维管理](#运维管理)
- [故障排查](#故障排查)

---

## 系统要求

### 硬件要求
- **CPU**: 2 核及以上
- **内存**: 4GB 及以上
- **磁盘**: 20GB 可用空间

### 软件要求
- **操作系统**: Ubuntu 20.04+, CentOS 7+, Debian 10+ 或其他主流 Linux 发行版
- **Docker**: 20.10+
- **Docker Compose**: 2.0+ 或 docker-compose 1.29+
- **Git**: 用于拉取代码

### 网络要求
- 能访问互联网（用于拉取 Docker 镜像、调用 DashScope API）
- 开放端口 80（或自定义端口）用于 Web 访问
- 能访问飞书 API（open.feishu.cn）

---

## 快速部署

如果服务器已安装 Docker 和 Git，可以使用一键部署脚本：

```bash
# 1. 克隆代码到用户主目录（推荐）
git clone <your-repo-url> ~/feishu-hr-translator
cd ~/feishu-hr-translator

# 2. 配置环境变量（必须配置在项目根目录的 .env 文件）
cp deploy/.env.production .env
vim .env  # 编辑配置文件，填写必要参数

# 3. 执行部署脚本
cd deploy
chmod +x deploy.sh
./deploy.sh
```

**重要提示**：
- 环境变量文件必须放在**项目根目录** `~/feishu-hr-translator/.env`
- 默认端口为 8888（可在 .env 中通过 WEB_PORT 修改）
- 部署完成后访问 `http://服务器IP:8888` 使用 Web UI

---

## 详细步骤

### 1. 安装 Docker 和 Docker Compose

#### Ubuntu/Debian

```bash
# 更新软件包
sudo apt-get update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo apt-get install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

#### CentOS/RHEL

```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo yum install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

### 2. 克隆项目代码

```bash
# 创建项目目录
sudo mkdir -p /opt/feishu-hr-translator
cd /opt/feishu-hr-translator

# 克隆代码（如果使用 Git）
git clone <your-repo-url> .

# 或者上传代码包
# scp -r feishu-hr-translator.tar.gz user@server:/opt/
# cd /opt && tar -xzf feishu-hr-translator.tar.gz
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp deploy/.env.production .env

# 编辑配置文件
vim .env
```

**必须修改的配置项：**

```ini
# 服务器地址（改为实际 IP 或域名）
APP_BASE_URL=http://your-server-ip

# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
FEISHU_BOT_VERIFICATION_TOKEN=xxxxxxxxxxxx
FEISHU_BOT_ENCRYPT_KEY=xxxxxxxxxxxx
FEISHU_DEFAULT_CHAT_ID=oc_xxxxxxxxxxxx

# DashScope API Key
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# JWT 密钥（生产环境必须修改！）
JWT_SECRET_KEY=your-random-secret-key-here

# 管理员密码（首次登录后请立即修改）
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=your-secure-password
```

**可选配置项：**

```ini
# 自定义 Web 端口（默认 80）
WEB_PORT=8080

# 启用自动同步
AUTO_SYNC_ENABLED=true
AUTO_SYNC_TIME=02:00
AUTO_SYNC_LOOKBACK_HOURS=24
```

### 4. 执行部署

```bash
cd deploy

# 赋予执行权限
chmod +x deploy.sh

# 执行部署（自动完成构建、启动）
./deploy.sh
```

部署脚本会自动完成以下操作：
1. 检查系统依赖（Docker、Docker Compose）
2. 检查环境配置文件
3. 创建必要的数据目录
4. 构建 Docker 镜像（Backend + Frontend）
5. 启动所有服务
6. 进行健康检查
7. 显示访问信息

### 5. 验证部署

部署完成后，执行以下检查：

```bash
# 查看容器状态
docker ps

# 应该看到两个容器运行中：
# - feishu-hr-backend
# - feishu-hr-frontend

# 查看服务日志
docker-compose -f deploy/docker-compose.production.yml logs -f

# 测试后端健康检查
curl http://localhost/healthz

# 预期输出: {"ok": true}
```

### 6. 访问 Web UI

在浏览器中访问：`http://服务器IP`

**首次登录：**
- 用户名：`admin`（或 .env 中配置的 DEFAULT_ADMIN_USERNAME）
- 密码：.env 中配置的 DEFAULT_ADMIN_PASSWORD

---

## 配置说明

### 端口配置

**默认端口**：
- **Web UI（Nginx）**: 端口 8888
- **Backend API**: 通过 Nginx 反向代理，路径 `/api/*`
- **Webhook 端点**: 通过 Nginx 反向代理，路径 `/webhook/*`

**修改端口**：

在项目根目录的 `.env` 文件中设置（注意不是 deploy/.env）：

```ini
WEB_PORT=8888  # 修改为其他端口，如 9000
```

**注意事项**：
- `deploy/.env` 仅用于 docker-compose 变量替换
- 容器内的环境变量从项目根目录的 `.env` 加载
- 修改端口后需要重启容器（见下方"环境变量生效方法"）

### 数据持久化

数据目录挂载到容器外：

```
项目根目录/
├── data/
│   ├── reports_slim.csv      # 报告数据
│   └── okr_cache.json         # OKR 缓存
└── secrets/                   # 敏感凭证（可选）
    └── gs.json                # Google Service Account
```

**备份建议：**

```bash
# 定期备份 data 目录
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 恢复备份
tar -xzf backup-20231215.tar.gz
```

### 防火墙配置

如果服务器启用了防火墙，需要开放端口：

#### UFW (Ubuntu)

```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

#### firewalld (CentOS)

```bash
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

---

## 运维管理

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f deploy/docker-compose.production.yml logs -f

# 查看特定服务日志
docker-compose -f deploy/docker-compose.production.yml logs -f backend
docker-compose -f deploy/docker-compose.production.yml logs -f frontend

# 查看最近 100 行日志
docker-compose -f deploy/docker-compose.production.yml logs --tail=100
```

### 重启服务

```bash
cd ~/feishu-hr-translator/deploy

# 重启所有服务
docker-compose -f docker-compose.production.yml restart

# 重启特定服务
docker-compose -f docker-compose.production.yml restart backend
docker-compose -f docker-compose.production.yml restart frontend
```

### ⚠️ 环境变量生效方法（重要）

**问题**：修改 `.env` 文件后，使用 `docker-compose restart` 不会重新加载环境变量！

**原因**：`restart` 命令只重启容器进程，不会重新创建容器，因此不会读取新的 `env_file`。

**正确方法**：

```bash
cd ~/feishu-hr-translator/deploy

# 方法1：完全停止后重新启动（推荐）
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# 方法2：强制重新创建容器
docker-compose -f docker-compose.production.yml up -d --force-recreate

# 方法3：重新构建并启动
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

**验证环境变量**：

```bash
# 检查容器内的环境变量
docker exec feishu-hr-backend env | grep AUTO_SYNC_TIME
docker exec feishu-hr-backend env | grep WEB_PORT
```

### 停止服务

```bash
cd /opt/feishu-hr-translator/deploy

# 停止服务（保留容器）
docker-compose -f docker-compose.production.yml stop

# 停止并删除容器
docker-compose -f docker-compose.production.yml down

# 停止并删除容器、网络、镜像
docker-compose -f docker-compose.production.yml down --rmi all
```

### 更新部署

```bash
cd /opt/feishu-hr-translator

# 方式一：使用更新脚本（推荐）
cd deploy
chmod +x update.sh
./update.sh

# 方式二：手动更新
git pull
cd deploy
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### 数据库备份

定期备份数据目录：

```bash
# 创建备份脚本
cat > /opt/backup-feishu.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/feishu-hr-translator"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/feishu-data-$DATE.tar.gz -C $PROJECT_DIR data/

# 保留最近 7 天的备份
find $BACKUP_DIR -name "feishu-data-*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/backup-feishu.sh

# 添加到 crontab（每天凌晨 3 点备份）
echo "0 3 * * * /opt/backup-feishu.sh" | crontab -
```

### 监控服务状态

```bash
# 查看容器资源使用
docker stats feishu-hr-backend feishu-hr-frontend

# 查看容器详细信息
docker inspect feishu-hr-backend

# 检查服务健康状态
docker ps --filter "name=feishu-hr" --format "table {{.Names}}\t{{.Status}}"
```

---

## 故障排查

### 问题 1: 容器无法启动

**现象**: `docker ps` 看不到容器运行

**排查步骤**:

```bash
# 查看容器日志
cd ~/feishu-hr-translator/deploy
docker-compose -f docker-compose.production.yml logs

# 检查 .env 配置是否正确（注意是项目根目录的 .env）
cat ~/feishu-hr-translator/.env | grep -E "FEISHU|DASHSCOPE"

# 检查端口是否被占用
sudo netstat -tlnp | grep :8888  # 或你配置的端口
```

**可能原因及解决方法**:

1. **端口被占用** → 修改项目根目录 `.env` 中的 `WEB_PORT`
2. **配置错误** → 检查 `.env` 必填项
3. **镜像构建失败** → 重新构建：
   ```bash
   docker-compose -f docker-compose.production.yml build --no-cache
   docker-compose -f docker-compose.production.yml up -d
   ```
4. **Docker Compose 缓存问题** → 完全清理后重建：
   ```bash
   docker-compose -f docker-compose.production.yml down -v
   docker rm -f feishu-hr-backend feishu-hr-frontend 2>/dev/null || true
   docker rmi feishu-hr-translator_backend feishu-hr-translator_frontend 2>/dev/null || true
   docker builder prune -f
   docker-compose -f docker-compose.production.yml build --no-cache
   docker-compose -f docker-compose.production.yml up -d
   ```

### 问题 2: 后端 API 无法访问

**现象**: Web UI 提示网络错误或 API 超时

**排查步骤**:

```bash
# 检查后端容器状态
docker logs feishu-hr-backend

# 测试后端健康检查
curl http://localhost/healthz
curl http://localhost/api/dashboard/summary

# 进入前端容器检查 Nginx 配置
docker exec feishu-hr-frontend cat /etc/nginx/conf.d/default.conf
```

**可能原因**:
- Backend 未启动 → 查看 backend 容器日志
- Nginx 配置错误 → 检查 `deploy/nginx.conf`
- 网络连接问题 → 检查 Docker 网络 `docker network ls`

### 问题 3: 前端静态资源 404

**现象**: Web UI 页面空白或样式丢失

**排查步骤**:

```bash
# 检查前端容器内的文件
docker exec feishu-hr-frontend ls -la /usr/share/nginx/html

# 重新构建前端镜像
docker-compose -f deploy/docker-compose.production.yml build --no-cache frontend
docker-compose -f deploy/docker-compose.production.yml up -d frontend
```

### 问题 4: Web UI 登录失败（500 错误）

**现象**: 访问登录页面正常，但点击登录后返回 500 错误

**排查步骤**:

```bash
# 查看后端日志
docker logs feishu-hr-backend | tail -50

# 检查是否有 SQLAlchemy 相关错误
docker logs feishu-hr-backend | grep -i "readonly database"
```

**可能原因及解决方法**:

1. **数据库权限问题**（最常见）：
   ```bash
   # 修改 data 目录权限（容器使用 UID 1000）
   sudo chown -R 1000:1000 ~/feishu-hr-translator/data/
   chmod -R 755 ~/feishu-hr-translator/data/

   # 重启后端容器
   docker-compose -f docker-compose.production.yml restart backend
   ```

2. **缺少依赖**：
   ```bash
   # 检查是否缺少 sqlalchemy 等依赖
   docker exec feishu-hr-backend pip list | grep -E "sqlalchemy|python-jose|email-validator"

   # 如果缺少，重新构建镜像
   docker-compose -f docker-compose.production.yml build --no-cache backend
   docker-compose -f docker-compose.production.yml up -d backend
   ```

3. **数据库文件损坏**：
   ```bash
   # 删除旧数据库，重新初始化
   rm ~/feishu-hr-translator/data/users.db
   docker-compose -f docker-compose.production.yml restart backend
   ```

### 问题 5: 飞书 Webhook 无法接收

**现象**: 飞书消息发送后无响应

**排查步骤**:

```bash
# 检查后端日志中的 Webhook 请求
docker logs feishu-hr-backend | grep webhook

# 检查 Nginx 配置是否包含 /webhook/ 路由
docker exec feishu-hr-frontend cat /etc/nginx/conf.d/default.conf | grep -A 5 webhook

# 手动测试 Webhook 端点
curl -X POST http://服务器IP:8888/webhook/feishu \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","user_name":"测试","text":"测试内容"}'
```

**可能原因及解决方法**:

1. **Nginx 配置缺少 webhook 路由**：
   ```bash
   # 检查 deploy/nginx.conf 是否包含以下配置
   cat deploy/nginx.conf | grep -A 8 "location /webhook/"

   # 应该有类似以下内容：
   # location /webhook/ {
   #     proxy_pass http://backend:8080/webhook/;
   #     ...
   # }

   # 如果没有，更新配置并重建前端
   docker-compose -f docker-compose.production.yml build --no-cache frontend
   docker-compose -f docker-compose.production.yml up -d frontend
   ```

2. **飞书配置错误** → 检查 `FEISHU_BOT_VERIFICATION_TOKEN`
3. **服务器防火墙阻挡** → 开放端口 `sudo ufw allow 8888`
4. **URL 配置错误** → 确保飞书机器人的回调地址是 `http://服务器IP:8888/webhook/feishu`

### 问题 6: 环境变量修改后不生效

**现象**: 修改 `.env` 文件后，使用 `docker-compose restart` 重启容器，但配置仍然是旧值

**原因**: `docker-compose restart` 只重启进程，不会重新加载 `env_file`

**正确方法**:

```bash
cd ~/feishu-hr-translator/deploy

# 必须先 down 再 up，或使用 --force-recreate
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# 或者
docker-compose -f docker-compose.production.yml up -d --force-recreate
```

**验证**:

```bash
# 检查容器内实际的环境变量值
docker exec feishu-hr-backend env | grep AUTO_SYNC_TIME
```

### 问题 7: 前端 API 连接失败

**现象**: 浏览器控制台显示 API 请求失败（如 `ERR_CONNECTION_REFUSED`）

**排查步骤**:

```bash
# 检查前端的 API_BASE_URL 配置
docker exec feishu-hr-frontend cat /usr/share/nginx/html/assets/*.js | grep -o 'localhost:8080' | head -1
```

**可能原因及解决方法**:

1. **生产模式下使用了 localhost**（已在实际部署中修复）：
   - 检查 `frontend/src/api/client.ts` 是否使用空字符串作为生产环境的 API_BASE_URL
   - 重新构建前端镜像

2. **Nginx 代理配置错误**：
   ```bash
   # 检查 nginx.conf 是否正确配置了 /api/ 代理
   docker exec feishu-hr-frontend cat /etc/nginx/conf.d/default.conf
   ```

### 问题 8: 容器健康检查失败

**现象**: `docker ps` 显示容器状态为 `unhealthy` 或 `starting`

**排查步骤**:

```bash
# 查看健康检查日志
docker inspect feishu-hr-backend | grep -A 20 Health
docker inspect feishu-hr-frontend | grep -A 20 Health

# 手动测试健康检查端点
docker exec feishu-hr-backend curl -f http://localhost:8080/healthz
docker exec feishu-hr-frontend wget -q -O - http://127.0.0.1/health
```

**解决方法**:

- Frontend 健康检查使用 `127.0.0.1` 而不是 `localhost`（Alpine 容器网络问题）
- 如果持续失败，检查服务是否正常启动

### 问题 9: DashScope API 调用失败

**现象**: 日志显示 "(离线模式)" 或 API 超时

**排查步骤**:

```bash
# 检查 API Key 配置
docker exec feishu-hr-backend env | grep DASHSCOPE

# 测试网络连接
docker exec feishu-hr-backend curl -I https://dashscope.aliyuncs.com

# 手动测试 API
docker exec feishu-hr-backend python3 -c "
from openai import OpenAI
client = OpenAI(api_key='$DASHSCOPE_API_KEY', base_url='https://dashscope.aliyuncs.com/compatible-mode/v1')
response = client.chat.completions.create(model='qwen-max', messages=[{'role':'user','content':'测试'}])
print(response.choices[0].message.content)
"
```

**可能原因**:
- API Key 错误 → 检查 `.env` 中的 `DASHSCOPE_API_KEY`
- 网络不通 → 检查服务器是否能访问阿里云
- 额度用尽 → 登录 DashScope 控制台检查

### 问题 6: 数据丢失

**现象**: 重启后报告数据消失

**排查步骤**:

```bash
# 检查数据卷挂载
docker inspect feishu-hr-backend | grep -A 10 Mounts

# 检查文件权限
ls -la /opt/feishu-hr-translator/data/

# 恢复备份
cd /opt/feishu-hr-translator
tar -xzf /opt/backups/feishu-data-YYYYMMDD.tar.gz
```

**预防措施**:
- 定期备份 `data/` 目录
- 使用外部存储（Google Sheet、飞书多维表格）

---

## 性能优化建议

### 1. 使用外部数据库

CSV 文件适合小规模使用，大规模场景建议切换到：
- **Google Sheet**: 修改 `.env` 中 `STORAGE_DRIVER=sheet`
- **飞书多维表格**: 修改 `.env` 中 `STORAGE_DRIVER=bitable`

### 2. 启用 CDN

如果用户分布广泛，建议前端静态资源使用 CDN：
- 将构建产物上传到 CDN
- 修改 `frontend/vite.config.ts` 中的 `base` 配置

### 3. 增加容器资源限制

在 `docker-compose.production.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 4. 配置日志轮转

避免日志文件过大，已在 docker-compose 中配置：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 安全建议

1. **修改默认密码**: 首次登录后立即修改管理员密码
2. **使用 HTTPS**: 在 Nginx 前配置 SSL 证书（Let's Encrypt）
3. **限制访问 IP**: 在防火墙中限制只允许特定 IP 访问
4. **定期更新**: 及时更新 Docker 镜像和依赖包
5. **环境隔离**: 生产环境不要使用 `--reload` 模式

---

## 生产环境 HTTPS 配置（可选）

如果需要启用 HTTPS，可以使用 Let's Encrypt 免费证书：

```bash
# 1. 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. 获取证书（需要域名）
sudo certbot --nginx -d your-domain.com

# 3. 自动续期
sudo certbot renew --dry-run
```

或者手动配置 SSL，修改 `deploy/nginx.conf`：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # ... 其他配置 ...
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 联系支持

如遇到问题，请：
1. 查看日志文件
2. 检查本文档的故障排查部分
3. 提交 Issue 到项目仓库

---

**祝部署顺利！**
