# Feishu HR Translator - Web 界面设计方案

> 为 Feishu HR Translator 项目添加完整的 Web 管理界面，包括登录、仪表盘、报告查看、OKR 管理等功能。

---

## 🎯 目标

将现有的后端服务扩展为一个完整的 Web 应用，提供：

1. **用户认证**：飞书 OAuth 登录 + 本地账号登录
2. **仪表盘**：数据统计、图表展示
3. **报告管理**：查看、搜索、筛选、导出周报/月报
4. **OKR 管理**：查看 OKR 对齐情况、进度追踪
5. **系统配置**：管理员配置、用户权限管理

---

## 📐 架构设计

### 技术栈选型

#### 后端（基于现有 FastAPI）
- **框架**：FastAPI（已有）
- **认证**：JWT + OAuth 2.0（飞书）
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **ORM**：SQLAlchemy
- **Session**：FastAPI-Users

#### 前端
- **选项 A**：React + TypeScript + Ant Design ⭐ **推荐**
  - 现代化、组件丰富、适合企业应用
- **选项 B**：Vue 3 + Element Plus
  - 学习曲线平缓、国内文档丰富
- **选项 C**：纯 HTML + Jinja2 模板（最简单）
  - 无需前后端分离、快速开发

#### 部署
- **开发**：前后端分离（React dev server + FastAPI）
- **生产**：静态文件打包到 FastAPI（单一服务）

---

## 🗂️ 数据库设计

### 新增表结构

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),  -- NULL for OAuth users
    full_name VARCHAR(200),
    feishu_user_id VARCHAR(100) UNIQUE,  -- 飞书用户ID
    feishu_open_id VARCHAR(100),
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'user',  -- admin, hr, user
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    INDEX idx_feishu_user_id (feishu_user_id),
    INDEX idx_username (username)
);

-- 会话表（JWT tokens）
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    access_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_access_token (access_token),
    INDEX idx_user_id (user_id)
);

-- 报告表（扩展现有 CSV 数据）
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feishu_user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(200),
    period_type VARCHAR(20),  -- daily, weekly, monthly
    period_start DATE,
    period_end DATE,
    raw_text TEXT,
    hr_summary TEXT,
    risk_level VARCHAR(20),
    risks JSON,  -- 风险列表
    needs JSON,  -- 需求列表
    okr_alignment JSON,  -- OKR 对齐信息
    next_actions JSON,  -- 下一步行动
    okr_brief TEXT,
    message_ts TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_period_type (period_type),
    INDEX idx_period_start (period_start),
    INDEX idx_feishu_user_id (feishu_user_id)
);

-- OKR 表
CREATE TABLE okrs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER,
    feishu_user_id VARCHAR(100),
    owner_name VARCHAR(200),
    okr_id VARCHAR(100),  -- 飞书 OKR ID
    objective VARCHAR(500),  -- 目标
    key_results JSON,  -- KR 列表
    period VARCHAR(50),  -- Q1 2025, 2025H1 等
    status VARCHAR(20),  -- active, completed, archived
    progress FLOAT DEFAULT 0.0,  -- 0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_user_id) REFERENCES users(id),
    INDEX idx_owner_user_id (owner_user_id),
    INDEX idx_period (period),
    INDEX idx_status (status)
);

-- 审计日志
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100),  -- login, view_report, export_data, etc.
    resource_type VARCHAR(50),  -- report, okr, user
    resource_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);
```

---

## 🎨 界面设计

### 1. 登录页面

**路径**：`/login`

**功能**：
- 飞书 OAuth 登录（主要）
- 本地账号登录（备用）
- 记住我（7天免登录）

**界面布局**：

```
┌────────────────────────────────────────┐
│                                        │
│         Feishu HR Translator           │
│                                        │
│   ┌──────────────────────────────┐    │
│   │  🔐 使用飞书账号登录          │    │
│   └──────────────────────────────┘    │
│                                        │
│   ──────── 或 ────────                 │
│                                        │
│   用户名: [__________________]         │
│   密码:   [__________________]         │
│   [ ] 记住我                           │
│                                        │
│   ┌──────────────────────────────┐    │
│   │        登录                   │    │
│   └──────────────────────────────┘    │
│                                        │
└────────────────────────────────────────┘
```

---

### 2. 主界面布局

**路径**：`/dashboard`

**布局**：左侧菜单 + 顶部导航 + 内容区

```
┌────────────────────────────────────────────────────────────┐
│  Feishu HR  │  📊 仪表盘     🔔通知(3)      👤 张三  ▼      │
├──────────────┴──────────────────────────────────────────────┤
│ 📊 仪表盘    │                                              │
│ 📝 报告管理  │     【内容区域，根据选择的菜单显示】           │
│ 🎯 OKR管理   │                                              │
│ 👥 团队视图  │                                              │
│ ⚙️  系统设置  │                                              │
│ 📤 退出登录  │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

