# Feishu HR Translator - Web UI 版本

> AI驱动的HR报告翻译系统 - 现在支持完整的Web管理界面！

---

## ✨ 新功能

### 🎨 Web 管理界面

- **登录系统**
  - ✅ 用户名/密码登录
  - ✅ JWT Token 认证
  - ✅ 记住我功能（7天免登录）
  - 🚧 飞书 OAuth 登录（即将推出）

- **仪表盘**
  - ✅ 数据统计卡片（本周/月报告、风险项、OKR完成度）
  - ✅ 趋势指标（增长率显示）
  - ✅ 最近报告列表
  - 🚧 趋势图表（即将推出）
  - 🚧 风险分布饼图（即将推出）

- **即将推出**
  - 📝 报告管理（查看、搜索、筛选、导出）
  - 🎯 OKR 管理（进度追踪、对齐分析）
  - 👥 团队视图（成员统计、OKR 展示）
  - ⚙️ 系统设置（个人设置、系统配置）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装后端依赖
pip install -r requirements-web.txt

# 安装前端依赖
cd frontend
npm install
```

### 2. 创建管理员账号

```bash
python scripts/create_admin.py
```

会创建默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

### 3. 启动服务

**开发模式**（推荐）：

```bash
# 终端 1 - 后端
python -m backend.web_main

# 终端 2 - 前端
cd frontend
npm run dev
```

访问：`http://localhost:3000`

**生产模式**：

```bash
# 构建前端
cd frontend
npm run build

# 启动后端（会自动serve前端）
cd ..
python -m backend.web_main
```

访问：`http://localhost:8080`

---

## 📖 文档

- **快速开始**：[docs/WEB_UI_QUICKSTART.md](docs/WEB_UI_QUICKSTART.md)
- **完整设计**：[docs/WEB_UI_DESIGN.md](docs/WEB_UI_DESIGN.md)
- **API文档**：访问 `http://localhost:8080/docs`

---

## 🏗️ 技术栈

### 后端
- FastAPI - Web框架
- SQLAlchemy - ORM
- JWT - 认证
- SQLite - 数据库（开发）
- PostgreSQL - 数据库（生产，可选）

### 前端
- React 18 - UI框架
- TypeScript - 类型安全
- Ant Design - UI组件库
- Vite - 构建工具
- Axios - HTTP客户端

---

## 📂 项目结构

```
feishu-hr-translator/
├── backend/              # 后端（FastAPI）
│   ├── api/             # API路由
│   ├── auth/            # 认证模块
│   ├── models/          # 数据库模型
│   └── web_main.py      # 主入口
├── frontend/            # 前端（React）
│   ├── src/
│   │   ├── api/        # API客户端
│   │   ├── pages/      # 页面组件
│   │   └── contexts/   # React Context
│   └── package.json
├── src/                 # 原有代码（飞书集成、AI翻译）
├── data/                # 数据目录
│   └── hr_translator.db # SQLite数据库
├── docs/                # 文档
└── scripts/             # 脚本
    └── create_admin.py  # 创建管理员账号
```

---

## 🎯 功能路线图

### ✅ 已完成（v1.0 - 登录 + 仪表盘）
- [x] 用户认证系统（JWT）
- [x] 登录页面
- [x] 仪表盘基础版
- [x] 数据统计卡片
- [x] 最近报告列表

### 🚧 开发中（v1.1 - 报告管理）
- [ ] 报告列表页面
- [ ] 报告详情页面
- [ ] 报告筛选和搜索
- [ ] 数据导出（CSV/Excel）

### 📅 计划中（v1.2 - OKR管理）
- [ ] OKR列表和详情
- [ ] OKR进度追踪
- [ ] OKR对齐分析
- [ ] 飞书OKR同步

### 🔮 未来版本
- [ ] 飞书OAuth登录
- [ ] 团队视图
- [ ] 权限管理
- [ ] 系统设置
- [ ] 多语言支持

---

## 🐛 故障排查

### 常见问题

**Q1: 后端启动失败 - ModuleNotFoundError**
```bash
pip install -r requirements-web.txt
```

**Q2: 登录失败 - 401 Unauthorized**
```bash
python scripts/create_admin.py
```

**Q3: 数据库表不存在**
```python
from backend.database import init_db
init_db()
```

更多问题请查看 [WEB_UI_QUICKSTART.md](docs/WEB_UI_QUICKSTART.md)

---

## 📸 界面预览

### 登录页面
- 简洁的登录表单
- 飞书品牌色渐变背景
- 响应式设计

### 仪表盘
- 4个统计卡片（报告数量、风险、OKR）
- 趋势指标（↑/↓ 百分比）
- 最近报告表格（用户、周期、风险等级、摘要）

---

## 🤝 贡献指南

欢迎贡献代码！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 📞 联系我们

- 问题反馈：GitHub Issues
- 完整文档：[docs/](docs/)

---

**Happy Coding! 🎉**
