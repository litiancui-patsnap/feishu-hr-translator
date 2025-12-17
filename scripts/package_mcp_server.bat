@echo off
REM 快速打包 MCP Server 为独立分发包（Windows 批处理版本）
REM 用法：scripts\package_mcp_server.bat

setlocal enabledelayedexpansion

set VERSION=0.1.0
set OUTPUT_DIR=dist\mcp-llm-translator-%VERSION%

echo.
echo ========================================
echo   打包 MCP Server v%VERSION%
echo ========================================
echo.

REM 创建输出目录
if exist "%OUTPUT_DIR%" (
    echo [清理] 删除旧的输出目录...
    rmdir /s /q "%OUTPUT_DIR%"
)
echo [创建] 创建输出目录...
mkdir "%OUTPUT_DIR%"

REM 复制核心文件
echo [复制] MCP Server 核心文件...
xcopy /E /I /Q mcp_servers\* "%OUTPUT_DIR%\" >nul

REM 复制依赖的 src 文件
echo [复制] 依赖模块...
mkdir "%OUTPUT_DIR%\src" 2>nul
xcopy /E /I /Q src\ai "%OUTPUT_DIR%\src\ai\" >nul
copy /Y src\schemas.py "%OUTPUT_DIR%\src\" >nul
xcopy /E /I /Q src\utils "%OUTPUT_DIR%\src\utils\" >nul
echo. > "%OUTPUT_DIR%\src\__init__.py"

REM 创建 requirements.txt
echo [创建] requirements.txt...
(
echo httpx^>=0.24.0
echo pydantic^>=2.0.0
echo pydantic-settings^>=2.0.0
echo jinja2^>=3.1.0
) > "%OUTPUT_DIR%\requirements.txt"

REM 创建 INSTALL.md
echo [创建] INSTALL.md...
(
echo # MCP LLM Translator - 安装指南
echo.
echo ## 快速开始
echo.
echo ### 1. 安装依赖
echo.
echo ```bash
echo pip install -r requirements.txt
echo ```
echo.
echo ### 2. 配置 API Key
echo.
echo **Windows:**
echo ```cmd
echo set DASHSCOPE_API_KEY=your_api_key_here
echo ```
echo.
echo **Linux/macOS:**
echo ```bash
echo export DASHSCOPE_API_KEY=your_api_key_here
echo ```
echo.
echo ### 3. 测试运行
echo.
echo ```bash
echo python -m llm_translator
echo ```
echo.
echo ### 4. 查看完整文档
echo.
echo - README.md - 功能文档
echo - QUICKSTART.md - 快速开始
echo - DOCKER.md - Docker 使用指南
echo.
echo ## 支持
echo.
echo - 版本: %VERSION%
echo - 问题反馈: GitHub Issues
) > "%OUTPUT_DIR%\INSTALL.md"

REM 创建启动脚本
echo [创建] start.bat...
(
echo @echo off
echo echo =======================================
echo echo   LLM Translator MCP Server
echo echo =======================================
echo echo.
echo.
echo if "%%DASHSCOPE_API_KEY%%"=="" ^(
echo     echo [错误] 未设置 DASHSCOPE_API_KEY 环境变量
echo     echo 请先设置: set DASHSCOPE_API_KEY=your_key
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo [启动] 运行 MCP Server...
echo echo.
echo python -m llm_translator
echo.
echo pause
) > "%OUTPUT_DIR%\start.bat"

REM 清理 __pycache__
echo [清理] Python 缓存目录...
for /d /r "%OUTPUT_DIR%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" 2>nul
)

REM 打包为 ZIP（需要 PowerShell）
echo [打包] 创建 ZIP 归档...
set ZIP_PATH=dist\mcp-llm-translator-%VERSION%.zip
if exist "%ZIP_PATH%" del /f /q "%ZIP_PATH%"

powershell -Command "Compress-Archive -Path '%OUTPUT_DIR%' -DestinationPath '%ZIP_PATH%'"

if exist "%ZIP_PATH%" (
    echo.
    echo ========================================
    echo   打包完成！
    echo ========================================
    echo.
    echo [完成] 输出位置: %ZIP_PATH%

    for %%A in ("%ZIP_PATH%") do (
        set SIZE=%%~zA
        set /a SIZE_MB=!SIZE! / 1048576
        echo [大小] !SIZE_MB! MB
    )

    echo.
    echo [内容] 包含文件:
    echo   - README.md ^(功能文档^)
    echo   - QUICKSTART.md ^(快速开始^)
    echo   - INSTALL.md ^(安装指南^)
    echo   - DOCKER.md ^(Docker 使用指南^)
    echo   - start.bat ^(Windows 启动脚本^)
    echo   - requirements.txt ^(Python 依赖^)
    echo.
    echo [下一步]
    echo   1. 将 %ZIP_PATH% 分享给其他团队
    echo   2. 接收者解压后阅读 INSTALL.md
    echo   3. 运行 start.bat 或 python -m llm_translator
    echo.
) else (
    echo.
    echo [错误] ZIP 打包失败，但目录已创建: %OUTPUT_DIR%
    echo.
)

pause