---

### 3. 仪表盘（Dashboard）

**路径**：`/dashboard`

**功能模块**：

#### A. 数据概览卡片

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 本周报告    │ 本月报告    │ 高风险项    │ OKR 完成度  │
│    42       │    186      │     8       │    73%      │
│  ↑ 5.2%    │  ↓ 2.1%    │  ↓ 15%     │  ↑ 3%      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### B. 趋势图表

```
报告提交趋势（近30天）
┌──────────────────────────────────────────┐
│  数量                                    │
│   60│                           ╱╲       │
│   50│                    ╱╲   ╱  ╲     │
│   40│            ╱╲   ╱  ╲╱      ╲   │
│   30│      ╱╲  ╱  ╲╱              ╲ │
│   20│  ╱╲╱  ╲╱                     ╲│
│    0└────────────────────────────────┘  │
│      1/1  1/8  1/15 1/22 1/29           │
└──────────────────────────────────────────┘
```

#### C. 风险分布饼图

```
风险等级分布
┌──────────────────────────┐
│       ╱───╲             │
│      │ 23% │  低风险     │
│       ╲───╱             │
│      ╱─────╲            │
│     │  52%  │ 中风险     │
│      ╲─────╱            │
│      ╱───╲              │
│     │ 25% │  高风险     │
│      ╲───╱              │
└──────────────────────────┘
```

#### D. 最近报告列表（预览）

| 提交人 | 周期 | 时间 | 风险等级 | 操作 |
|--------|------|------|---------|------|
| 张三   | 本周 | 2小时前 | 🟡 中 | 查看 |
| 李四   | 本周 | 3小时前 | 🟢 低 | 查看 |
| 王五   | 本周 | 5小时前 | 🔴 高 | 查看 |

---

### 4. 报告管理页面

**路径**：`/reports`

**功能**：

#### A. 筛选器
```
┌─────────────────────────────────────────────────────────┐
│ 🔍 搜索: [____________]  周期: [本周 ▼]  风险: [全部 ▼] │
│                                                         │
│ 提交人: [全部 ▼]  部门: [全部 ▼]  [🔄 刷新]  [📥 导出]  │
└─────────────────────────────────────────────────────────┘
```

#### B. 报告列表（表格）

| 选择 | ID | 提交人 | 周期 | 提交时间 | 风险等级 | OKR对齐度 | 操作 |
|------|-----|--------|------|----------|---------|-----------|------|
| ☐ | 1234 | 张三 | 本周 | 2025-01-15 | 🟡 中 | 80% | 查看 编辑 删除 |
| ☐ | 1233 | 李四 | 本周 | 2025-01-14 | 🟢 低 | 92% | 查看 编辑 删除 |
| ☐ | 1232 | 王五 | 本周 | 2025-01-14 | 🔴 高 | 45% | 查看 编辑 删除 |

#### C. 批量操作
```
[全选] [导出选中] [批量删除] [批量标记]
```

---

### 5. 报告详情页面

**路径**：`/reports/:id`

**布局**：

```
┌─────────────────────────────────────────────────────────┐
│ ← 返回列表             周报 - 张三 (2025-01-08 ~ 01-14) │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📋 原始内容                                             │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 本周完成了用户认证模块的开发，包括：                │
│ │ 1. 实现了 JWT 认证                                  │
│ │ 2. 集成飞书 OAuth 登录                              │
│ │ 3. 完成了权限控制                                   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ 💬 HR 友好总结                                          │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 本周完成了系统登录功能，用户可以通过企业账号      │
│ │ 安全访问系统，并根据不同角色看到相应内容。        │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ ⚠️ 风险项                                               │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 🔴 高风险：OAuth 集成测试不充分，可能存在安全漏洞 │
│ │    缓解措施：计划下周进行安全审计                   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ 🎯 OKR 对齐情况                                         │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 命中目标：[O1] 提升系统安全性                       │
│ │ 命中 KR：[KR1] 实现企业级认证 (80%)                │
│ │ 差距：权限管理模块尚未完成                          │
│ │ 置信度：85%                                         │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ 📌 下一步行动                                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ □ 完成安全审计（负责人：张三，截止：1/20）        │
│ │ □ 完善权限管理文档（负责人：李四，截止：1/18）    │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ [编辑] [删除] [导出PDF] [发送飞书]                     │
└─────────────────────────────────────────────────────────┘
```

---

