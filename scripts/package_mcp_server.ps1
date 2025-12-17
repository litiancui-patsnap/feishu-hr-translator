# 快速打包 MCP Server 为独立分发包（Windows PowerShell 版本）
# 用法：.\scripts\package_mcp_server.ps1

$ErrorActionPreference = "Stop"

$VERSION = "0.1.0"
$OUTPUT_DIR = "dist\mcp-llm-translator-$VERSION"

Write-Host "📦 打包 MCP Server v$VERSION..." -ForegroundColor Cyan

# 创建输出目录
if (Test-Path $OUTPUT_DIR) {
    Remove-Item -Recurse -Force $OUTPUT_DIR
}
New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null

# 复制核心文件
Write-Host "📁 复制文件..." -ForegroundColor Yellow
Copy-Item -Recurse -Path "mcp_servers\*" -Destination $OUTPUT_DIR

# 复制依赖的 src 文件
New-Item -ItemType Directory -Path "$OUTPUT_DIR\src" -Force | Out-Null
Copy-Item -Recurse -Path "src\ai" -Destination "$OUTPUT_DIR\src\"
Copy-Item -Path "src\schemas.py" -Destination "$OUTPUT_DIR\src\"
Copy-Item -Recurse -Path "src\utils" -Destination "$OUTPUT_DIR\src\"
New-Item -ItemType File -Path "$OUTPUT_DIR\src\__init__.py" -Force | Out-Null

# 创建 requirements.txt
$requirements = @"
httpx>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
jinja2>=3.1.0
"@
Set-Content -Path "$OUTPUT_DIR\requirements.txt" -Value $requirements

# 创建 INSTALL.md
$installGuide = @"
# MCP LLM Translator - 安装指南

## 📦 快速开始

### 1. 安装依赖

``````bash
pip install -r requirements.txt
``````

### 2. 配置 API Key

**Windows PowerShell:**
``````powershell
`$env:DASHSCOPE_API_KEY="your_api_key_here"
``````

**Linux/macOS:**
``````bash
export DASHSCOPE_API_KEY="your_api_key_here"
``````

或创建 `.env` 文件：
``````ini
DASHSCOPE_API_KEY=sk-your-key-here
QWEN_MODEL=qwen-plus
``````

### 3. 测试运行

``````bash
python -m llm_translator
``````

应该看到类似输出：
``````
🔄 测试 LLM Translator Server...
输入文本: 本周完成了 WebApp 的 TDD/BDD 测试框架搭建...

✅ 翻译结果:
📝 HR 总结: 本周搭建了网页端的自动化测试工具...
``````

### 4. 在 Python 代码中使用

``````python
import asyncio
from llm_translator import LLMTranslatorServer

async def main():
    server = LLMTranslatorServer(
        api_key="your_key",
        model="qwen-plus"
    )

    result = await server.translate_to_hr_language(
        text="本周完成了 gRPC 服务迁移，优化了 Redis 缓存",
        user_name="张三",
        period_type="weekly"
    )

    print(result['summary'])

asyncio.run(main())
``````

### 5. 在 Claude Desktop 中使用

编辑配置文件：
- **Windows**: ``%APPDATA%\Claude\mcp_settings.json``
- **macOS/Linux**: ``~/.config/claude/mcp_settings.json``

添加配置：
``````json
{
  "mcpServers": {
    "llm-translator": {
      "command": "python",
      "args": ["-m", "llm_translator"],
      "env": {
        "PYTHONPATH": "E:\\path\\to\\mcp-llm-translator-$VERSION",
        "DASHSCOPE_API_KEY": "your_key"
      }
    }
  }
}
``````

重启 Claude Desktop，即可在对话中使用翻译功能。

---

## 📚 完整文档

- [README.md](README.md) - 完整功能介绍
- [QUICKSTART.md](QUICKSTART.md) - 5 分钟快速开始
- [mcp_config.json](mcp_config.json) - MCP 配置参考

---

## 🐛 故障排查

### 问题 1：ModuleNotFoundError: No module named 'src'

**解决**：
``````bash
# 确保在包根目录运行
cd mcp-llm-translator-$VERSION
python -m llm_translator

# 或设置 PYTHONPATH
set PYTHONPATH=%CD%
python -m llm_translator
``````

### 问题 2：API Key 错误

**解决**：
``````bash
# 检查环境变量是否设置
echo %DASHSCOPE_API_KEY%  # Windows
echo `$DASHSCOPE_API_KEY  # Linux

