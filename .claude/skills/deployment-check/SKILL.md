---
name: deployment-check
description: 检查 Linux 服务器上的 Docker 部署配置，验证 .env 文件、端口、防火墙、日志等是否正确配置。当用户询问"部署检查"、"环境配置"、"服务器状态"时自动触发。
---

# 部署环境检查技能

当用户询问"部署是否正确"、"环境配置检查"、"服务器设置验证"、"服务状态"等问题时，自动执行以下检查：

## 检查清单

### 1. Docker 服务状态
检查 Docker 和 Docker Compose 是否正确安装和运行：
```bash
docker --version
docker-compose --version
docker-compose -f deploy/docker-compose.yml ps
```

### 2. 环境变量配置
验证关键配置项：
- 检查 `.env` 文件是否存在
- 验证必填字段：
  - `FEISHU_APP_ID` - 飞书应用 ID
  - `FEISHU_APP_SECRET` - 飞书应用密钥
  - `FEISHU_BOT_VERIFICATION_TOKEN` - 机器人验证 Token
  - `FEISHU_DEFAULT_CHAT_ID` - 默认群聊 ID
  - `DASHSCOPE_API_KEY` - DashScope API 密钥
- 确认端口配置（默认 8080）

### 3. 网络连通性测试
```bash
# 本地健康检查
curl http://localhost:8080/healthz

# 飞书 API 连通性
curl -I https://open.feishu.cn

# DashScope API 连通性
curl -I https://dashscope.aliyuncs.com
```

### 4. 防火墙状态检查
```bash
# Ubuntu/Debian
sudo ufw status | grep 8080

# CentOS/RHEL
sudo firewall-cmd --list-ports | grep 8080
```

### 5. 应用日志检查
查看最近的应用日志，识别错误和警告：
```bash
docker-compose -f deploy/docker-compose.yml logs app | tail -50
```

### 6. 数据目录检查
验证数据持久化：
```bash
ls -lh data/
# 应该包含：
# - okr_cache.json
# - report_task_cache.json
# - reports_slim.csv（如果已有数据）
```

### 7. 容器资源使用
```bash
docker stats --no-stream
```

## 输出格式

按照以下格式输出检查结果：

### ✅ 通过项
列出所有正常的配置项

### ⚠️ 警告项
列出需要注意但不影响运行的问题

### ❌ 失败项
列出必须修复的严重问题

### 📊 总体评估
- 健康度评分（优秀/良好/需改进/严重问题）
- 关键问题摘要
- 修复建议（带具体命令）

## 常见问题及解决方案

### 问题 1：无法访问健康检查端点
**可能原因**：
- 容器未启动
- 端口未正确映射
- 防火墙阻止

**解决方案**：
```bash
# 检查容器状态
docker-compose -f deploy/docker-compose.yml ps

# 重启容器
docker-compose -f deploy/docker-compose.yml restart app

# 检查端口绑定
docker-compose -f deploy/docker-compose.yml port app 8080
```

### 问题 2：飞书 API 连接失败
**可能原因**：
- 网络不通
- 配置错误
- Token 过期

**解决方案**：
```bash
# 检查 .env 中的飞书配置
grep FEISHU .env

# 测试网络
ping open.feishu.cn

# 查看日志中的具体错误
docker-compose -f deploy/docker-compose.yml logs app | grep -i feishu
```

### 问题 3：DashScope API 调用失败
**解决方案**：
```bash
# 验证 API Key
grep DASHSCOPE_API_KEY .env

# 测试 API 连通性
curl -I https://dashscope.aliyuncs.com

# 查看相关日志
docker-compose -f deploy/docker-compose.yml logs app | grep -i dashscope
```

## 执行注意事项

1. 运行检查前确保在项目根目录
2. 某些命令可能需要 sudo 权限
3. 首次部署时，某些检查项可能为空属正常
4. 建议在修改配置后运行完整检查
