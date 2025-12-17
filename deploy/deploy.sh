#!/bin/bash

# Feishu HR Translator 部署脚本
# 用于 Linux 服务器快速部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的命令
check_requirements() {
    log_info "检查系统依赖..."

    if ! command -v docker &> /dev/null; then
        log_error "未找到 Docker，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "未找到 Docker Compose，请先安装 Docker Compose"
        exit 1
    fi

    log_info "系统依赖检查完成"
}

# 检查 .env 文件
check_env_file() {
    log_info "检查环境配置文件..."

    if [ ! -f "../.env" ]; then
        log_warn ".env 文件不存在，从 .env.example 复制..."
        cp ../.env.example ../.env
        log_warn "请编辑 .env 文件，配置必要的参数："
        log_warn "  - FEISHU_APP_ID / FEISHU_APP_SECRET"
        log_warn "  - DASHSCOPE_API_KEY"
        log_warn "  - FEISHU_DEFAULT_CHAT_ID"
        log_warn "  - APP_BASE_URL (改为服务器的实际地址)"
        read -p "配置完成后按回车继续..."
    fi

    log_info "环境配置检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."

    mkdir -p ../data
    mkdir -p ../secrets

    # 检查必要的数据文件
    if [ ! -f "../data/reports_slim.csv" ]; then
        log_info "初始化 reports_slim.csv..."
        echo "report_id,user_id,user_name,report_text,okr_summary,translated_report,risk_items,okr_confidence,created_at,parsed_ts,period" > ../data/reports_slim.csv
    fi

    if [ ! -f "../data/okr_cache.json" ]; then
        log_info "初始化 okr_cache.json..."
        echo "[]" > ../data/okr_cache.json
    fi

    log_info "目录创建完成"
}

# 构建镜像
build_images() {
    log_info "开始构建 Docker 镜像..."

    cd "$(dirname "$0")"

    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml build
    else
        docker compose -f docker-compose.production.yml build
    fi

    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."

    cd "$(dirname "$0")"

    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml up -d
    else
        docker compose -f docker-compose.production.yml up -d
    fi

    log_info "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "等待服务就绪..."
    sleep 10

    cd "$(dirname "$0")"

    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml ps
    else
        docker compose -f docker-compose.production.yml ps
    fi

    log_info "检查后端健康状态..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml exec -T backend curl -f http://localhost:8080/healthz || log_warn "后端健康检查失败"
    else
        docker compose -f docker-compose.production.yml exec -T backend curl -f http://localhost:8080/healthz || log_warn "后端健康检查失败"
    fi
}

# 显示访问信息
show_info() {
    log_info "=========================================="
    log_info "部署完成！"
    log_info "=========================================="
    log_info "Web UI: http://$(hostname -I | awk '{print $1}'):${WEB_PORT:-80}"
    log_info "后端 API: http://$(hostname -I | awk '{print $1}'):${WEB_PORT:-80}/api"
    log_info ""
    log_info "查看日志："
    log_info "  docker-compose -f deploy/docker-compose.production.yml logs -f"
    log_info ""
    log_info "停止服务："
    log_info "  docker-compose -f deploy/docker-compose.production.yml down"
    log_info ""
    log_info "重启服务："
    log_info "  docker-compose -f deploy/docker-compose.production.yml restart"
    log_info "=========================================="
}

# 主流程
main() {
    log_info "开始部署 Feishu HR Translator..."

    check_requirements
    check_env_file
    create_directories
    build_images
    start_services
    check_services
    show_info

    log_info "部署流程完成！"
}

# 执行主流程
main
