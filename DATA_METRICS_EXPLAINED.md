# 数据指标来源说明

> 📊 本文档详细解释飞书 HR 翻译器系统中各项数据指标的来源和计算逻辑

---

## 📌 目录

1. [数据流程概览](#数据流程概览)
2. [核心指标详解](#核心指标详解)
3. [计算公式](#计算公式)
4. [数据存储结构](#数据存储结构)

---

## 数据流程概览

### 完整的数据链路

```
员工提交飞书日报/周报
    ↓
系统接收 Webhook 触发
    ↓
调用 AI (Qwen) 分析报告内容
    ↓
AI 生成结构化数据（包含 OKR 信心度、风险等级等）
    ↓
保存到 CSV 文件 (data/reports_slim.csv)
    ↓
Web UI 读取 CSV 并计算统计指标
    ↓
在统计分析页面显示
```

---

## 核心指标详解

您在统计分析页面看到的指标，都是基于 **AI 对员工工作报告的分析结果**。

### 1️⃣ 平均 OKR 信心度 (Average OKR Confidence)

#### 📍 数据来源

**AI 自动评估**，基于员工报告内容与公司 OKR 目标的匹配程度。

#### 🔍 评估维度

AI 在分析每份报告时，会：
1. **对比公司 OKR**：从 `data/okr_cache.json` 读取公司的 OKR 目标
2. **匹配工作内容**：分析员工的工作是否与 OKR 对齐
3. **计算信心度**：生成 0-1 之间的数值
   - `0.0` = 完全不匹配 OKR
   - `0.5` = 部分匹配
   - `1.0` = 完全匹配 OKR

#### 💾 存储位置

- **字段名**：`okr_confidence`
- **文件**：`data/reports_slim.csv`
- **格式**：浮点数（例如 `0.85` 表示 85% 的信心度）

#### 📊 统计页面计算方式

**平均 OKR 信心度** = 所有报告的 `okr_confidence` 之和 ÷ 报告总数

```python
# 代码位置: backend/services/report_stats.py 第 648-658 行
okr_confidences = []
for report in all_reports:
    okr_confidence = report.get("okr_confidence")
    if okr_confidence is not None:
        okr_confidences.append(float(okr_confidence))

avg_okr_confidence = sum(okr_confidences) / len(okr_confidences) if okr_confidences else 0.0
```

**显示结果**：0-100 的百分比（`avg_okr_confidence * 100`）

---

### 2️⃣ 高风险率 (High Risk Rate)

#### 📍 数据来源

**AI 自动评估**，基于报告中提到的风险和问题。

#### 🔍 评估逻辑

AI 在分析每份报告时，会：
1. **识别风险项**：提取报告中的问题、阻碍、挑战等
2. **评估严重程度**：根据风险的影响和紧急性分级
3. **判定风险等级**：
   - `low`（低风险）：小问题、可控风险
   - `medium`（中风险）：需要关注的风险
   - `high`（高风险）：严重问题、紧急风险

#### 💾 存储位置

- **字段名**：`risk_level`
- **文件**：`data/reports_slim.csv`
- **可选值**：`low`, `medium`, `high`

#### 📊 统计页面计算方式

**高风险率** = 高风险报告数 ÷ 报告总数 × 100%

```python
# 代码位置: backend/services/report_stats.py 第 635-667 行
high_risk_count = sum(1 for r in all_reports if r.get("risk_level") == "high")
total_reports = len(all_reports)

high_risk_rate = high_risk_count / total_reports if total_reports > 0 else 0
```

**显示结果**：0-100 的百分比

---

### 3️⃣ 高风险项 (High Risk Items)

#### 📍 数据来源

与"高风险率"相同，也是 **AI 自动评估**。

#### 💾 存储位置

同上：`data/reports_slim.csv` 的 `risk_level` 字段

#### 📊 统计页面计算方式

**高风险项** = 风险等级为 `high` 的报告总数

```python
# 代码位置: backend/services/report_stats.py 第 107-109 行
high_risk_items = sum(
    1 for r in all_reports if r.get("risk_level") == "high"
)
```

**显示结果**：整数（例如 `5` 表示有 5 份高风险报告）

---

### 4️⃣ 平均 OKR 信心 (Average OKR Confidence in User Ranking)

#### 📍 数据来源

与"平均 OKR 信心度"相同，都是基于 AI 评估的 `okr_confidence`。

#### 💾 存储位置

同上：`data/reports_slim.csv` 的 `okr_confidence` 字段

#### 📊 统计页面计算方式

**按用户分组计算**：

1. 筛选最近 30 天的报告
2. 按用户名分组
3. 计算每个用户所有报告的平均信心度
4. 按信心度从高到低排序

```python
# 代码位置: backend/services/report_stats.py 第 560-621 行
for report in all_reports:
    user_name = report.get("user_name")
    okr_confidence = float(report.get("okr_confidence"))

    # 累加该用户的信心度
    user_okr[user_name]["confidence_sum"] += okr_confidence
    user_okr[user_name]["confidence_count"] += 1

# 计算平均值
avg_confidence = confidence_sum / confidence_count
```

**显示结果**：用户排名表中每个人的平均信心度百分比

---

## 计算公式

### 团队总览指标

| 指标 | 公式 | 说明 |
|------|------|------|
| **团队总人数** | `DISTINCT(user_name)` | 去重的用户数 |
| **总报告数** | `COUNT(*)` | 所有报告总数 |
| **人均报告数** | `总报告数 ÷ 团队总人数` | 平均每人提交的报告数 |
| **平均OKR信心度** | `SUM(okr_confidence) ÷ COUNT(*)` | 所有报告的平均信心度 |
| **高风险率** | `COUNT(risk_level='high') ÷ COUNT(*) × 100%` | 高风险报告占比 |

### 用户维度指标

| 指标 | 公式 | 说明 |
|------|------|------|
| **总报告数** | `COUNT(*) WHERE user_name=X` | 该用户的报告总数 |
| **周报数** | `COUNT(*) WHERE period_type='weekly'` | 该用户提交的周报数 |
| **月报数** | `COUNT(*) WHERE period_type='monthly'` | 该用户提交的月报数 |
| **高风险项** | `COUNT(*) WHERE risk_level='high'` | 该用户的高风险报告数 |
| **平均OKR信心** | `SUM(okr_confidence) ÷ COUNT(*)` | 该用户的平均信心度 |

### 趋势分析指标

| 指标 | 公式 | 说明 |
|------|------|------|
| **日报告数** | `COUNT(*) WHERE DATE(created_at)=X` | 某一天的报告总数 |
| **日均OKR信心** | `AVG(okr_confidence) WHERE DATE(created_at)=X` | 某一天的平均信心度 |
| **日风险分布** | `COUNT(*) GROUP BY risk_level` | 某一天各风险等级的报告数 |

---

## 数据存储结构

### CSV 文件字段说明

系统将所有数据保存在 `data/reports_slim.csv` 文件中，字段如下：

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `user_id` | String | 飞书用户ID | `ou_1303116...` |
| `user_name` | String | 用户姓名 | `张三` |
| `period_type` | String | 报告类型 | `daily`, `weekly`, `monthly` |
| `period_start` | Date | 报告开始日期 | `2025-12-17` |
| `period_end` | Date | 报告结束日期 | `2025-12-17` |
| `message_ts` | DateTime | 提交时间 | `2025-12-17T14:30:00` |
| `raw_text` | String | 员工原始报告内容 | `今天完成了...` |
| `hr_summary` | String | AI生成的HR友好总结 | `该员工本周主要...` |
| **`risk_level`** | String | **风险等级** | `low`, `medium`, `high` |
| `risks` | String | 风险项列表（分号分隔） | `项目延期(high);资源不足(medium)` |
| `needs` | String | 需求和帮助 | `需要技术支持:张经理` |
| `hit_objectives` | String | 命中的OKR目标 | `提升产品质量;优化用户体验` |
| `hit_krs` | String | 命中的关键结果 | `Bug减少30%;响应时间降低20%` |
| `okr_gaps` | String | OKR差距 | `尚未完成测试覆盖率目标` |
| **`okr_confidence`** | Float | **OKR信心度（0-1）** | `0.85` |
| `next_actions` | String | 下一步行动 | `完成UI设计;提交代码审查` |
| `okr_brief` | String | OKR简要说明 | `本周工作与Q4 OKR对齐良好` |

---

## AI 如何生成这些数据？

### 处理流程

1. **接收报告**：系统收到员工的飞书日报/周报
2. **读取 OKR**：从 `data/okr_cache.json` 加载公司 OKR 目标
3. **调用 AI**：将报告和 OKR 发送给 Qwen 大模型
4. **结构化输出**：AI 返回 JSON 格式的分析结果

### AI Prompt 模板

系统使用的 AI 指令模板（部分）：

```
请分析以下工作报告，并生成 HR 易读的总结：

工作报告：{员工原始内容}
公司 OKR：{OKR目标列表}

请按以下格式输出：
{
  "hr_summary": "通俗易懂的工作总结",
  "risk_level": "low|medium|high",
  "risks": [{"item": "风险描述", "likelihood": "high"}],
  "okr_alignment": {
    "hit_objectives": ["命中的目标1", "目标2"],
    "hit_krs": ["命中的关键结果1", "关键结果2"],
    "gaps": ["未完成的OKR项"],
    "confidence": 0.85  // ← OKR 信心度在这里生成
  }
}
```

### AI 代码位置

- **主要逻辑**：[src/ai/qwen.py](src/ai/qwen.py)
- **数据模型**：[src/schemas.py](src/schemas.py)
- **存储逻辑**：[src/storage/csv_store.py](src/storage/csv_store.py)

---

## 常见问题

### ❓ Q1：OKR 信心度为什么是 0%？

**可能原因：**
1. 系统还没有 OKR 数据（`data/okr_cache.json` 为空或不存在）
2. 员工报告内容与 OKR 完全不匹配
3. AI 分析失败（网络问题、API 配额不足等）

**解决方法：**
1. 确认 OKR 数据已同步：点击"OKR管理" → "同步OKR"
2. 检查员工报告是否包含工作内容（不能只写"今天请假"）
3. 查看后端日志确认 AI 调用是否成功

---

### ❓ Q2：高风险率是 AI 自动判断的吗？

**是的！** 风险等级完全由 AI 自动评估。

AI 会根据报告中的关键词和语义分析：
- 提到"延期"、"阻碍"、"问题" → 可能标记为高风险
- 提到"进展顺利"、"按计划完成" → 通常标记为低风险

---

### ❓ Q3：可以手动修改某份报告的风险等级吗？

**目前不支持**。所有指标都是基于 CSV 文件的原始数据计算的。

如果需要修改，可以：
1. 直接编辑 `data/reports_slim.csv` 文件（不推荐，重启后可能被覆盖）
2. 联系技术人员调整 AI Prompt，改进风险评估逻辑

---

### ❓ Q4：为什么用户排名中有人信心度特别低？

**可能原因：**
1. 该员工的工作内容与当前 OKR 不匹配
2. 该员工提交的报告过于简单（例如只有一句话）
3. OKR 数据不完整，导致匹配度低

**建议：**
1. 提醒员工详细填写工作内容
2. 确认 OKR 数据涵盖了该员工的工作方向
3. 查看该员工的具体报告，了解为何信心度低

---

### ❓ Q5：统计数据多久更新一次？

**实时更新！** 每次员工提交报告后：

1. AI 立即分析并生成指标
2. 数据保存到 CSV 文件
3. Web UI 页面刷新时自动读取最新数据

无需手动刷新，打开统计页面即可看到最新数据。

---

## 📚 相关文档

- **[Web 操作手册](WEB_USER_GUIDE.md)** - 详细的使用指南
- **[部署文档](deploy/DEPLOYMENT.md)** - 服务器部署说明
- **[项目总体说明](README.md)** - 项目介绍和配置

---

## 🔍 技术人员参考

### 核心代码文件

| 文件 | 作用 |
|------|------|
| `backend/services/report_stats.py` | 统计指标计算逻辑 |
| `src/ai/qwen.py` | AI 分析和数据生成 |
| `src/schemas.py` | 数据模型定义 |
| `src/storage/csv_store.py` | CSV 存储逻辑 |
| `frontend/src/pages/AnalyticsPage.tsx` | 统计页面前端 |

### API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/dashboard/analytics/team-stats` | 团队总体统计 |
| `GET /api/dashboard/analytics/user-submissions` | 用户提交统计 |
| `GET /api/dashboard/analytics/risk-trend` | 风险趋势数据 |
| `GET /api/dashboard/analytics/okr-ranking` | OKR 信心度排名 |

---

**祝您使用愉快！** 🎉

如有任何疑问，欢迎随时联系技术支持团队。
