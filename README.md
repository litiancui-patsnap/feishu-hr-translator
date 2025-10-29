# Feishu HR Translator 使用指南

本项目是一套把飞书 OKR 和工作日报整理成 HR 能直接阅读的总结工具。按照下面的步骤操作，就能在本地启动服务，并向飞书群推送 AI 生成的卡片。

## 1. 准备工作
- Windows 10/11 或 macOS
- 已安装 Python 3.10 及以上版本
- 可以访问互联网（用于调用 DashScope 的 Qwen 模型）
- 一个能收到飞书消息的群聊（需要提前把机器人拉进群，并记录群 ID）

## 2. 下载并配置
1. 打开终端/PowerShell，进入项目目录：
   ```powershell
   cd E:\feishu-ai\feishu-hr-translator
   ```
2. 复制环境变量模板，并填写自己的配置：
   ```powershell
   copy .env.example .env
   ```
3. 用记事本或 VS Code 打开 `.env`，把下面几项换成真实值：
   - `FEISHU_APP_ID` / `FEISHU_APP_SECRET`：飞书机器人的应用 ID 与密钥
   - `FEISHU_DEFAULT_CHAT_ID`：需要推送卡片的群 ID
   - `DASHSCOPE_API_KEY`：阿里 DashScope 控制台申请的 API Key

> 小贴士：其余选项可以保留默认值，后续遇到需要再调整。

## 3. 安装依赖
1. 创建虚拟环境：
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. 安装项目依赖：
   ```powershell
   pip install -r requirements.txt
   ```

## 4. 启动服务
在虚拟环境保持激活的状态下执行：
```powershell
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```
终端看到 “Uvicorn running on http://0.0.0.0:8080” 表示启动成功。

若想确认服务是否正常，可在另一个终端运行：
```powershell
curl http://127.0.0.1:8080/healthz
```
收到 `{"ok": true}` 即代表服务正常。

## 5. 发送测试 Webhook
保持服务运行，在第二个终端执行：
```powershell
.\.venv\Scripts\python.exe send_webhook.py
```
脚本会模拟一条飞书消息，并在日志里打印执行情况：
- 如果一切顺利，会收到 `200` 状态码，并看到 “feishu_card_sent” 日志；
- 飞书群里将出现一张包含 HR 总结的卡片；
- 同时 `data/reports_slim.csv` 会追加一条记录，方便后续复盘。

## 6. 日常使用
1. 保持服务运行状态。
2. 把机器人加入需要汇报的飞书群。
3. 员工按日或周在群里发送日报内容，或通过自动化流程触发 Webhook。
```powershell
.\.venv\Scripts\python.exe -m src.feishu.report_fetch --start 2025-10-28 --end 2025-10-28
```
4. 服务会自动：
   - 识别周期（日报、周报、月报）；
   - 读取本地 `data/okr_cache.json` 中的 OKR 摘要；
   - 调用 Qwen 模型生成 HR 语言的总结；
   - 在飞书群里发送卡片，并保存到 CSV。

## 7. 常见问题
- **提示 “(离线模式)”**：通常是 DashScope 请求超时或 Key 配置错误，请检查 `.env` 里的 `DASHSCOPE_API_KEY`，并确认当前网络能访问 `dashscope.aliyuncs.com`。
- **卡片没有发送**：查看终端是否有 “Invalid verification token” 或 “feishu_card_sent”，若没有，请确认 `.env` 里的飞书 Token、群 ID 是否正确。
- **CSV 文件打不开**：请确保使用支持 UTF-8 的文本编辑器或 Excel 打开 `data/reports_slim.csv`。

## 8. 进一步设置（选做）
- **改用 Google Sheet 或多维表格保存**：在 `.env` 中把 `STORAGE_DRIVER` 改为 `sheet` 或 `bitable`，并补全对应凭证即可。
- **同步企业 OKR**：配置 `FEISHU_TENANT_APP_ID`、`FEISHU_OKR_IDS` 等参数后，运行 `python -m src.okr.sync_job` 可以自动更新 OKR 缓存。

---
如遇问题，可以把终端中的错误信息粘贴给技术同事协助排查。祝使用顺利！