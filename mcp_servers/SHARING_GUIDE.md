# LLM Translator MCP Server - 分享指南总结

> 本文档总结了如何将 LLM Translator MCP Server 作为独立工具分享给其他团队的所有方式。

---

## 🎯 快速决策树

```
需要分享 MCP Server
│
├─ 给同事快速测试？
│  └─ ✅ 方式 1：ZIP 文件分享（5分钟）
│
├─ 团队内部长期使用？
│  ├─ 有 Git 仓库？
│  │  └─ ✅ 方式 2：Git Submodule 或独立仓库
│  └─ 没有 Git？
│     └─ ✅ 方式 3：Docker 镜像（离线分发）
│
├─ 公开分享给社区？
│  └─ ✅ 方式 4：PyPI 包发布
│
└─ 生产环境部署？
   └─ ✅ 方式 5：Docker 镜像（在线仓库）
```

---

## 📦 方式 1：ZIP 文件分享（最简单）⭐ 推荐新手

### 适用场景
- ✅ 快速给同事测试
- ✅ 内网环境，无法访问外部仓库
- ✅ 不需要版本管理

### 操作步骤

**1. 打包（你的操作）**

```bash
# Windows
scripts\package_mcp_server.bat

# 或直接复制文件夹
# 生成 dist/mcp-llm-translator-0.1.0.zip（约 50KB）
```

**2. 分享**

将 `dist/mcp-llm-translator-0.1.0.zip` 通过以下方式分享：
- 邮件附件
- 企业文件服务器
- U盘拷贝
- 内网聊天工具

**3. 接收者使用**

```bash
# 解压
unzip mcp-llm-translator-0.1.0.zip
cd mcp-llm-translator-0.1.0

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
set DASHSCOPE_API_KEY=your_key  # Windows
export DASHSCOPE_API_KEY=your_key  # Linux/macOS

# 运行测试
python -m llm_translator

# 或 Windows 直接运行
start.bat
```

**优点**：
- ✅ 最简单，5分钟搞定
- ✅ 无需任何额外工具
- ✅ 适合非技术人员

**缺点**：
- ❌ 版本更新需要重新打包分享
- ❌ 文件冗余（包含整个 src/ 目录）

---

## 📦 方式 2：Git 仓库分享

### 选项 A：独立 Git 仓库 ⭐ 推荐团队协作

**适用场景**：
- ✅ 多个项目共享同一个 MCP Server
- ✅ 需要版本管理和更新
- ✅ 开源分享

**步骤 1：创建独立仓库**

```bash
# 1. 在 GitHub/GitLab 创建新仓库
# 仓库名: llm-translator-mcp

# 2. 提取相关文件到新仓库
git clone https://github.com/your-org/llm-translator-mcp.git
cd llm-translator-mcp

# 3. 复制文件（调整目录结构）
# 见 DISTRIBUTION.md 的详细说明

# 4. 推送
git add .
git commit -m "Initial commit"
git push origin main
```

**步骤 2：其他团队使用**

```bash
# 方式 1：克隆完整仓库
git clone https://github.com/your-org/llm-translator-mcp.git
cd llm-translator-mcp
pip install -r requirements.txt
python -m llm_translator

# 方式 2：作为子模块引入
cd your-project
git submodule add https://github.com/your-org/llm-translator-mcp.git lib/llm-translator
```

**优点**：
- ✅ 自动同步更新（`git pull`）
- ✅ 版本控制完善
- ✅ 支持多人协作

**缺点**：
- ❌ 需要重构代码结构（独立化）
- ❌ 需要 Git 知识

---

### 选项 B：Git Submodule（当前仓库）

**适用场景**：
- ✅ 不想创建新仓库
- ✅ 多个项目引用同一个 MCP Server

**操作**：

```bash
# 在主项目创建独立分支
git checkout --orphan mcp-server-standalone
git rm -rf .
git checkout master -- mcp_servers/ src/ai/ src/schemas.py src/utils/
git add .
git commit -m "Standalone MCP Server"
git push origin mcp-server-standalone

# 其他项目引用
git submodule add -b mcp-server-standalone \
  https://github.com/your-org/feishu-hr-translator.git \
  lib/llm-translator
```

**优点**：
- ✅ 不需要创建新仓库
- ✅ 保持代码同步

**缺点**：
- ❌ 依赖原仓库
- ❌ submodule 管理较复杂

---

## 📦 方式 3：Docker 镜像分享 ⭐ 推荐生产环境

### 选项 A：离线分发（内网环境）

**步骤 1：构建并导出镜像**

```bash
# 构建
cd /path/to/feishu-hr-translator
docker build -f mcp_servers/Dockerfile -t llm-translator-mcp:0.1.0 .

# 导出
docker save llm-translator-mcp:0.1.0 | gzip > llm-translator-mcp.tar.gz

# 查看大小（约 200MB）
ls -lh llm-translator-mcp.tar.gz
```

**步骤 2：分享 tar.gz 文件**

通过内网文件服务器、U盘等方式传输

**步骤 3：接收者导入**

```bash
# 导入镜像
gunzip -c llm-translator-mcp.tar.gz | docker load

# 运行
docker run --rm \
  -e DASHSCOPE_API_KEY="your_key" \
  llm-translator-mcp:0.1.0
```

**优点**：
- ✅ 开箱即用，无需配置 Python 环境
- ✅ 适合内网离线环境
- ✅ 跨平台（Linux/macOS/Windows）

**缺点**：
- ❌ 文件较大（~200MB）
- ❌ 需要 Docker 环境

---

### 选项 B：在线镜像仓库

