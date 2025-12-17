# 文件拷贝清单 - 部署到 Linux 服务器

## 📋 必须拷贝的文件和目录

### 1. 后端核心文件
```
src/                          # 后端源代码目录（整个目录）
requirements.txt              # Python 依赖
```

### 2. 前端文件
```
frontend/                     # 前端源代码目录（整个目录）
  ├── src/                   # React 源代码
  ├── public/                # 静态资源
  ├── package.json           # Node.js 依赖
  ├── package-lock.json      # 依赖锁定文件
  ├── tsconfig.json          # TypeScript 配置
  ├── vite.config.ts         # Vite 构建配置
  └── index.html             # HTML 入口
```

### 3. 部署配置文件
```
deploy/                       # 部署目录（整个目录）
  ├── Dockerfile.backend     # 后端 Docker 配置
  ├── Dockerfile.frontend    # 前端 Docker 配置
  ├── docker-compose.production.yml  # Docker Compose 配置
  ├── nginx.conf             # Nginx 配置
  ├── deploy.sh              # 部署脚本
  ├── update.sh              # 更新脚本
  ├── check-health.sh        # 健康检查脚本
  ├── .env.production        # 环境配置模板
  └── DEPLOYMENT.md          # 部署文档
```

### 4. 数据目录
```
data/                         # 数据目录
  ├── reports_slim.csv       # 报告数据（如果已有）
  └── okr_cache.json         # OKR 缓存（如果已有）
```

### 5. 配置文件
```
.env.example                  # 环境变量模板
.dockerignore                 # Docker 构建忽略文件
README.md                     # 项目说明（可选）
```

---

## 🚫 不需要拷贝的文件

以下文件/目录**不要拷贝**到服务器：

```
.venv/                        # Python 虚拟环境（会在容器内重建）
frontend/node_modules/        # Node.js 依赖（会在容器内重建）
frontend/dist/                # 前端构建产物（会在容器内生成）
.git/                         # Git 版本控制目录
__pycache__/                  # Python 缓存
*.pyc                         # Python 编译文件
.pytest_cache/                # 测试缓存
tests/                        # 测试文件（可选）
demo.py, send_webhook.py      # 测试脚本（可选）
backup-*.tar.gz               # 备份文件
nul                           # Windows 临时文件
```

---

## 📦 打包和传输方法

### 方法 1: 创建压缩包（推荐）

在 Windows 开发机上执行：

```powershell
# 进入项目根目录
cd E:\feishu-ai\feishu-hr-translator

# 创建部署包（排除不需要的文件）
tar -czf feishu-hr-deploy.tar.gz `
  --exclude=".venv" `
  --exclude="frontend/node_modules" `
  --exclude="frontend/dist" `
  --exclude=".git" `
  --exclude="__pycache__" `
  --exclude="*.pyc" `
  --exclude=".pytest_cache" `
  --exclude="backup-*.tar.gz" `
  --exclude="nul" `
  src/ frontend/ deploy/ data/ requirements.txt .env.example .dockerignore README.md
```

### 方法 2: 使用 SCP 传输

```powershell
# 传输压缩包到服务器
scp feishu-hr-deploy.tar.gz root@your-server-ip:/tmp/

# SSH 登录服务器
ssh root@your-server-ip

# 在服务器上解压
cd /root/feishu-hr-translator
tar -xzf /tmp/feishu-hr-deploy.tar.gz
```

### 方法 3: 使用 SFTP 工具

使用 FileZilla、WinSCP 等工具：
1. 连接到服务器
2. 上传以下目录和文件：
   - `src/` 目录
   - `frontend/` 目录（**重要！您当前缺少这个**）
   - `deploy/` 目录
   - `data/` 目录
   - `requirements.txt`
   - `.env.example`
   - `.dockerignore`

---

## ⚠️ 您当前缺少的关键文件

根据您提供的服务器文件列表，缺少：

### 🔴 必须补充的目录
```
frontend/                     # ← 这个目录完全缺失，必须上传！
```

没有这个目录，Web UI 无法构建和运行。

### 可选补充的文件
```
.dockerignore                 # 优化 Docker 构建
```

---

## ✅ 验证文件完整性

上传完成后，在服务器上执行：

```bash
cd /root/feishu-hr-translator

# 检查关键目录
ls -la

# 应该看到以下目录和文件：
# src/          ✓ 后端代码
# frontend/     ✓ 前端代码（您需要补充）
# deploy/       ✓ 部署配置
# data/         ✓ 数据目录
# requirements.txt  ✓ Python 依赖

# 检查 frontend 目录内容
ls -la frontend/

# 应该看到：
# src/          ✓ React 源代码
# public/       ✓ 静态资源
# package.json  ✓ Node.js 依赖配置
# vite.config.ts ✓ Vite 配置
```

---

## 🚀 上传完成后的部署步骤

```bash
cd /root/feishu-hr-translator

# 1. 配置环境变量
cp deploy/.env.production .env
vim .env  # 修改必要的配置

# 2. 执行部署
cd deploy
chmod +x *.sh
./deploy.sh
```

---

## 📁 最终服务器目录结构

```
/root/feishu-hr-translator/
├── src/                      # 后端代码
├── frontend/                 # 前端代码（需要补充）
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── deploy/                   # 部署配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.production.yml
│   ├── nginx.conf
│   ├── deploy.sh
│   └── ...
├── data/                     # 数据目录
│   ├── reports_slim.csv
│   └── okr_cache.json
├── requirements.txt          # Python 依赖
├── .env                      # 环境配置（从 .env.production 复制）
└── .dockerignore             # Docker 构建忽略
```

---

## 💡 快速操作建议

基于您当前的服务器状态：

```bash
# 1. 回到 Windows 开发机，打包 frontend 目录
cd E:\feishu-ai\feishu-hr-translator
tar -czf frontend.tar.gz frontend/

# 2. 上传到服务器
scp frontend.tar.gz root@your-server-ip:/root/feishu-hr-translator/

# 3. 在服务器上解压
cd /root/feishu-hr-translator
tar -xzf frontend.tar.gz

# 4. 验证文件
ls -la frontend/

# 5. 补充 .dockerignore（可选但推荐）
# 从 Windows 复制 .dockerignore 文件到服务器

# 6. 开始部署
cd deploy
chmod +x *.sh
./deploy.sh
```

---

## 🔍 文件大小参考

预期的目录大小（不含依赖）：
- `src/`: ~2-5 MB
- `frontend/src/`: ~1-3 MB
- `deploy/`: ~100 KB
- `data/`: 视数据量而定

完整压缩包（不含 node_modules 和 .venv）：约 5-10 MB

---

有问题随时问我！
