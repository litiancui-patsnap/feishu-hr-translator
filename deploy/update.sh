#!/bin/bash

# 快速更新脚本 - 拉取最新代码并重新部署

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}[INFO]${NC} 停止现有服务..."
cd "$(dirname "$0")"

if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.production.yml down
else
    docker compose -f docker-compose.production.yml down
fi

echo -e "${GREEN}[INFO]${NC} 拉取最新代码..."
cd ..
git pull

echo -e "${GREEN}[INFO]${NC} 重新构建并启动..."
cd deploy
./deploy.sh

echo -e "${GREEN}[INFO]${NC} 更新完成！"
