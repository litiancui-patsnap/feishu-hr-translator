# LLM Translator MCP Server - Quick Start Guide

## 🚀 5 分钟快速开始

### 1. 确认环境

```bash
# 检查 Python 版本 (需要 3.10+)
python --version

# 确认在项目根目录
cd /path/to/feishu-hr-translator
```

### 2. 配置 API Key

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件，填入你的 DashScope API Key
nano .env
```

在 `.env` 中设置：
```ini
DASHSCOPE_API_KEY=sk-your-api-key-here
QWEN_MODEL=qwen-plus
```

### 3. 测试运行

```bash
# 直接运行测试
python -m mcp_servers.llm_translator
```

**应该看到类似输出：**
```
🔄 测试 LLM Translator Server...
输入文本: 本周完成了 WebApp 的 TDD/BDD 测试框架搭建...

✅ 翻译结果:
📝 HR 总结: 本周搭建了网页端的自动化测试工具...
```

---

## 💻 在 Claude Desktop 中使用

### 步骤 1：配置 MCP

编辑配置文件：
- **Windows**: `%APPDATA%\Claude\mcp_settings.json`
- **macOS**: `~/.config/claude/mcp_settings.json`
- **Linux**: `~/.config/claude/mcp_settings.json`

添加配置：
```json
{
  "mcpServers": {
    "llm-translator": {
      "command": "python",
      "args": [
        "-m",
        "mcp_servers.llm_translator"
      ],
      "env": {
        "PYTHONPATH": "/path/to/feishu-hr-translator",
        "DASHSCOPE_API_KEY": "your_api_key_here",
        "QWEN_MODEL": "qwen-plus"
      }
    }
  }
}
```

### 步骤 2：重启 Claude Desktop

### 步骤 3：测试使用

在 Claude 中输入：
```
帮我把这段技术周报翻译成 HR 能看懂的语言：
"本周完成了 API 重构，优化了 Redis 缓存，修复了 5 个 bug"
```

Claude 应该会：
1. 识别到需要使用 llm-translator
2. 调用 MCP Server
3. 返回通俗化的翻译结果

---

## 🧪 Python 代码中使用

```python
import asyncio
from mcp_servers.llm_translator import LLMTranslatorServer

async def main():
    # 创建 server
    server = LLMTranslatorServer(
        api_key="your_api_key",
        model="qwen-plus"
    )

    # 翻译技术报告
    result = await server.translate_to_hr_language(
        text="本周完成了微服务架构升级，实现了 gRPC 通信",
        user_name="张三",
        period_type="weekly",
        okr_context="Q1目标：提升系统性能"
    )

    # 输出结果
    print("HR 总结:", result["summary"])
    print("风险项:", result["risks"])
    print("下一步:", result["next_actions"])

# 运行
asyncio.run(main())
```

---

## 📚 常用功能示例

### 示例 1：仅提取风险

```python
risks = await server.extract_risks(
    text="项目进度延期，第三方 API 不稳定",
    context="关键项目"
)

for risk in risks:
    print(f"[{risk['likelihood']}] {risk['item']}")
```

### 示例 2：检查 OKR 对齐

```python
alignment = await server.infer_okr_alignment(
    text="完成了用户登录和注册功能",
    okr_context="Q1 OKR：完成用户认证系统 (登录、注册、密码重置)"
)

print(f"已完成: {alignment['hit_krs']}")
print(f"未完成: {alignment['gaps']}")
```

### 示例 3：生成行动项

```python
actions = await server.generate_next_actions(
    text="前端已完成，后端开发中",
    context="月底上线"
)

for action in actions:
    print(f"- {action}")
```

---

## ⚙️ 高级配置

### 切换模型

```python
# 使用更强大的模型（更高质量）
server = LLMTranslatorServer(
    api_key="...",
    model="qwen-max"
)

# 使用更快的模型（更低成本）
server = LLMTranslatorServer(
    api_key="...",
    model="qwen-turbo"
)
```

### 调整超时

```python
# 处理长文档时增加超时
server = LLMTranslatorServer(
    api_key="...",
    timeout=60.0  # 60 秒
)
```

---

## 🐛 故障排查

### 问题 1：API Key 错误

```
❌ Error: Invalid API key
```

**解决**：
1. 检查 `.env` 中的 `DASHSCOPE_API_KEY` 是否正确
2. 确认 Key 未过期：https://dashscope.console.aliyun.com

### 问题 2：Module not found

```
❌ ModuleNotFoundError: No module named 'src'
```

**解决**：
```bash
# 设置 PYTHONPATH
export PYTHONPATH=/path/to/feishu-hr-translator:$PYTHONPATH

# 或在代码中添加
import sys
sys.path.insert(0, '/path/to/feishu-hr-translator')
```

### 问题 3：请求超时

```
❌ TimeoutError: Request timed out
```

**解决**：
```python
# 增加超时时间
server = LLMTranslatorServer(timeout=60.0)
```

---

## 📊 性能参考

| 场景 | 输入长度 | 处理时间 | 模型 |
|------|---------|---------|------|
| 简短日报 | ~100字 | 2-3秒 | qwen-turbo |
| 标准周报 | ~500字 | 3-5秒 | qwen-plus |
| 详细月报 | ~2000字 | 5-8秒 | qwen-max |

---

## 🎯 下一步

- 📖 阅读完整文档：[README.md](README.md)
- 🧪 运行测试：`pytest tests/mcp_tests/`
- 🚀 集成到你的应用
- 🤝 贡献改进

---

**需要帮助？** 查看 [Issues](https://github.com/your-org/feishu-hr-translator/issues) 或联系团队