### 6. OKR 管理页面

**路径**：`/okrs`

**功能**：

#### A. OKR 概览

```
┌─────────────────────────────────────────────────────────┐
│ 2025 Q1 OKR 进度                                        │
│                                                         │
│ O1: 提升系统稳定性                      ████████░░ 80%  │
│   KR1: SLA 达到 99.9%                  ████████░░ 85%  │
│   KR2: 故障恢复时间 < 10分钟           ███████░░░ 75%  │
│                                                         │
│ O2: 提升团队效能                        ███████░░░ 70%  │
│   KR1: 代码审查覆盖率 100%             ██████████ 100% │
│   KR2: 平均交付周期缩短 20%            ████░░░░░░ 40%  │
│                                                         │
│ O3: 完善技术文档                        ██████░░░░ 60%  │
│   KR1: API 文档完整度 90%              ██████░░░░ 60%  │
│   KR2: 用户手册发布                    ░░░░░░░░░░ 0%   │
└─────────────────────────────────────────────────────────┘
```

#### B. OKR 详情列表

| OKR | 负责人 | 周期 | 进度 | 对齐报告数 | 最后更新 | 操作 |
|-----|--------|------|------|-----------|----------|------|
| O1: 提升系统稳定性 | 张三 | 2025 Q1 | 80% | 12 | 2天前 | 查看 |
| O2: 提升团队效能 | 李四 | 2025 Q1 | 70% | 8 | 3天前 | 查看 |

---

### 7. 团队视图页面

**路径**：`/team`

**功能**：展示团队成员的报告提交情况、OKR 进度

```
┌─────────────────────────────────────────────────────────┐
│ 团队成员                                                 │
│                                                         │
│ ┌─────────────────────────────────────────────────┐     │
│ │ 👤 张三              部门：研发部                │     │
│ │    本周报告：✅      本月报告：5篇              │     │
│ │    OKR 进度：78%     风险：🟡 中                │     │
│ └─────────────────────────────────────────────────┘     │
│                                                         │
│ ┌─────────────────────────────────────────────────┐     │
│ │ 👤 李四              部门：研发部                │     │
│ │    本周报告：✅      本月报告：4篇              │     │
│ │    OKR 进度：92%     风险：🟢 低                │     │
│ └─────────────────────────────────────────────────┘     │
│                                                         │
│ ┌─────────────────────────────────────────────────┐     │
│ │ 👤 王五              部门：产品部                │     │
│ │    本周报告：❌      本月报告：3篇              │     │
│ │    OKR 进度：45%     风险：🔴 高                │     │
│ └─────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

### 8. 系统设置页面

**路径**：`/settings`

**功能**：

#### A. 个人设置
- 修改头像
- 修改密码
- 通知偏好设置

#### B. 系统配置（仅管理员）
- 飞书集成配置
- AI 模型配置
- 存储配置
- OKR 同步配置

```
┌─────────────────────────────────────────────────────────┐
│ ⚙️ 系统配置                                              │
│                                                         │
│ 【飞书集成】                                             │
│ App ID:     [__________________]                        │
│ App Secret: [__________________]  [测试连接]            │
│                                                         │
│ 【AI 模型】                                              │
│ API Key:    [********************]                      │
│ 模型:       [qwen-plus ▼]                               │
│ 超时:       [30] 秒                                     │
│                                                         │
│ 【自动同步】                                             │
│ ☑ 启用自动同步                                           │
│ 同步时间:   [02:00]                                      │
│ 回溯小时:   [24]                                         │
│                                                         │
│ [保存配置]  [恢复默认]                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 认证流程

### 飞书 OAuth 登录流程

```
用户点击"使用飞书登录"
    ↓
重定向到飞书授权页面
https://open.feishu.cn/open-apis/authen/v1/authorize
    ↓
用户授权
    ↓
飞书回调到 /auth/feishu/callback
    ↓
后端获取 access_token 和用户信息
    ↓
查找或创建用户记录
    ↓
生成 JWT token
    ↓
前端存储 token 到 localStorage
    ↓
跳转到仪表盘
```

### JWT Token 结构

```json
{
  "sub": "user_id",
  "username": "zhangsan",
  "feishu_user_id": "ou_xxx",
  "role": "user",
  "exp": 1704038400,  // 过期时间
  "iat": 1703952000   // 签发时间
}
```

---

## 📡 API 设计

### 认证相关

```
POST   /api/auth/login              # 本地账号登录
POST   /api/auth/logout             # 登出
POST   /api/auth/refresh            # 刷新token
GET    /api/auth/me                 # 获取当前用户信息
GET    /api/auth/feishu/login       # 飞书登录跳转
GET    /api/auth/feishu/callback    # 飞书回调
```

