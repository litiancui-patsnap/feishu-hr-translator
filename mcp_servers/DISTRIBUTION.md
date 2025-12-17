# LLM Translator MCP Server - 分享与分发指南

本文档介绍如何将 LLM Translator MCP Server 作为独立工具分享给其他团队。

---

## 📦 方案总览

| 方案 | 适用场景 | 难度 | 独立性 |
|------|---------|------|-------|
| [方案 1：文件夹复制](#方案-1文件夹复制) | 快速测试 | ⭐ | ❌ 依赖父项目 |
| [方案 2：Git Submodule](#方案-2git-submodule) | 多项目共享 | ⭐⭐ | ⚠️ 部分独立 |
| [方案 3：独立 Git 仓库](#方案-3独立-git-仓库) | 完全独立分发 | ⭐⭐⭐ | ✅ 完全独立 |
| [方案 4：PyPI 包发布](#方案-4pypi-包发布) | 公开分享 | ⭐⭐⭐⭐ | ✅ pip install |
| [方案 5：Docker 镜像](#方案-5docker-镜像) | 生产环境 | ⭐⭐⭐ | ✅ 开箱即用 |

---

## 方案 1：文件夹复制

**适用场景**：快速给同事测试，不需要版本管理

### 操作步骤

```bash
# 1. 创建独立副本
cp -r mcp_servers /path/to/share/llm-translator-mcp

# 2. 复制必要的依赖文件
cp -r src/ai /path/to/share/llm-translator-mcp/src/
cp -r src/schemas.py /path/to/share/llm-translator-mcp/src/
cp -r src/utils /path/to/share/llm-translator-mcp/src/

# 3. 创建独立的 requirements.txt
cat > /path/to/share/llm-translator-mcp/requirements.txt << 'EOF'
httpx>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
jinja2>=3.1.0
EOF

# 4. 打包为 zip
cd /path/to/share
zip -r llm-translator-mcp.zip llm-translator-mcp/
```

### 使用方式

接收者操作：
```bash
# 1. 解压
unzip llm-translator-mcp.zip
cd llm-translator-mcp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 测试运行
export DASHSCOPE_API_KEY="your_key"
python -m llm_translator
```

**优点**：简单快速
**缺点**：不利于版本更新，文件冗余

---

## 方案 2：Git Submodule

**适用场景**：多个项目共享同一个 MCP Server，保持同步更新

### 步骤 1：创建独立分支

在当前仓库创建独立分支：

```bash
# 在主项目中
cd /path/to/feishu-hr-translator

# 创建 orphan 分支（无历史记录）
git checkout --orphan mcp-server-standalone

# 清空工作区
git rm -rf .

# 仅复制 MCP Server 相关文件
git checkout master -- mcp_servers/
git checkout master -- src/ai/
git checkout master -- src/schemas.py
git checkout master -- src/utils/

# 创建根目录 README
cat > README.md << 'EOF'
# LLM Translator MCP Server

独立的 AI 内容翻译 MCP Server。

查看文档：[mcp_servers/README.md](mcp_servers/README.md)
EOF

# 提交
git add .
git commit -m "Initial standalone MCP Server"
git push origin mcp-server-standalone
```

### 步骤 2：其他项目引用

```bash
# 在其他项目中
cd /path/to/other-project

# 添加 submodule
git submodule add -b mcp-server-standalone \
  https://github.com/your-org/feishu-hr-translator.git \
  lib/llm-translator

# 使用
cd lib/llm-translator
pip install -r mcp_servers/requirements.txt
python -m mcp_servers.llm_translator
```

**优点**：自动同步更新
**缺点**：需要 Git 操作，依赖原仓库

---

## 方案 3：独立 Git 仓库

**适用场景**：完全独立的开源项目，最佳实践 ✅ **推荐**

### 步骤 1：重构为独立包

创建新的独立仓库结构：

```
llm-translator-mcp/
├── llm_translator_mcp/          # 包名
│   ├── __init__.py
│   ├── server.py                # 重命名 llm_translator.py
│   ├── ai/
│   │   ├── __init__.py
│   │   └── qwen.py              # 从 src/ai/qwen.py 复制
│   ├── models.py                # 从 src/schemas.py 提取必要部分
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   └── test_server.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

详细步骤见：[STANDALONE_SETUP.md](#附录-standalone_setupmd)

**优点**：完全独立，最佳实践
**缺点**：需要重构代码

---

## 方案 4：PyPI 包发布

**适用场景**：公开分享，任何人都可以 `pip install`

### 前置条件

完成方案 3 的独立仓库重构

### 发布步骤

```bash
# 1. 安装构建工具
pip install build twine

# 2. 构建包
cd llm-translator-mcp
python -m build

# 3. 测试上传（TestPyPI）
twine upload --repository testpypi dist/*

# 4. 测试安装
pip install --index-url https://test.pypi.org/simple/ mcp-llm-translator

# 5. 正式发布
twine upload dist/*
```

### 使用方式

其他团队使用：
```bash
# 1. 安装
pip install mcp-llm-translator

# 2. 使用
python -c "
from llm_translator_mcp import LLMTranslatorServer
import asyncio

async def test():
    server = LLMTranslatorServer(api_key='your_key')
    result = await server.translate_to_hr_language('测试文本')
    print(result)

asyncio.run(test())
"
```

**优点**：最方便，支持版本管理
**缺点**：需要公开（或企业内部 PyPI）

---

## 方案 5：Docker 镜像

**适用场景**：生产环境，无需配置 Python 环境

### Dockerfile

创建 `mcp_servers/Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml .
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY llm_translator.py .
COPY __init__.py .
COPY ../src/ai ./src/ai/
COPY ../src/schemas.py ./src/
COPY ../src/utils ./src/utils/

# 暴露端口（如果提供 HTTP API）
# EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV DASHSCOPE_API_KEY=""

# 默认命令
CMD ["python", "-m", "llm_translator"]
```

### 构建和分发

```bash
# 1. 构建镜像
cd mcp_servers
docker build -t llm-translator-mcp:latest .

# 2. 推送到镜像仓库
docker tag llm-translator-mcp:latest your-org/llm-translator-mcp:latest
docker push your-org/llm-translator-mcp:latest

# 3. 导出为 tar（离线分享）
docker save llm-translator-mcp:latest > llm-translator-mcp.tar
```

### 使用方式

其他团队使用：
```bash
# 方式 1：从镜像仓库拉取
docker pull your-org/llm-translator-mcp:latest
docker run -e DASHSCOPE_API_KEY=your_key llm-translator-mcp:latest

# 方式 2：离线加载
docker load < llm-translator-mcp.tar
docker run -e DASHSCOPE_API_KEY=your_key llm-translator-mcp:latest
```

**优点**：开箱即用，环境隔离
**缺点**：镜像体积较大（~500MB）

---

## 🎯 推荐方案

### 快速测试（内部同事）
→ **方案 1**：文件夹复制 + zip 分享

### 团队协作（多项目共享）
→ **方案 3**：独立 Git 仓库

### 公开分享（开源社区）
→ **方案 4**：PyPI 包发布

### 生产部署（企业环境）
→ **方案 5**：Docker 镜像

---

## 📋 检查清单

分享前确认：

- [ ] 更新 README.md 文档
- [ ] 添加使用示例
- [ ] 编写测试用例
- [ ] 添加 LICENSE 文件
- [ ] 移除敏感信息（API keys）
- [ ] 版本号管理（pyproject.toml）
- [ ] 添加 CHANGELOG.md
- [ ] 设置 .gitignore

---

## 附录 A：快速分享脚本

创建 `scripts/package_mcp_server.sh`：

```bash
#!/bin/bash
# 快速打包 MCP Server 为独立分发包

set -e

VERSION="0.1.0"
OUTPUT_DIR="dist/mcp-llm-translator-$VERSION"

echo "📦 打包 MCP Server v$VERSION..."

# 创建输出目录
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# 复制核心文件
cp -r mcp_servers/* "$OUTPUT_DIR/"
mkdir -p "$OUTPUT_DIR/src"
cp -r src/ai "$OUTPUT_DIR/src/"
cp src/schemas.py "$OUTPUT_DIR/src/"
cp -r src/utils "$OUTPUT_DIR/src/"

# 创建 requirements.txt
cat > "$OUTPUT_DIR/requirements.txt" << 'EOF'
httpx>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
jinja2>=3.1.0
EOF

# 创建使用说明
cat > "$OUTPUT_DIR/INSTALL.md" << 'EOF'
# 安装说明

1. 安装依赖：
   pip install -r requirements.txt

2. 配置 API Key：
   export DASHSCOPE_API_KEY="your_key"

3. 运行测试：
   python -m llm_translator

4. 查看文档：
   详见 README.md
EOF

# 打包
cd dist
zip -r "mcp-llm-translator-$VERSION.zip" "mcp-llm-translator-$VERSION/"

echo "✅ 打包完成：dist/mcp-llm-translator-$VERSION.zip"
```

使用：
```bash
chmod +x scripts/package_mcp_server.sh
./scripts/package_mcp_server.sh
```

---

## 附录 B：版本更新流程

更新版本时：

1. 修改 `mcp_servers/pyproject.toml` 版本号
2. 更新 `CHANGELOG.md`
3. 创建 Git tag：
   ```bash
   git tag -a mcp-v0.2.0 -m "Release v0.2.0"
   git push origin mcp-v0.2.0
   ```
4. 重新构建分发包

---

## 📞 支持

- 问题反馈：GitHub Issues
- 文档：[README.md](README.md)
- 快速开始：[QUICKSTART.md](QUICKSTART.md)

