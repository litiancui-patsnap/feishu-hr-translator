# 飞书 HR 翻译器 - 技术栈总结

> 📚 本文档详细说明项目使用的前后端技术、开发工具和部署架构

---

## 📌 技术架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (前端容器)                          │
│  • 静态文件服务 (React SPA)                                  │
│  • 反向代理 (/api/* → Backend)                               │
│  • 反向代理 (/webhook/* → Backend)                           │
└────────────────────────┬────────────────────────────────────┘
                         │ Docker 内部网络
                         ↓
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (后端容器)                      │
│  • RESTful API (用户认证、数据查询)                          │
│  • Webhook 处理 (飞书消息接收)                               │
│  • AI 调用 (Qwen 大模型分析)                                 │
│  • 数据存储 (CSV 文件)                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   外部服务 & 数据存储                         │
│  • 飞书 API (获取 OKR、发送消息卡片)                          │
│  • 阿里云 DashScope (Qwen AI 模型)                           │
│  • CSV 文件 (data/reports_slim.csv)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 前端技术栈

### 核心框架

| 技术 | 版本 | 用途 | 说明 |
|------|------|------|------|
| **React** | 18.2.0 | UI 框架 | 用于构建用户界面的声明式组件库 |
| **TypeScript** | 5.2.2 | 开发语言 | 提供类型安全和更好的开发体验 |
| **Vite** | 5.0.8 | 构建工具 | 快速的前端构建工具，替代 Webpack |

### UI 组件库

| 技术 | 版本 | 用途 |
|------|------|------|
| **Ant Design** | 5.12.0 | UI 组件库 |
| **@ant-design/icons** | 5.2.6 | 图标库 |
| **@ant-design/charts** | 2.0.3 | 图表组件（基于 G2） |

### 路由和状态管理

| 技术 | 版本 | 用途 |
|------|------|------|
| **React Router** | 6.20.0 | 单页面应用路由 |
| **React Context API** | 内置 | 全局状态管理（用户认证） |

### 数据可视化

| 技术 | 版本 | 用途 |
|------|------|------|
| **Recharts** | 3.5.1 | 图表库（折线图、柱状图） |

### HTTP 客户端

| 技术 | 版本 | 用途 |
|------|------|------|
| **Axios** | 1.6.2 | HTTP 请求库 |

### 工具库

| 技术 | 版本 | 用途 |
|------|------|------|
| **Day.js** | 1.11.10 | 日期时间处理 |
| **XLSX** | 0.18.5 | Excel 文件导出 |

### 开发工具

| 技术 | 版本 | 用途 |
|------|------|------|
| **ESLint** | 8.55.0 | 代码检查 |
| **@typescript-eslint** | 6.14.0 | TypeScript 代码规范 |
| **@vitejs/plugin-react** | 4.2.1 | Vite React 插件 |

---

## ⚙️ 后端技术栈

### 核心框架

| 技术 | 版本 | 用途 | 说明 |
|------|------|------|------|
| **Python** | 3.11 | 开发语言 | 高效、易读的编程语言 |
| **FastAPI** | 最新 | Web 框架 | 现代、高性能的异步 API 框架 |
| **Uvicorn** | 最新 | ASGI 服务器 | 用于运行 FastAPI 应用 |

### 数据验证和配置

| 技术 | 版本 | 用途 |
|------|------|------|
| **Pydantic** | 最新 | 数据验证 |
| **pydantic-settings** | 最新 | 配置管理 |
| **python-dotenv** | 最新 | 环境变量加载 |

### HTTP 客户端

| 技术 | 版本 | 用途 |
|------|------|------|
| **httpx** | 最新 | 异步 HTTP 客户端 |

### 数据库 & ORM

| 技术 | 版本 | 用途 |
|------|------|------|
| **SQLAlchemy** | 最新 | ORM 框架（用于用户管理） |
| **CSV** | 内置 | 报告数据存储 |

### 认证和安全

| 技术 | 版本 | 用途 |
|------|------|------|
| **python-jose[cryptography]** | 最新 | JWT Token 生成和验证 |
| **email-validator** | 最新 | 邮箱格式验证 |

### 模板引擎

| 技术 | 版本 | 用途 |
|------|------|------|
| **Jinja2** | 最新 | 飞书消息卡片模板渲染 |

### 测试

| 技术 | 版本 | 用途 |
|------|------|------|
| **pytest** | 最新 | 单元测试和集成测试 |

---

## 🤖 AI 和外部服务

### AI 模型

| 服务 | 模型 | 用途 |
|------|------|------|
| **阿里云 DashScope** | Qwen (通义千问) | 报告分析、OKR 匹配、风险评估 |

### 飞书 API

| 功能 | 说明 |
|------|------|
| **飞书开放平台 API** | 获取 OKR、发送消息卡片、接收 Webhook |
| **Webhook** | 接收员工报告提交事件 |

---

## 🐳 部署技术栈

### 容器化

| 技术 | 版本 | 用途 |
|------|------|------|
| **Docker** | 20.10+ | 容器化应用 |
| **Docker Compose** | 2.0+ | 多容器编排 |

### 前端容器

```dockerfile
# 基础镜像
FROM node:20-alpine (构建阶段)
FROM nginx:1.25-alpine (运行阶段)

# 构建工具
- Node.js 20
- npm (包管理器)
- Vite (构建工具)

# Web 服务器
- Nginx (反向代理 + 静态文件服务)
```

### 后端容器

```dockerfile
# 基础镜像
FROM python:3.11-slim

# Python 环境
- Python 3.11
- pip (包管理器)
- uvicorn (ASGI 服务器)

# 系统依赖
- curl (健康检查)
```

### 网络架构

| 组件 | 端口 | 说明 |
|------|------|------|
| **Frontend (Nginx)** | 80 (容器内)<br>8888 (宿主机) | 对外暴露 |
| **Backend (FastAPI)** | 8080 (容器内)<br>不暴露 | 仅通过 Nginx 代理访问 |
| **Docker 内部网络** | app-network | Bridge 模式 |

---

## 📂 项目目录结构

```
feishu-hr-translator/
├── frontend/                    # 前端代码
│   ├── src/
│   │   ├── api/                 # API 请求封装
│   │   ├── components/          # React 组件
│   │   ├── contexts/            # Context (全局状态)
│   │   ├── pages/               # 页面组件
│   │   ├── types/               # TypeScript 类型定义
│   │   └── utils/               # 工具函数
│   ├── package.json             # 依赖配置
│   ├── vite.config.ts           # Vite 配置
│   └── tsconfig.json            # TypeScript 配置
│
├── backend/                     # 后端代码 (Web UI 专用)
│   ├── api/                     # API 路由
│   ├── auth/                    # 认证中间件
│   ├── models/                  # 数据模型 (SQLAlchemy)
│   ├── services/                # 业务逻辑
│   └── web_main.py              # Web UI 入口
│
├── src/                         # 后端核心逻辑
│   ├── ai/                      # AI 调用 (Qwen)
│   ├── feishu/                  # 飞书 API 封装
│   ├── okr/                     # OKR 数据处理
│   ├── storage/                 # 数据存储 (CSV)
│   ├── main.py                  # Webhook 服务入口
│   └── schemas.py               # 数据模型 (Pydantic)
│
├── deploy/                      # 部署配置
│   ├── Dockerfile.backend       # 后端 Dockerfile
│   ├── Dockerfile.frontend      # 前端 Dockerfile
│   ├── docker-compose.production.yml
│   ├── nginx.conf               # Nginx 配置
│   └── deploy.sh                # 一键部署脚本
│
├── data/                        # 数据文件
│   ├── reports_slim.csv         # 报告数据
│   └── okr_cache.json           # OKR 缓存
│
├── requirements.txt             # Python 依赖
├── .env                         # 环境变量配置
└── README.md                    # 项目说明
```

---

## 🔧 开发工具链

### 前端开发

```bash
# 开发服务器
npm run dev          # 启动 Vite 开发服务器 (端口 3000)

# 构建
npm run build        # TypeScript 编译 + Vite 构建

# 代码检查
npm run lint         # ESLint 检查

# 预览构建结果
npm run preview      # 预览生产构建
```

### 后端开发

```bash
# 开发服务器
uvicorn src.main:app --reload --port 8080

# 测试
pytest tests/

# 代码格式化
black src/ backend/

# 类型检查
mypy src/ backend/
```

---

## 🚀 部署流程

### 本地开发

```bash
# 前端
cd frontend
npm install
npm run dev

# 后端
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8080
```

### Docker 生产部署

```bash
# 1. 配置环境变量
cp deploy/.env.production .env
vim .env

# 2. 一键部署
cd deploy
./deploy.sh

# 3. 查看状态
docker-compose -f docker-compose.production.yml ps

# 4. 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

---

## 📊 数据流向

### 1. 员工提交报告

```
员工在飞书提交日报
    ↓
飞书发送 Webhook 到后端 (/webhook/feishu)
    ↓
后端接收并验证 Token
    ↓
读取 OKR 数据 (data/okr_cache.json)
    ↓
调用 Qwen AI 分析报告
    ↓
保存到 CSV (data/reports_slim.csv)
    ↓
发送卡片到飞书群
```

### 2. Web UI 查询数据

```
用户登录 Web UI
    ↓
前端发送 API 请求 (/api/dashboard/*)
    ↓
后端读取 CSV 文件
    ↓
计算统计指标 (平均 OKR 信心度、高风险率等)
    ↓
返回 JSON 数据
    ↓
前端渲染图表和表格
```

---

## 🔐 安全措施

| 层级 | 措施 | 说明 |
|------|------|------|
| **前端** | JWT Token | 存储在 localStorage，每次请求携带 |
| **后端** | Token 验证 | 所有 API 需要验证 Token |
| **后端** | 密码加密 | 使用 bcrypt 哈希存储 |
| **飞书** | Webhook Token | 验证飞书请求合法性 |
| **容器** | 非 root 用户 | 容器内使用 appuser (UID 1000) |
| **网络** | 内部通信 | 后端不直接暴露端口 |
| **环境变量** | .env 文件 | 敏感信息存储在环境变量 |

---

## 📈 性能优化

| 优化点 | 技术 | 说明 |
|--------|------|------|
| **前端构建** | Vite | 快速冷启动、HMR 热更新 |
| **前端缓存** | Nginx | 静态资源缓存控制 |
| **代码分割** | React.lazy | 按需加载组件 |
| **异步请求** | Promise.all | 并行请求多个 API |
| **后端异步** | FastAPI + asyncio | 异步处理请求 |
| **数据存储** | CSV | 轻量级存储，无需数据库 |
| **容器镜像** | Alpine Linux | 前端镜像仅 ~50MB |
| **健康检查** | Docker Healthcheck | 自动重启异常容器 |

---

## 🔍 监控和日志

| 功能 | 实现方式 |
|------|----------|
| **应用日志** | Python logging 模块 |
| **容器日志** | docker-compose logs |
| **健康检查** | /healthz 端点 + Docker Healthcheck |
| **错误追踪** | FastAPI 异常处理 + 日志记录 |

---

## 📚 核心依赖说明

### 为什么选择这些技术？

| 技术 | 选择原因 |
|------|----------|
| **React + TypeScript** | 类型安全、生态成熟、社区活跃 |
| **Ant Design** | 企业级 UI 组件库、开箱即用、中文友好 |
| **FastAPI** | 异步高性能、自动生成 API 文档、类型安全 |
| **Pydantic** | 数据验证简单、与 FastAPI 完美集成 |
| **Docker** | 环境一致性、易于部署、跨平台 |
| **Nginx** | 高性能静态文件服务、反向代理 |
| **CSV** | 轻量级存储、易于查看和备份 |
| **Qwen (通义千问)** | 中文理解能力强、适合 HR 场景 |

---

## 🎓 学习资源

### 前端

- [React 官方文档](https://react.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/docs/)
- [Ant Design 组件库](https://ant.design/components/overview-cn)
- [Vite 构建工具](https://vitejs.dev/)

### 后端

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

### 部署

- [Docker 文档](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Nginx 配置](https://nginx.org/en/docs/)

### AI

- [阿里云 DashScope](https://help.aliyun.com/zh/dashscope/)
- [飞书开放平台](https://open.feishu.cn/document/home/index)

---

## 🔄 版本历史

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| v1.0.0 | 2025-12 | 初始版本：支持报告分析、Web UI、Docker 部署 |

---

## 📞 技术支持

如有技术问题，可以：

1. 查看本文档和项目 README
2. 查看 [完整部署文档](deploy/DEPLOYMENT.md)
3. 查看 [数据指标说明](DATA_METRICS_EXPLAINED.md)
4. 查看 [Web 操作手册](WEB_USER_GUIDE.md)
5. 提交 Issue 到 GitHub 仓库

---

**技术栈总结完毕！** 🎉

本项目采用**现代化的前后端分离架构**，结合 **AI 大模型**和**飞书开放平台**，实现了智能化的工作报告分析和管理。
