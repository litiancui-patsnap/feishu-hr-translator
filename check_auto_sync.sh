#!/bin/bash
# 自动同步配置检查脚本

echo "=== 1. 检查项目根目录的 .env 配置 ==="
cat ~/.env 2>/dev/null | grep -E "AUTO_SYNC" || echo "未找到 ~/.env 文件"

echo ""
echo "=== 2. 检查 feishu-hr-translator/.env 配置 ==="
cat ~/feishu-hr-translator/.env 2>/dev/null | grep -E "AUTO_SYNC" || echo "未找到 ~/feishu-hr-translator/.env 文件"

echo ""
echo "=== 3. 检查容器内的环境变量 ==="
docker exec feishu-hr-backend env | grep -E "AUTO_SYNC"

echo ""
echo "=== 4. 检查后端日志中的自动同步信息 ==="
docker logs feishu-hr-backend 2>&1 | grep -i "auto_sync" | tail -20

echo ""
echo "=== 5. 检查容器启动时间 ==="
docker inspect feishu-hr-backend | grep -A 5 "StartedAt"

echo ""
echo "=== 6. 当前服务器时间 ==="
date

echo ""
echo "=== 7. 容器内时间 ==="
docker exec feishu-hr-backend date