### 报告相关

```
GET    /api/reports                 # 获取报告列表（分页、筛选）
GET    /api/reports/:id             # 获取报告详情
POST   /api/reports                 # 创建报告
PUT    /api/reports/:id             # 更新报告
DELETE /api/reports/:id             # 删除报告
GET    /api/reports/export          # 导出报告（CSV/Excel）
GET    /api/reports/stats           # 报告统计数据
```

### OKR 相关

```
GET    /api/okrs                    # 获取 OKR 列表
GET    /api/okrs/:id                # 获取 OKR 详情
POST   /api/okrs                    # 创建 OKR
PUT    /api/okrs/:id                # 更新 OKR
DELETE /api/okrs/:id                # 删除 OKR
GET    /api/okrs/sync               # 同步飞书 OKR
GET    /api/okrs/alignment/:report_id  # 获取报告的 OKR 对齐情况
```

### 用户相关

```
GET    /api/users                   # 获取用户列表（管理员）
GET    /api/users/:id               # 获取用户详情
PUT    /api/users/:id               # 更新用户信息
DELETE /api/users/:id               # 删除用户
GET    /api/users/team              # 获取团队成员
```

### 仪表盘相关

```
GET    /api/dashboard/stats         # 仪表盘统计数据
GET    /api/dashboard/trends        # 趋势数据（图表）
GET    /api/dashboard/risks         # 风险分布
GET    /api/dashboard/recent-reports  # 最近报告
```

---

## 🚀 实施路线图

### 阶段 1：基础架构（1-2周）⭐ 优先

- [ ] 数据库设计和迁移脚本
- [ ] 用户模型和认证系统（JWT）
- [ ] 基础 API 框架
- [ ] 前端脚手架搭建

### 阶段 2：核心功能（2-3周）

- [ ] 报告管理 CRUD API
- [ ] 报告列表和详情页面
- [ ] 仪表盘数据 API
- [ ] 仪表盘界面

### 阶段 3：飞书集成（1-2周）

- [ ] 飞书 OAuth 登录
- [ ] OKR 同步功能
- [ ] OKR 管理界面

### 阶段 4：高级功能（2-3周）

- [ ] 数据导出（Excel/PDF）
- [ ] 权限管理
- [ ] 审计日志
- [ ] 系统设置界面

### 阶段 5：优化部署（1周）

- [ ] 性能优化
- [ ] Docker 部署
- [ ] 文档完善
- [ ] 用户测试

---

## 📦 目录结构（扩展后）

```
feishu-hr-translator/
├── backend/                    # 后端（重命名 src）
│   ├── api/                    # API 路由
│   │   ├── auth.py            # 认证相关
│   │   ├── reports.py         # 报告相关
│   │   ├── okrs.py            # OKR 相关
│   │   ├── users.py           # 用户相关
│   │   └── dashboard.py       # 仪表盘
│   ├── models/                 # 数据库模型
│   │   ├── user.py
│   │   ├── report.py
│   │   ├── okr.py
│   │   └── session.py
│   ├── schemas/                # Pydantic 模型
│   ├── auth/                   # 认证逻辑
│   │   ├── jwt.py
│   │   └── feishu_oauth.py
│   ├── ai/                     # AI 集成（原有）
│   ├── feishu/                 # 飞书集成（原有）
│   ├── storage/                # 存储层（原有）
│   ├── database.py             # 数据库连接
│   └── main.py                 # FastAPI 应用
├── frontend/                   # 前端
│   ├── public/
│   ├── src/
│   │   ├── components/        # 组件
│   │   │   ├── Layout/
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Reports/
│   │   │   └── OKRs/
│   │   ├── pages/             # 页面
│   │   ├── api/               # API 调用
│   │   ├── utils/             # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── migrations/                 # 数据库迁移
│   └── versions/
├── docs/                       # 文档
│   ├── WEB_UI_DESIGN.md       # 本文档
│   ├── API_DOCS.md            # API 文档
│   └── DEPLOYMENT.md          # 部署文档
├── docker-compose.yml          # Docker 配置
└── README.md
```

---

## 🎯 下一步行动

1. **确认技术栈**：选择前端框架（React/Vue/纯HTML）
2. **数据库选择**：SQLite（开发）or PostgreSQL（生产）
3. **开始实施**：从阶段 1 开始逐步实现

---

**需要我开始实现吗？请告诉我：**
1. 选择哪个前端框架？（推荐 React + Ant Design）
2. 需要先实现哪个功能？（推荐从登录+仪表盘开始）
3. 是否需要完整的代码示例？
