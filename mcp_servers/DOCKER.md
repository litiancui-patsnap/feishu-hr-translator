# LLM Translator MCP Server - Docker 使用指南

## 📦 Docker 分享方式

### 方式 1：构建和运行（本地开发）

```bash
# 进入项目根目录
cd /path/to/feishu-hr-translator

# 构建镜像
docker build -f mcp_servers/Dockerfile -t llm-translator-mcp:latest .

# 运行测试
docker run --rm \
  -e DASHSCOPE_API_KEY="your_api_key" \
  llm-translator-mcp:latest

# 或使用 docker-compose
cd mcp_servers
docker-compose up
```

---

### 方式 2：导出镜像（离线分享）

**适用场景**：内网环境，无法访问镜像仓库

#### 步骤 1：导出镜像

```bash
# 构建镜像
docker build -f mcp_servers/Dockerfile -t llm-translator-mcp:0.1.0 .

# 导出为 tar 文件
docker save llm-translator-mcp:0.1.0 | gzip > llm-translator-mcp-0.1.0.tar.gz

# 查看文件大小
ls -lh llm-translator-mcp-0.1.0.tar.gz
```

#### 步骤 2：分享给其他团队

将 `llm-translator-mcp-0.1.0.tar.gz` 文件传输给其他团队（U盘、内网文件服务器等）

#### 步骤 3：接收者导入镜像

```bash
# 解压并导入
gunzip -c llm-translator-mcp-0.1.0.tar.gz | docker load

# 验证镜像已导入
docker images | grep llm-translator-mcp

# 运行
docker run --rm \
  -e DASHSCOPE_API_KEY="your_api_key" \
  llm-translator-mcp:0.1.0
```

---

### 方式 3：推送到镜像仓库（推荐）

**适用场景**：有企业 Docker Registry 或使用 Docker Hub

#### 选项 A：Docker Hub（公开）

```bash
# 1. 登录 Docker Hub
docker login

# 2. 打标签
docker tag llm-translator-mcp:latest your-username/llm-translator-mcp:0.1.0
docker tag llm-translator-mcp:latest your-username/llm-translator-mcp:latest

# 3. 推送
docker push your-username/llm-translator-mcp:0.1.0
docker push your-username/llm-translator-mcp:latest
```

**其他团队使用**：
```bash
docker pull your-username/llm-translator-mcp:latest
docker run --rm -e DASHSCOPE_API_KEY="your_key" your-username/llm-translator-mcp:latest
```

#### 选项 B：企业私有仓库

```bash
# 1. 登录企业仓库
docker login registry.your-company.com

# 2. 打标签
docker tag llm-translator-mcp:latest \
  registry.your-company.com/tools/llm-translator-mcp:0.1.0

# 3. 推送
docker push registry.your-company.com/tools/llm-translator-mcp:0.1.0
```

**其他团队使用**：
```bash
docker pull registry.your-company.com/tools/llm-translator-mcp:0.1.0
docker run --rm -e DASHSCOPE_API_KEY="your_key" \
  registry.your-company.com/tools/llm-translator-mcp:0.1.0
```

---

### 方式 4：多架构构建（跨平台）

**适用场景**：同时支持 AMD64 和 ARM64（如 Apple Silicon）

```bash
# 1. 启用 buildx
docker buildx create --use

# 2. 构建多架构镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f mcp_servers/Dockerfile \
  -t your-username/llm-translator-mcp:0.1.0 \
  --push \
  .

# 3. 查看镜像信息
docker buildx imagetools inspect your-username/llm-translator-mcp:0.1.0
```

---

## 🚀 使用场景

### 场景 1：快速测试翻译功能

```bash
docker run --rm -it \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  llm-translator-mcp:latest
```

### 场景 2：交互式使用

```bash
# 进入容器
docker run --rm -it \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  --entrypoint /bin/bash \
  llm-translator-mcp:latest

# 容器内操作
python -c "
from llm_translator import LLMTranslatorServer
import asyncio

async def test():
    server = LLMTranslatorServer(model='qwen-plus')
    result = await server.translate_to_hr_language('测试文本')
    print(result)

asyncio.run(test())
"
```

### 场景 3：作为服务持续运行

修改 `docker-compose.yml`，添加 HTTP API：

```yaml
services:
  llm-translator:
    # ... 其他配置
    ports:
      - "8000:8000"
    command: ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

启动服务：
```bash
docker-compose up -d
curl http://localhost:8000/health
```

### 场景 4：批量处理

```bash
# 挂载本地文件
docker run --rm \
  -v $(pwd)/data:/data \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  llm-translator-mcp:latest \
  python process_batch.py /data/reports.txt
