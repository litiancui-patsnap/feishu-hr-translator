# 快速参考 - 常用命令

## 服务管理

```bash
cd ~/feishu-hr-translator/deploy

# 启动服务
docker-compose -f docker-compose.production.yml up -d

# 停止服务
docker-compose -f docker-compose.production.yml down

# 重启服务（不重新加载 .env）
docker-compose -f docker-compose.production.yml restart

# ⚠️ 修改 .env 后重启（重新加载环境变量）
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# 查看状态
docker-compose -f docker-compose.production.yml ps
```

**重要提醒**：
- `restart` 命令不会重新加载 `.env` 文件！
- 修改环境变量后必须使用 `down` + `up`

## 日志查看

```bash
# 实时查看所有日志
docker-compose -f docker-compose.production.yml logs -f

# 查看后端日志
docker-compose -f docker-compose.production.yml logs -f backend

# 查看前端日志
docker-compose -f docker-compose.production.yml logs -f frontend

# 查看最近 100 行
docker-compose -f docker-compose.production.yml logs --tail=100
```

## 健康检查

```bash
# 后端健康检查
curl http://localhost/healthz

# 查看容器状态
docker ps

# 执行健康检查脚本
cd /opt/feishu-hr-translator/deploy
./check-health.sh
```

## 更新部署

```bash
cd /opt/feishu-hr-translator

# 拉取最新代码
git pull

# 方式一：使用更新脚本
cd deploy && ./update.sh

# 方式二：手动更新
cd deploy
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

## 数据备份

```bash
# 手动备份
cd /opt/feishu-hr-translator
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 查看备份
ls -lh backup-*.tar.gz

# 恢复备份
tar -xzf backup-20231215.tar.gz
```

## 故障排查

```bash
# 查看容器详细信息
docker inspect feishu-hr-backend

# 进入容器 shell
docker exec -it feishu-hr-backend bash

# 查看容器资源使用
docker stats feishu-hr-backend feishu-hr-frontend

# 检查端口占用
netstat -tlnp | grep :80

# 查看环境变量
docker exec feishu-hr-backend env | grep FEISHU

# 检查 data 目录权限（如果登录失败 500 错误）
ls -la ~/feishu-hr-translator/data/
sudo chown -R 1000:1000 ~/feishu-hr-translator/data/
```

## 常见问题快速修复

```bash
# 问题1：环境变量修改后不生效
cd ~/feishu-hr-translator/deploy
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# 问题2：登录失败 500 错误（数据库权限）
sudo chown -R 1000:1000 ~/feishu-hr-translator/data/
docker-compose -f docker-compose.production.yml restart backend

# 问题3：完全清理后重建
docker-compose -f docker-compose.production.yml down -v
docker rm -f feishu-hr-backend feishu-hr-frontend 2>/dev/null || true
docker rmi feishu-hr-translator_backend feishu-hr-translator_frontend 2>/dev/null || true
docker builder prune -f
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# 问题4：测试 Webhook 端点
curl -X POST http://localhost:8888/webhook/feishu \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","user_name":"测试","text":"测试内容"}'

# 问题5：验证环境变量是否加载
docker exec feishu-hr-backend env | grep AUTO_SYNC_TIME
docker exec feishu-hr-backend env | grep WEB_PORT
```

## 访问地址

```bash
# Web UI
http://服务器IP:8888

# 健康检查
http://服务器IP:8888/healthz

# Webhook 端点（飞书机器人配置）
http://服务器IP:8888/webhook/feishu
```

## 清理空间

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 一键清理所有未使用资源
docker system prune -a --volumes
```

## 访问地址

- **Web UI**: http://服务器IP
- **API 文档**: http://服务器IP/docs
- **健康检查**: http://服务器IP/healthz

## 默认账号

- **用户名**: admin（可在 .env 中修改）
- **密码**: 见 .env 中的 DEFAULT_ADMIN_PASSWORD

## 配置文件位置

- **环境配置**: `/opt/feishu-hr-translator/.env`
- **数据目录**: `/opt/feishu-hr-translator/data/`
- **报告数据**: `/opt/feishu-hr-translator/data/reports_slim.csv`
- **OKR 缓存**: `/opt/feishu-hr-translator/data/okr_cache.json`

## 常见端口

- `80`: 前端 Web UI（可在 .env 中通过 WEB_PORT 修改）
- `8080`: 后端 API（内部，不对外暴露）

## 应急操作

```bash
# 快速重启（保留数据）
docker-compose -f docker-compose.production.yml restart

# 完全重建（清除容器，保留数据）
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# 重建镜像（代码更新后）
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# 查看实时资源使用
watch -n 1 docker stats
```

## 性能监控

```bash
# 查看容器资源
docker stats --no-stream

# 查看磁盘使用
df -h
du -sh /opt/feishu-hr-translator/data/*

# 查看内存使用
free -h

# 查看 CPU 负载
uptime
```

## 网络诊断

```bash
# 测试后端连接
curl -v http://localhost:8080/healthz

# 测试前端
curl -I http://localhost

# 测试 API
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# 查看网络配置
docker network ls
docker network inspect deploy_app-network
```
