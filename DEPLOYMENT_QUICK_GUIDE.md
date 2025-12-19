# 快速部署指南 - 修复导出 CSV 功能

## 📋 需要更新的文件

本次修复涉及 **4 个文件**：

### 前端文件（3 个）
1. `frontend/src/pages/ReportDetailPage.tsx` - 报告详情页导出
2. `frontend/src/pages/ReportsListPage.tsx` - 报告列表页导出
3. `frontend/src/utils/export.ts` - 导出工具函数

### 后端文件（1 个）
4. `backend/api/dashboard.py` - 后端 API 接口

---

## 🚀 部署步骤

### 方式 A：使用 Git（推荐）

#### 第 1 步：在本地推送代码
```bash
git push origin master
```

#### 第 2 步：在服务器上执行
```bash
# 进入项目目录
cd ~/feishu-hr-translator

# 拉取最新代码
git pull origin master

# 进入部署目录
cd deploy

# 停止所有容器
docker-compose -f docker-compose.production.yml down

# 重新构建（前后端都需要重建）
docker-compose -f docker-compose.production.yml build --no-cache

# 启动所有容器
docker-compose -f docker-compose.production.yml up -d

# 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

---

### 方式 B：手动上传文件

#### 第 1 步：上传文件到服务器

使用 `scp` 命令上传以下文件：

```bash
# 从 Windows 本地上传到 Linux 服务器

# 上传前端文件
scp frontend/src/pages/ReportDetailPage.tsx root@服务器IP:~/feishu-hr-translator/frontend/src/pages/
scp frontend/src/pages/ReportsListPage.tsx root@服务器IP:~/feishu-hr-translator/frontend/src/pages/
scp frontend/src/utils/export.ts root@服务器IP:~/feishu-hr-translator/frontend/src/utils/

# 上传后端文件
scp backend/api/dashboard.py root@服务器IP:~/feishu-hr-translator/backend/api/
```

#### 第 2 步：在服务器上重新构建和部署

```bash
cd ~/feishu-hr-translator/deploy

# 停止所有容器
docker-compose -f docker-compose.production.yml down

# 重新构建前端和后端
docker-compose -f docker-compose.production.yml build --no-cache frontend
docker-compose -f docker-compose.production.yml build --no-cache backend

# 启动所有容器
docker-compose -f docker-compose.production.yml up -d

# 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

---

## ✅ 验证修复

部署完成后，按以下步骤验证：

### 1. 重新登录系统
访问 `http://192.168.106.97:8888`，登出后重新登录（获取新的 Token）

### 2. 测试报告详情导出
1. 进入任意一个报告详情页
2. 点击"导出 CSV"按钮
3. ✅ 应该成功下载 CSV 文件

### 3. 测试报告列表导出
1. 进入报告列表页面
2. 点击"导出 CSV (全部)"按钮
3. ✅ 应该成功下载 CSV 文件

### 4. 检查浏览器控制台（F12）
- ✅ 没有跨域错误
- ✅ 没有 401 Unauthorized 错误
- ✅ 没有 422 Unprocessable Entity 错误
- ✅ 请求状态码为 200

---

## 🐛 修复的问题总结

| 问题 | 错误代码 | 原因 | 修复 |
|------|----------|------|------|
| **跨域错误** | CORS | 硬编码 `localhost:8080` | 改为相对路径 `/api/...` |
| **未授权错误** | 401 | Token 键名不一致 (`'token'` vs `'access_token'`) | 统一使用 `'access_token'` |
| **参数验证失败** | 422 | 缺少 `Optional` 类型注解 | 添加 `Optional[str]` |

---

## 📝 重要提醒

### ⚠️ 必须重新构建容器

修改代码后，**必须重新构建 Docker 镜像**，否则容器内运行的还是旧代码！

```bash
# ❌ 错误做法（只重启，不会更新代码）
docker-compose restart

# ✅ 正确做法（重新构建并启动）
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### ⚠️ 必须重新登录

修改后端代码后，建议重新登录系统以获取新的 Token。

### ⚠️ 清除浏览器缓存

如果问题持续，尝试：
1. 按 `Ctrl + Shift + Delete` 清除浏览器缓存
2. 或使用无痕模式访问

---

## 🔍 故障排查

### 问题：还是报跨域错误

**检查**：
```bash
# 查看前端容器内的代码
docker exec feishu-hr-frontend cat /usr/share/nginx/html/assets/*.js | grep "localhost:8080"
```

**预期**：应该没有输出

**修复**：重新构建前端
```bash
docker-compose -f docker-compose.production.yml build --no-cache frontend
docker-compose -f docker-compose.production.yml up -d
```

---

### 问题：还是报 401 错误

**检查**：浏览器开发者工具 → Application → Local Storage → 查看 `access_token` 是否存在

**修复**：
1. 清除浏览器缓存
2. 重新登录系统

---

### 问题：还是报 422 错误

**检查**：后端日志
```bash
docker-compose -f docker-compose.production.yml logs backend --tail 100
```

**修复**：确保后端容器已重新构建
```bash
docker-compose -f docker-compose.production.yml build --no-cache backend
docker-compose -f docker-compose.production.yml up -d
```

---

## 📊 文件变更对比

### frontend/src/utils/export.ts
```diff
- const token = localStorage.getItem('token')
+ const token = localStorage.getItem('access_token')
```

### frontend/src/pages/ReportDetailPage.tsx
```diff
- const url = `http://localhost:8080/api/dashboard/reports/${id}/export`
+ const url = `/api/dashboard/reports/${id}/export`
```

### frontend/src/pages/ReportsListPage.tsx
```diff
- const url = `http://localhost:8080/api/dashboard/reports/export?${params.toString()}`
+ const url = `/api/dashboard/reports/export?${params.toString()}`
```

### backend/api/dashboard.py
```diff
- from typing import List
+ from typing import List, Optional

  @router.get("/reports/export")
  async def export_reports(
-     risk_level: str = None,
+     risk_level: Optional[str] = None,
      # ... 其他参数同样修改
```

---

## 📚 相关文档

- [详细修复文档](BUGFIX_EXPORT_CSV.md)
- [完整部署文档](deploy/DEPLOYMENT.md)
- [Web 操作手册](WEB_USER_GUIDE.md)
- [技术栈说明](TECH_STACK.md)

---

**更新日期**: 2025-12-19

**修复完成** ✅
