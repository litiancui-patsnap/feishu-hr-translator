#!/bin/bash

# Bash 脚本 - 创建部署包（适用于 Git Bash 或 Linux/Mac）

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}创建 Feishu HR Translator 部署包${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""

# 设置变量
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="feishu-hr-deploy-${TIMESTAMP}.tar.gz"
TEMP_DIR="./deploy-temp"

echo -e "${YELLOW}[1/5] 检查必要文件...${NC}"

# 检查关键目录
REQUIRED_DIRS=("src" "frontend" "deploy" "data")
MISSING_DIRS=()

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
    echo -e "${RED}错误：缺少以下目录：${NC}"
    for dir in "${MISSING_DIRS[@]}"; do
        echo -e "${RED}  - $dir${NC}"
    done
    exit 1
fi

echo -e "${GREEN}✓ 所有必要文件存在${NC}"
echo ""

echo -e "${YELLOW}[2/5] 创建临时目录...${NC}"

# 清理旧的临时目录
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo -e "${GREEN}✓ 临时目录已创建${NC}"
echo ""

echo -e "${YELLOW}[3/5] 复制文件...${NC}"

# 复制目录
cp -r src "$TEMP_DIR/"
cp -r frontend "$TEMP_DIR/"
cp -r deploy "$TEMP_DIR/"
cp -r data "$TEMP_DIR/"

# 复制文件
cp requirements.txt "$TEMP_DIR/"
cp .env.example "$TEMP_DIR/"
cp README.md "$TEMP_DIR/"

if [ -f .dockerignore ]; then
    cp .dockerignore "$TEMP_DIR/"
fi

echo -e "${GREEN}✓ 文件复制完成${NC}"
echo ""

echo -e "${YELLOW}[4/5] 清理不需要的文件...${NC}"

# 删除不需要的文件和目录
find "$TEMP_DIR" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -type d -name ".vite" -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

echo -e "${YELLOW}[5/5] 创建压缩包...${NC}"

# 创建 tar.gz 包
tar -czf "$PACKAGE_NAME" -C "$TEMP_DIR" .

echo -e "${GREEN}✓ 压缩包创建完成${NC}"
echo ""

# 清理临时目录
rm -rf "$TEMP_DIR"

# 显示结果
PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}部署包创建成功！${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${CYAN}文件名: $PACKAGE_NAME${NC}"
echo -e "${CYAN}大小: $PACKAGE_SIZE${NC}"
echo -e "${CYAN}位置: $(pwd)/$PACKAGE_NAME${NC}"
echo ""

echo -e "${YELLOW}下一步操作：${NC}"
echo -e "1. 上传到服务器："
echo -e "${GRAY}   scp $PACKAGE_NAME root@your-server-ip:/tmp/${NC}"
echo ""
echo -e "2. SSH 登录服务器："
echo -e "${GRAY}   ssh root@your-server-ip${NC}"
echo ""
echo -e "3. 解压文件："
echo -e "${GRAY}   cd /root/feishu-hr-translator${NC}"
echo -e "${GRAY}   tar -xzf /tmp/$PACKAGE_NAME${NC}"
echo ""
echo -e "4. 执行部署："
echo -e "${GRAY}   cd deploy${NC}"
echo -e "${GRAY}   chmod +x *.sh${NC}"
echo -e "${GRAY}   ./deploy.sh${NC}"
echo ""