# 重新设置
set DASHSCOPE_API_KEY=your_key  # Windows
``````

---

## 📞 支持

- 问题反馈：GitHub Issues
- 技术文档：README.md
- 更新日志：CHANGELOG.md

**版本**: $VERSION
**发布日期**: $(Get-Date -Format "yyyy-MM-dd")
"@
Set-Content -Path "$OUTPUT_DIR\INSTALL.md" -Value $installGuide -Encoding UTF8

# 创建 CHANGELOG.md
$changelog = @"
# 更新日志

## [0.1.0] - $(Get-Date -Format "yyyy-MM-dd")

### 新增功能
- ✨ 完整的 LLM Translator MCP Server 实现
- ✨ 4 个 MCP Tools：翻译、风险提取、OKR 对齐、行动生成
- ✨ 3 个 MCP Resources：模型列表、Prompt 模板、词汇表
- ✨ 支持 Qwen 系列模型（max/plus/turbo/long）
- ✨ 完整的文档和测试用例

### 技术特性
- 🔧 异步架构（async/await）
- 🔧 完整的类型提示
- 🔧 错误处理和降级逻辑
- 🔧 可独立运行或集成到 Claude Desktop

### 文档
- 📖 完整的 README.md（355 行）
- 📖 快速开始指南 QUICKSTART.md
- 📖 单元测试覆盖

---

## 未来计划

### [0.2.0] - 计划中
- [ ] 支持更多 LLM 模型（OpenAI GPT、Claude）
- [ ] 流式输出支持
- [ ] 批量翻译功能
- [ ] 缓存优化

### [0.3.0] - 计划中
- [ ] HTTP API 服务
- [ ] Web UI 界面
- [ ] 多语言支持
"@
Set-Content -Path "$OUTPUT_DIR\CHANGELOG.md" -Value $changelog -Encoding UTF8

# 创建简单的启动脚本
$startScript = @"
@echo off
echo 启动 LLM Translator MCP Server...
echo.

REM 检查 API Key
if "%DASHSCOPE_API_KEY%"=="" (
    echo [错误] 未设置 DASHSCOPE_API_KEY 环境变量
    echo 请先设置: set DASHSCOPE_API_KEY=your_key
    pause
    exit /b 1
)

REM 运行测试
python -m llm_translator

pause
"@
Set-Content -Path "$OUTPUT_DIR\start.bat" -Value $startScript -Encoding ASCII

# 清理 __pycache__
Get-ChildItem -Path $OUTPUT_DIR -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 打包为 ZIP
Write-Host "📦 创建 ZIP 归档..." -ForegroundColor Yellow
$zipPath = "dist\mcp-llm-translator-$VERSION.zip"
if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}

Compress-Archive -Path $OUTPUT_DIR -DestinationPath $zipPath

# 显示文件大小
$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "✅ 打包完成!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 输出位置: $zipPath" -ForegroundColor Cyan
Write-Host "📊 文件大小: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 分享清单:" -ForegroundColor Yellow
Write-Host "  - README.md (功能文档)" -ForegroundColor Gray
Write-Host "  - QUICKSTART.md (快速开始)" -ForegroundColor Gray
Write-Host "  - INSTALL.md (安装指南)" -ForegroundColor Gray
Write-Host "  - CHANGELOG.md (更新日志)" -ForegroundColor Gray
Write-Host "  - start.bat (Windows 启动脚本)" -ForegroundColor Gray
Write-Host "  - requirements.txt (Python 依赖)" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 下一步:" -ForegroundColor Yellow
Write-Host "  1. 将 $zipPath 分享给其他团队" -ForegroundColor Gray
Write-Host "  2. 接收者解压后阅读 INSTALL.md" -ForegroundColor Gray
Write-Host "  3. 运行 start.bat (Windows) 或 python -m llm_translator" -ForegroundColor Gray
