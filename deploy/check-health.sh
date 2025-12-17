#!/bin/bash

# 服务健康检查脚本

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Feishu HR Translator 健康检查"
echo "=========================================="
echo ""

# 检查 Docker 服务
echo -n "检查 Docker 服务... "
if systemctl is-active --quiet docker; then
    echo -e "${GREEN}运行中${NC}"
else
    echo -e "${RED}未运行${NC}"
    exit 1
fi

# 检查容器状态
echo ""
echo "容器状态："
cd "$(dirname "$0")"

if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

$COMPOSE_CMD -f docker-compose.production.yml ps

# 检查后端健康
echo ""
echo -n "检查后端健康... "
if $COMPOSE_CMD -f docker-compose.production.yml exec -T backend curl -sf http://localhost:8080/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}正常${NC}"
else
    echo -e "${RED}异常${NC}"
fi

# 检查前端健康
echo -n "检查前端健康... "
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}正常${NC}"
else
    echo -e "${RED}异常${NC}"
fi

# 检查端口监听
echo ""
echo "端口监听状态："
netstat -tlnp 2>/dev/null | grep -E ":(80|8080)" || ss -tlnp | grep -E ":(80|8080)"

# 检查磁盘使用
echo ""
echo "数据目录磁盘使用："
du -sh ../data/

# 检查最近的日志
echo ""
echo "最近的日志（最后 10 行）："
$COMPOSE_CMD -f docker-compose.production.yml logs --tail=10

echo ""
echo "=========================================="
echo "健康检查完成"
echo "=========================================="