```

---

## 🔧 高级配置

### 自定义环境变量

```bash
docker run --rm \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  -e QWEN_MODEL="qwen-max" \
  -e REQUEST_TIMEOUT_SECONDS="60" \
  -e QWEN_API_MODE="compatible" \
  llm-translator-mcp:latest
```

### 挂载配置文件

```bash
docker run --rm \
  -v $(pwd)/custom_config.json:/app/mcp_config.json:ro \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  llm-translator-mcp:latest
```

### 资源限制

```bash
docker run --rm \
  --memory="512m" \
  --cpus="1.0" \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  llm-translator-mcp:latest
```

---

## 📊 镜像大小优化

### 当前镜像大小

```bash
docker images llm-translator-mcp
# REPOSITORY              TAG       SIZE
# llm-translator-mcp     latest    ~200MB
```

### 优化技巧

1. **使用 slim 基础镜像**（已应用）
   ```dockerfile
   FROM python:3.11-slim  # 而不是 python:3.11
   ```

2. **多阶段构建**（可选）
   ```dockerfile
   # 构建阶段
   FROM python:3.11 AS builder
   RUN pip install --user httpx pydantic jinja2

   # 运行阶段
   FROM python:3.11-slim
   COPY --from=builder /root/.local /root/.local
   ```

3. **清理缓存**（已应用）
   ```dockerfile
   RUN pip install --no-cache-dir ...
   RUN apt-get clean && rm -rf /var/lib/apt/lists/*
   ```

---

## 🐛 故障排查

### 问题 1：构建失败 "No such file or directory: src/ai/qwen.py"

**原因**：Dockerfile 从错误的上下文构建

**解决**：
```bash
# 错误（在 mcp_servers 目录下）
cd mcp_servers
docker build -f Dockerfile .  # ❌

# 正确（在项目根目录）
cd /path/to/feishu-hr-translator
docker build -f mcp_servers/Dockerfile .  # ✅
```

### 问题 2：运行时报错 "ModuleNotFoundError: No module named 'src'"

**原因**：没有正确挂载 src 目录

**解决**：
```bash
# 使用 docker-compose（已配置挂载）
docker-compose up

# 或手动挂载
docker run --rm \
  -v $(pwd)/src:/app/src:ro \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  llm-translator-mcp:latest
```

### 问题 3：API 调用失败

**检查网络**：
```bash
# 测试容器网络
docker run --rm \
  -e DASHSCOPE_API_KEY="sk-xxx" \
  llm-translator-mcp:latest \
  python -c "import httpx; print(httpx.get('https://dashscope.aliyuncs.com').status_code)"
```

---

## 📋 分享检查清单

分享 Docker 镜像前确认：

- [ ] 已测试镜像能正常运行
- [ ] 已移除敏感信息（API keys）
- [ ] 镜像大小合理（< 500MB）
- [ ] 添加了正确的标签和版本号
- [ ] 编写了使用文档
- [ ] 提供了 docker-compose.yml 示例
- [ ] 测试了在不同环境运行（Linux/macOS/Windows）

---

## 📞 支持

- Docker 文档：https://docs.docker.com/
- 项目文档：[README.md](README.md)
- 问题反馈：GitHub Issues

---

## 示例：完整的分享流程

```bash
# ========== 1. 构建镜像 ==========
cd /path/to/feishu-hr-translator
docker build -f mcp_servers/Dockerfile -t llm-translator-mcp:0.1.0 .

# ========== 2. 测试镜像 ==========
docker run --rm -e DASHSCOPE_API_KEY="test_key" llm-translator-mcp:0.1.0

# ========== 3. 导出镜像（离线分享）==========
docker save llm-translator-mcp:0.1.0 | gzip > llm-translator-mcp-0.1.0.tar.gz

# ========== 4. 或推送到仓库（在线分享）==========
docker tag llm-translator-mcp:0.1.0 your-username/llm-translator-mcp:0.1.0
docker push your-username/llm-translator-mcp:0.1.0

# ========== 5. 编写分享文档 ==========
cat > DOCKER_USAGE.md << 'EOF'
# 使用说明

## 方式 1：从导出文件加载
gunzip -c llm-translator-mcp-0.1.0.tar.gz | docker load
docker run --rm -e DASHSCOPE_API_KEY="your_key" llm-translator-mcp:0.1.0

## 方式 2：从仓库拉取
docker pull your-username/llm-translator-mcp:0.1.0
docker run --rm -e DASHSCOPE_API_KEY="your_key" your-username/llm-translator-mcp:0.1.0
EOF

# ========== 6. 分享给其他团队 ==========
# - 发送 .tar.gz 文件（离线）
# - 或分享 docker pull 命令（在线）
# - 附上 DOCKER_USAGE.md 文档
```
