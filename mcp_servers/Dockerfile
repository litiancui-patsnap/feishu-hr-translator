# LLM Translator MCP Server - Docker Image
# 基于 Python 3.11 slim 镜像构建

FROM python:3.11-slim

LABEL maintainer="Feishu HR Translator Team"
LABEL description="MCP Server for AI-powered content translation"
LABEL version="0.1.0"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    DASHSCOPE_API_KEY="" \
    QWEN_MODEL="qwen-plus" \
    QWEN_API_MODE="text" \
    REQUEST_TIMEOUT_SECONDS="30"

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .
COPY requirements.txt* ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    httpx>=0.24.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0 \
    jinja2>=3.1.0

# 复制 MCP Server 代码
COPY llm_translator.py .
COPY __init__.py .
COPY mcp_config.json .
COPY README.md .
COPY QUICKSTART.md .

# 复制依赖的 src 模块
COPY --from=builder /tmp/src /app/src 2>/dev/null || true

# 如果上面的 COPY 失败，创建 src 目录并添加占位符
# 实际使用时需要在构建时挂载 src 目录
RUN mkdir -p src/ai src/utils && \
    touch src/__init__.py src/ai/__init__.py src/utils/__init__.py

# 健康检查（简单的 Python 语法检查）
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import llm_translator; print('OK')" || exit 1

# 创建非 root 用户
RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app

USER mcp

# 默认命令：运行测试
CMD ["python", "-m", "llm_translator"]

# 如果作为服务运行，可以使用以下命令
# CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
