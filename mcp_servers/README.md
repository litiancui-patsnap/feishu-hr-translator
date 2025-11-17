# LLM Translator MCP Server

> AI-powered content translation server for converting technical reports to HR-friendly language

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/your-org/feishu-hr-translator)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 📖 Overview

The LLM Translator MCP Server provides AI-powered capabilities to translate technical content into plain language suitable for non-technical audiences (HR, executives, board members). It wraps the Qwen LLM to offer:

- **Technical → HR Language Translation**: Convert technical jargon to business-friendly terms
- **Risk Extraction**: Identify and assess risks from reports
- **OKR Alignment**: Match work against objectives and key results
- **Action Generation**: Create concrete next steps from reports

## 🎯 Features

### MCP Tools

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `translate_to_hr_language` | Main translation function | Technical text + context | HR-friendly summary + risks + OKR alignment |
| `extract_risks` | Extract risks from text | Report text | List of risks with likelihood |
| `infer_okr_alignment` | Match work to OKRs | Report + OKR context | Hit objectives, gaps, confidence |
| `generate_next_actions` | Generate action items | Report text | List of next steps |

### MCP Resources

| Resource | Description |
|----------|-------------|
| `supported_models` | List of available LLM models |
| `prompt_templates` | Prompt templates used for translation |
| `translation_glossary` | Technical terms → plain language mappings |

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/feishu-hr-translator
cd feishu-hr-translator

# Install dependencies
pip install -r requirements.txt

# Or install as package
cd mcp_servers
pip install -e .
```

### 2. Configuration

Set environment variables:

```bash
# Required
export DASHSCOPE_API_KEY="your_api_key_here"

# Optional
export QWEN_MODEL="qwen-plus"  # or qwen-max, qwen-turbo
export QWEN_API_MODE="text"    # or compatible
export REQUEST_TIMEOUT_SECONDS="30"
```

Or use `.env` file:

```ini
DASHSCOPE_API_KEY=sk-xxxxx
QWEN_MODEL=qwen-plus
QWEN_API_MODE=text
REQUEST_TIMEOUT_SECONDS=30
```

### 3. Test the Server

```bash
# Run standalone test
python -m mcp_servers.llm_translator
```

**Expected output:**
```
🔄 测试 LLM Translator Server...
输入文本: 本周完成了 WebApp 的 TDD/BDD 测试框架搭建...

✅ 翻译结果:
📝 HR 总结: 本周搭建了网页端的自动化测试工具（让程序自动检测错误）...

⚠️ 风险项:
  - [medium] 性能优化尚未开始，可能影响用户体验
    缓解措施: 下周优先安排性能测试和优化工作

🎯 已完成的关键成果:
  - 完成自动化测试工具开发

📌 待推进的目标:
  - 性能优化工作进展较慢

➡️ 下一步行动:
  - 开展性能测试并制定优化方案
  - 补充测试用例覆盖

📊 风险等级: medium
🔍 OKR 对齐置信度: 75%
```

## 💻 Usage Examples

### Example 1: Basic Translation

```python
from mcp_servers.llm_translator import LLMTranslatorServer

# Initialize server
server = LLMTranslatorServer(
    api_key="your_api_key",
    model="qwen-plus"
)

# Translate technical report
result = await server.translate_to_hr_language(
    text="本周完成了 API 重构，优化了数据库查询性能，修复了 3 个 P0 bug",
    user_name="张三",
    period_type="weekly",
    okr_context="Q1 目标：提升系统性能和稳定性"
)

print(result["summary"])
# Output: "本周完成了后台接口优化，提升了数据查询速度，解决了 3 个严重问题"
```

### Example 2: Risk Extraction

```python
# Extract risks only
risks = await server.extract_risks(
    text="项目进度延期 2 周，依赖的第三方 API 频繁超时，团队人力不足",
    context="关键项目，需按时交付"
)

for risk in risks:
    print(f"[{risk['likelihood']}] {risk['item']}")
    if risk['mitigation']:
        print(f"  → {risk['mitigation']}")

# Output:
# [high] 项目进度延期可能导致无法按时交付
#   → 增加人力投入，优化关键路径任务
# [high] 第三方服务不稳定影响系统可用性
#   → 实施重试机制和降级方案
```

### Example 3: OKR Alignment

```python
# Check OKR alignment
alignment = await server.infer_okr_alignment(
    text="完成了用户登录、注册功能开发，密码重置功能进度 50%",
    okr_context="Q1 OKR：完成用户认证系统 (KR1: 登录, KR2: 注册, KR3: 密码重置)"
)

print(f"✅ 已完成: {', '.join(alignment['hit_krs'])}")
print(f"📌 待完成: {', '.join(alignment['gaps'])}")
print(f"🔍 置信度: {alignment['confidence']:.0%}")

