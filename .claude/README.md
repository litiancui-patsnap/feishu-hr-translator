# Claude Code 配置说明

本目录包含了项目专用的 Claude Code subagents 和 skills 配置。

## 📁 目录结构

```
.claude/
├── agents/                          # Subagents（子代理）
│   └── feishu-optimizer.md         # 飞书内容优化专家
├── skills/                          # Skills（技能包）
│   └── deployment-check/           # 部署环境检查
│       └── SKILL.md
└── README.md                        # 本文档
```

## 🤖 Subagents

### feishu-optimizer（飞书内容优化专家）

**用途**：优化飞书机器人的 AI prompt 和卡片展示，确保内容通俗易懂。

**触发方式**：
```bash
# 自动触发（Claude 识别相关任务）
你：飞书卡片里有太多技术术语，HRBP 看不懂

# 手动指定
你：使用 feishu-optimizer 检查一下当前的 prompt 是否足够通俗
```

**主要功能**：
- ✅ 优化 AI prompt 模板（`src/ai/qwen.py`）
- ✅ 优化飞书卡片展示（`src/feishu/cards.py`）
- ✅ 识别和替换技术黑话
- ✅ 提供通俗化改进建议

**使用示例**：
```bash
# 场景 1：检查当前配置
你：帮我检查一下 AI prompt 是否会生成技术术语

# 场景 2：优化特定问题
你：用户反馈"O2KR1: TDD与BDD"看不懂，帮我优化一下

# 场景 3：全面审查
你：使用 feishu-optimizer 做一次完整的内容友好度审查
```

---

## 🎯 Skills

### deployment-check（部署环境检查）

**用途**：检查 Linux 服务器上的 Docker 部署配置和运行状态。

**触发方式**（Claude 自动识别以下关键词）：
- "部署检查"
- "环境配置"
- "服务器状态"
- "检查部署"
- "验证环境"

**检查项目**：
1. ✅ Docker 服务状态
2. ✅ 环境变量配置（`.env` 文件）
3. ✅ 网络连通性（飞书、DashScope）
4. ✅ 防火墙端口开放
5. ✅ 应用日志状态
6. ✅ 数据目录完整性
7. ✅ 容器资源使用

**使用示例**：
```bash
# 自动触发
你：帮我检查一下服务器部署是否正常
你：验证一下环境配置
你：看看部署有没有问题

# 获得的输出
✅ 通过项：Docker 运行正常、健康检查通过...
⚠️ 警告项：DashScope 响应较慢...
❌ 失败项：防火墙未开放 8080 端口
📊 总体评估：需改进（1 个严重问题需修复）
```

---

## 🚀 快速开始

### 1. 验证配置已加载

```bash
# 在 Claude Code 中运行
/agents

# 应该能看到 feishu-optimizer
```

### 2. 测试 Skill

```bash
# 直接询问（Claude 会自动调用 deployment-check skill）
你：检查一下部署环境
```

### 3. 使用 Subagent

```bash
# 让 Claude 自动选择合适的 subagent
你：帮我优化一下飞书卡片的内容，HRBP 反馈看不懂

# 或明确指定
你：使用 feishu-optimizer 分析一下 src/ai/qwen.py 的 prompt
```

---

## 📚 详细使用场景

### 场景 1：新部署后检查

```bash
你：我刚完成 Linux 服务器部署，帮我检查一下环境

Claude：我来执行一次完整的部署环境检查...
        （自动调用 deployment-check skill）

        ✅ Docker 和 Docker Compose 已正确安装
        ✅ 应用容器正在运行
        ✅ 健康检查端点返回正常
        ❌ 防火墙未开放 8080 端口

        建议执行：sudo ufw allow 8080
```

### 场景 2：内容优化迭代

```bash
你：用户反馈周报卡片里"O2KR1: TDD与BDD模式研究尚未完成"看不懂

Claude：我会调用 feishu-optimizer 来优化这个问题...

        🔍 问题分析：
        prompt 中对 gaps 字段的描述不够明确，导致 AI 输出了技术术语

        💡 优化方案：
        在约束条件中明确要求"不要输出 O2KR1 这样的格式"

        📝 修改内容：
        [显示具体的代码改动]

        🧪 测试建议：
        docker-compose restart app && 发送测试消息
```

### 场景 3：故障排查

```bash
你：服务无法访问了，帮我查一下

Claude：让我做一次全面的环境检查...
        （调用 deployment-check skill）

        ❌ 健康检查失败：连接超时
        ✅ 容器正在运行

        正在查看日志...
        发现问题：DashScope API Key 过期

        修复建议：
        1. 更新 .env 中的 DASHSCOPE_API_KEY
        2. 重启服务：docker-compose restart app
```

---

## 🔧 配置修改

### 修改 Subagent

编辑对应的 `.md` 文件：
```bash
nano .claude/agents/feishu-optimizer.md
```

修改后无需重启 Claude Code，会自动重新加载。

### 修改 Skill

编辑对应的 `SKILL.md` 文件：
```bash
nano .claude/skills/deployment-check/SKILL.md
```

### 添加新的 Subagent 或 Skill

参考现有文件的格式创建新文件即可。

---

## 📊 团队协作

### 共享配置

这些配置文件已纳入 Git 版本控制，团队成员只需：

```bash
git pull
```

即可获得最新的 subagents 和 skills。

### 贡献改进

如果你对现有配置有改进建议：

1. 修改对应的 `.md` 文件
2. 提交到 Git
3. 通知团队成员更新

```bash
git add .claude/
git commit -m "优化 feishu-optimizer 的通俗化词汇表"
git push
```

---

## ⚠️ 注意事项

1. **首次使用**：Claude 需要一些时间"学习"何时调用这些 subagents/skills
2. **明确表达**：如果 Claude 没有自动调用，尝试更明确地描述你的需求
3. **反馈改进**：如果发现触发不准确，可以优化 `description` 字段
4. **版本控制**：重要的配置修改建议先测试，再提交到 Git

---

## 🆘 故障排查

### Subagent 未被调用

**检查**：
```bash
# 查看文件格式是否正确
cat .claude/agents/feishu-optimizer.md | head -10

# 确认 YAML frontmatter 格式正确
# 确认 description 清晰描述了使用场景
```

### Skill 未被触发

**尝试**：
- 使用更明确的关键词（参考 description 中的触发词）
- 直接说"使用 deployment-check skill"
- 检查 SKILL.md 文件格式是否正确

---

## 📖 参考资料

- [Claude Code Subagents 文档](https://code.claude.com/docs/en/sub-agents.md)
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills.md)
- [项目主 README](../README.md)

---

**最后更新**：2025-11-14
**维护者**：项目团队