**Docker Hub（公开）**

```bash
# 推送
docker tag llm-translator-mcp:0.1.0 your-username/llm-translator-mcp:0.1.0
docker push your-username/llm-translator-mcp:0.1.0

# 其他人使用
docker pull your-username/llm-translator-mcp:0.1.0
docker run --rm -e DASHSCOPE_API_KEY="key" your-username/llm-translator-mcp:0.1.0
```

**企业私有仓库**

```bash
# 推送
docker tag llm-translator-mcp:0.1.0 \
  registry.company.com/tools/llm-translator-mcp:0.1.0
docker push registry.company.com/tools/llm-translator-mcp:0.1.0

# 其他人使用
docker pull registry.company.com/tools/llm-translator-mcp:0.1.0
```

**优点**：
- ✅ 版本管理方便
- ✅ 一行命令安装使用
- ✅ 支持自动更新

**缺点**：
- ❌ 需要镜像仓库
- ❌ 公开仓库可能暴露代码

详见：[DOCKER.md](DOCKER.md)

---

## 📦 方式 4：PyPI 包发布（最专业）

### 适用场景
- ✅ 公开开源项目
- ✅ pip install 安装
- ✅ 版本管理完善

### 操作步骤

**1. 准备独立包结构**

需要先完成独立仓库重构（见 DISTRIBUTION.md）

**2. 构建和发布**

```bash
# 安装工具
pip install build twine

# 构建
python -m build

# 测试发布（TestPyPI）
twine upload --repository testpypi dist/*

# 正式发布
twine upload dist/*
```

**3. 其他人使用**

```bash
# 安装
pip install mcp-llm-translator

# 使用
python -c "
from llm_translator_mcp import LLMTranslatorServer
import asyncio

async def test():
    server = LLMTranslatorServer(api_key='your_key')
    result = await server.translate_to_hr_language('测试')
    print(result)

asyncio.run(test())
"
```

**优点**：
- ✅ 最专业的分享方式
- ✅ 自动依赖管理
- ✅ 版本升级方便（`pip install --upgrade`）

**缺点**：
- ❌ 需要 PyPI 账号
- ❌ 公开发布（企业可用私有 PyPI）
- ❌ 需要代码重构

---

## 📊 方式对比

| 特性 | ZIP 文件 | Git 仓库 | Docker（离线） | Docker（在线） | PyPI |
|------|---------|---------|-------------|-------------|------|
| **难度** | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **速度** | 5分钟 | 30分钟 | 20分钟 | 15分钟 | 2小时 |
| **文件大小** | ~50KB | N/A | ~200MB | N/A | ~50KB |
| **版本管理** | ❌ | ✅ | ⚠️ | ✅ | ✅ |
| **安装依赖** | 手动 | 手动 | 自动 | 自动 | 自动 |
| **更新方式** | 重新打包 | git pull | 重新导入 | docker pull | pip upgrade |
| **适合内网** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **需要工具** | 无 | Git | Docker | Docker | PyPI账号 |

---

## 🎯 推荐方案总结

### 🥇 首选：ZIP 文件（内部快速分享）

**何时使用**：
- 给同事快速测试
- 内网环境
- 不需要频繁更新

**操作**：
```bash
scripts\package_mcp_server.bat  # Windows
# 分享 dist/mcp-llm-translator-0.1.0.zip
```

---

### 🥈 次选：Docker 镜像（生产环境）

**何时使用**：
- 生产环境部署
- 需要环境隔离
- 跨平台支持

**操作**：
```bash
# 构建
docker build -f mcp_servers/Dockerfile -t llm-translator-mcp:latest .

# 离线分享
docker save llm-translator-mcp:latest | gzip > llm-translator-mcp.tar.gz

# 或在线分享
docker push your-repo/llm-translator-mcp:latest
```

---

### 🥉 备选：Git 独立仓库（长期协作）

**何时使用**：
- 多个项目共享
- 需要版本管理
- 开源分享

**操作**：
需要代码重构，见 [DISTRIBUTION.md](DISTRIBUTION.md)

---

## 📋 分享检查清单

分享前确认：

- [ ] ✅ 代码能正常运行
- [ ] ✅ 已移除敏感信息（API keys、内部地址）
- [ ] ✅ 文档齐全（README、INSTALL、QUICKSTART）
- [ ] ✅ 添加使用示例
- [ ] ✅ 说明依赖要求（Python 3.10+、DashScope API）
- [ ] ✅ 提供故障排查指南
- [ ] ✅ 标注版本号
- [ ] ✅ 添加 LICENSE 文件

---

## 📞 相关文档

- [README.md](README.md) - 功能介绍
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- [DISTRIBUTION.md](DISTRIBUTION.md) - 详细分发方案
- [DOCKER.md](DOCKER.md) - Docker 使用指南

---

## 💡 常见问题

### Q1: 接收者没有 DASHSCOPE_API_KEY 怎么办？

**A**: 在分享文档中说明：
1. 访问 https://dashscope.console.aliyun.com/
2. 注册阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key

### Q2: 如何更新已分享的版本？

**A**:
- **ZIP 方式**：重新打包，提供新版本 ZIP
- **Git 方式**：`git pull` 更新
- **Docker 方式**：`docker pull` 更新镜像
- **PyPI 方式**：`pip install --upgrade`

### Q3: 可以同时使用多种分享方式吗？

**A**: 可以！推荐组合：
- 内部测试：ZIP 文件
- 生产部署：Docker 镜像
- 公开分享：PyPI + Git 仓库

---

**Made with ❤️ for easy sharing**