# Output:
# ✅ 已完成: 用户登录功能, 用户注册功能
# 📌 待完成: 密码重置功能进展较慢
# 🔍 置信度: 67%
```

### Example 4: Action Generation

```python
# Generate next actions
actions = await server.generate_next_actions(
    text="完成了前端页面开发，但后端接口还在开发中，预计下周完成",
    context="需要在月底前上线"
)

for i, action in enumerate(actions, 1):
    print(f"{i}. {action}")

# Output:
# 1. 加快后端接口开发进度，确保下周完成
# 2. 前后端联调测试，验证功能完整性
# 3. 准备上线方案和回滚预案
```

## 🔧 Claude Desktop Integration

### Step 1: Configure MCP Server

Edit Claude Desktop configuration file:

**macOS/Linux**: `~/.config/claude/mcp_settings.json`
**Windows**: `%APPDATA%\Claude\mcp_settings.json`

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
        "DASHSCOPE_API_KEY": "your_api_key_here",
        "QWEN_MODEL": "qwen-plus"
      }
    }
  }
}
```

### Step 2: Restart Claude Desktop

### Step 3: Use in Claude

```
You: 帮我把这段技术周报翻译成 HR 能看懂的语言：
"本周完成了 gRPC 服务迁移，实现了 Redis 缓存优化，集成了 K8s 自动扩缩容"

Claude: 我会使用 llm-translator MCP Server 来翻译...

[Claude calls: translate_to_hr_language]

Claude: 翻译结果：
"本周完成了服务通信方式升级，优化了数据临时存储系统（提升访问速度），实现了服务器资源自动调整（高峰期自动扩容）"
```

## 📊 Supported Models

| Model | Provider | Cost | Best For | Context |
|-------|----------|------|----------|---------|
| `qwen-max` | DashScope | Higher | Highest quality | 8K tokens |
| `qwen-plus` | DashScope | Medium | **Recommended** balance | 32K tokens |
| `qwen-turbo` | DashScope | Lower | Fast simple tasks | 8K tokens |
| `qwen-long` | DashScope | Medium | Long documents | 10M tokens |

Get full list via:
```python
models = server.get_supported_models()
```

## 🎨 Translation Glossary

The server uses an extensive glossary to translate technical terms:

| Technical | Plain Language |
|-----------|----------------|
| API | 系统接口 / 程序连接通道 |
| SDK | 开发工具包 |
| TDD/BDD | 测试驱动开发方法 |
| CI/CD | 自动化部署流程 |
| 重构 | 代码优化 |
| 异步 | 后台处理 / 不阻塞操作 |
| Bug | 程序错误 |
| 前端/后端 | 用户界面 / 服务器程序 |

Get full glossary via:
```python
glossary = server.get_translation_glossary()
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/mcp_tests/test_llm_translator.py

# Run with coverage
pytest --cov=mcp_servers tests/

# Run integration test
python -m mcp_servers.llm_translator
```

## 📈 Performance

- **Average latency**: 2-5 seconds (depends on model)
- **Max input**: 8K tokens (qwen-max/turbo), 32K tokens (qwen-plus), 10M tokens (qwen-long)
- **Output**: ~200-300 words summary + structured data
- **Cost**: ~¥0.002-0.01 per translation (DashScope pricing)

## 🔒 Security & Privacy

- **API Keys**: Never logged or stored, only used for API calls
- **Data**: Input text sent to DashScope API (阿里云), review their privacy policy
- **Caching**: No caching of API responses by default
- **Logging**: Only logs errors and metrics, not content

## 🛠️ Advanced Configuration

### Custom Prompt Templates

```python
# Customize prompts
from src.ai.qwen import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# Modify templates in src/ai/qwen.py or override at runtime
```

### Retry & Timeout

```python
server = LLMTranslatorServer(
    api_key="...",
    timeout=60.0,  # Increase timeout for long documents
)

# Retry logic is built-in (max 2 retries with exponential backoff)
```

### Fallback Behavior

If API fails, the server returns:
- Summary: First 180 chars of original text + "(离线模式)"
- Risks: Empty list
- OKR: Default low-confidence alignment
- Actions: Generic suggestions based on period type

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details

## 🙏 Acknowledgments

- Built on [Qwen](https://help.aliyun.com/zh/dashscope/) by Alibaba Cloud
- Part of [Feishu HR Translator](https://github.com/your-org/feishu-hr-translator) project
- Inspired by [Model Context Protocol](https://modelcontextprotocol.io/)

## 📞 Support

- Issues: [GitHub Issues](https://github.com/your-org/feishu-hr-translator/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/feishu-hr-translator/discussions)
- Email: support@your-org.com

---

**Made with ❤️ for HR teams who deserve plain language**
