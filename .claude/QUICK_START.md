# 🚀 Claude Code 快速参考

## 30 秒快速开始

### ✅ Skill：部署环境检查
```bash
你：检查一下部署环境
```
自动检查 Docker、.env、网络、日志等 7 项配置

### ✅ Subagent：内容优化
```bash
你：帮我优化飞书卡片，HRBP 看不懂技术术语
```
自动调用 feishu-optimizer 分析和优化

---

## 📋 常用命令

| 你想做什么 | 说什么 |
|-----------|--------|
| 检查服务器部署 | "检查部署环境" / "验证服务器配置" |
| 优化 HR 总结 | "优化飞书内容" / "消除技术黑话" |
| 查看可用 agents | `/agents` |
| 明确指定 agent | "使用 feishu-optimizer ..." |

---

## 🎯 典型场景

### 场景 1：刚部署完
```
你：我刚在 Linux 上部署完，帮我全面检查一下
→ 自动调用 deployment-check
→ 输出完整的健康检查报告
```

### 场景 2：用户反馈看不懂
```
你：HRBP 反馈"O2KR1: TDD与BDD"看不懂，帮我优化
→ 自动调用 feishu-optimizer
→ 分析问题并修改代码
→ 提供测试方法
```

### 场景 3：服务异常
```
你：服务无法访问了，查一下原因
→ 调用 deployment-check 做全面检查
→ 分析日志找出问题
→ 给出具体修复建议
```

---

## 💡 Pro Tips

1. **越具体越好**：说"优化 gaps 字段的技术术语"比"优化内容"更精准
2. **多用关键词**：说"部署检查"、"环境配置"等触发词
3. **可以明确指定**：说"使用 feishu-optimizer"强制调用
4. **查看已配置的 agents**：运行 `/agents` 命令

---

## 📞 需要帮助？

- 查看详细说明：`cat .claude/README.md`
- Claude Code 文档：https://code.claude.com/docs
- 项目文档：`README.md`
