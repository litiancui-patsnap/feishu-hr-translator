# Bug 修复：导出 CSV 跨域错误

## 🐛 问题描述

在生产环境（Docker 部署）中，点击"导出 CSV"按钮时出现跨域错误：

```
Strict-Origin-When-Cross-Origin
```

错误截图显示请求被浏览器阻止，原因是使用了硬编码的 `http://localhost:8080` URL。

## 🔍 根本原因

在以下两个文件中，CSV 导出功能使用了硬编码的绝对 URL：

1. **[frontend/src/pages/ReportDetailPage.tsx](frontend/src/pages/ReportDetailPage.tsx)** (第 71 行)
2. **[frontend/src/pages/ReportsListPage.tsx](frontend/src/pages/ReportsListPage.tsx)** (第 111 行)

### 问题代码

```typescript
// ❌ 错误：硬编码的绝对 URL
const url = `http://localhost:8080/api/dashboard/reports/${id}/export`
```

### 为什么会出错？

在 Docker 生产环境中：
- 前端运行在 `http://服务器IP:8888`
- 代码中请求 `http://localhost:8080`（不同的域名/端口）
- 浏览器检测到跨域请求，触发 CORS 策略阻止

## ✅ 修复方案

将硬编码的绝对 URL 改为**相对路径**，让请求通过 Nginx 反向代理转发到后端。

### 修复后的代码

```typescript
// ✅ 正确：使用相对路径
const url = `/api/dashboard/reports/${id}/export`
```

### 工作原理

1. 前端发送请求：`/api/dashboard/reports/10005/export`
2. Nginx 接收请求并匹配路由规则：
   ```nginx
   location /api/ {
       proxy_pass http://backend:8080/api/;
   }
   ```
3. Nginx 转发到后端：`http://backend:8080/api/dashboard/reports/10005/export`
4. 后端处理并返回 CSV 文件
5. Nginx 将响应返回给前端
6. 前端触发下载

## 📝 修改的文件

### 1. [frontend/src/utils/export.ts](frontend/src/utils/export.ts)

**位置**: 第 142 行

**问题**: Token 键名不一致导致 401 Unauthorized 错误

**修改前**:
```typescript
const token = localStorage.getItem('token')
```

**修改后**:
```typescript
const token = localStorage.getItem('access_token')
```

**说明**:
- 系统其他地方使用 `access_token` 作为 localStorage 键名
- 导出函数错误地使用了 `token`
- 导致获取到 `null`，Authorization header 为 `Bearer null`
- 后端返回 401 Unauthorized

---

### 2. [frontend/src/pages/ReportDetailPage.tsx](frontend/src/pages/ReportDetailPage.tsx)

**位置**: 第 71 行

**问题**: 硬编码 localhost:8080 导致跨域错误

**修改前**:
```typescript
const handleExportCSV = async () => {
  if (!id) return
  try {
    const url = `http://localhost:8080/api/dashboard/reports/${id}/export`
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    await downloadExportFile(url, `report_${id}_${timestamp}.csv`)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
    console.error(error)
  }
}
```

**修改后**:
```typescript
const handleExportCSV = async () => {
  if (!id) return
  try {
    const url = `/api/dashboard/reports/${id}/export`  // ← 改为相对路径
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    await downloadExportFile(url, `report_${id}_${timestamp}.csv`)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
    console.error(error)
  }
}
```

---

### 3. [frontend/src/pages/ReportsListPage.tsx](frontend/src/pages/ReportsListPage.tsx)

**位置**: 第 111 行

**问题**: 硬编码 localhost:8080 导致跨域错误

**修改前**:
```typescript
const handleExportCSV = async () => {
  try {
    const params = new URLSearchParams()
    if (riskLevel) params.append('risk_level', riskLevel)
    if (periodType) params.append('period_type', periodType)
    if (userName) params.append('user_name', userName)
    if (searchKeyword) params.append('search', searchKeyword)
    if (dateRange?.[0]) params.append('start_date', dateRange[0].format('YYYY-MM-DD'))
    if (dateRange?.[1]) params.append('end_date', dateRange[1].format('YYYY-MM-DD'))

    const url = `http://localhost:8080/api/dashboard/reports/export?${params.toString()}`
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    await downloadExportFile(url, `reports_export_${timestamp}.csv`)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
    console.error(error)
  }
}
```

**修改后**:
```typescript
const handleExportCSV = async () => {
  try {
    const params = new URLSearchParams()
    if (riskLevel) params.append('risk_level', riskLevel)
    if (periodType) params.append('period_type', periodType)
    if (userName) params.append('user_name', userName)
    if (searchKeyword) params.append('search', searchKeyword)
    if (dateRange?.[0]) params.append('start_date', dateRange[0].format('YYYY-MM-DD'))
    if (dateRange?.[1]) params.append('end_date', dateRange[1].format('YYYY-MM-DD'))

    const url = `/api/dashboard/reports/export?${params.toString()}`  // ← 改为相对路径
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    await downloadExportFile(url, `reports_export_${timestamp}.csv`)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
    console.error(error)
  }
}
```

## 🚀 部署更新

### 方式一：重新构建前端容器（推荐）

```bash
cd ~/feishu-hr-translator/deploy

# 停止容器
docker-compose -f docker-compose.production.yml down

# 重新构建前端镜像
docker-compose -f docker-compose.production.yml build --no-cache frontend

# 启动所有容器
docker-compose -f docker-compose.production.yml up -d

# 查看日志
docker-compose -f docker-compose.production.yml logs -f frontend
```

### 方式二：使用部署脚本

```bash
cd ~/feishu-hr-translator/deploy
./deploy.sh
```

## ✅ 验证修复

1. 访问 Web UI：`http://服务器IP:8888`
2. 登录系统
3. 进入"报告管理"页面
4. 点击"导出 CSV (全部)"按钮
5. 或者点击某个报告详情，点击"导出 CSV"按钮
6. 应该能成功下载 CSV 文件，不再出现跨域错误

## 📚 相关知识

### 为什么 API 请求不需要修改？

项目中的其他 API 请求（如登录、获取报告列表等）使用了统一的 API 客户端：

**[frontend/src/api/client.ts](frontend/src/api/client.ts)**:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8080')
```

- **开发环境** (`npm run dev`): `API_BASE_URL = 'http://localhost:8080'`
- **生产环境** (Docker): `API_BASE_URL = ''` (相对路径)

因此，通过 `apiClient` 发起的请求在生产环境会自动使用相对路径。

### 为什么 CSV 导出要单独处理？

CSV 导出使用了 `downloadExportFile` 函数，直接通过 `fetch` API 请求后端，而不是通过 `apiClient`。因此需要手动确保 URL 是相对路径。

**[frontend/src/utils/export.ts](frontend/src/utils/export.ts)** (第 140-166 行):
```typescript
export const downloadExportFile = async (url: string, filename: string) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(url, {  // ← 直接使用 fetch
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    // ... 处理下载
  }
}
```

## 🎓 经验总结

### 最佳实践

1. ✅ **使用相对路径**：在前端代码中，所有 API 请求都应使用相对路径
2. ✅ **统一 API 客户端**：尽量使用 Axios 实例或封装的 API 客户端
3. ✅ **环境变量配置**：通过环境变量区分开发和生产环境
4. ✅ **Nginx 反向代理**：在生产环境使用 Nginx 统一代理后端请求

### 避免的错误

1. ❌ **硬编码 localhost**：永远不要在前端代码中硬编码 `localhost`
2. ❌ **硬编码端口**：端口应该通过配置文件或环境变量指定
3. ❌ **绕过 CORS**：不要试图通过配置 CORS 来"修复"跨域问题，应该从架构上避免跨域

## 📞 参考文档

- [Nginx 配置文件](deploy/nginx.conf)
- [前端 API 客户端配置](frontend/src/api/client.ts)
- [Vite 配置文件](frontend/vite.config.ts)
- [部署文档](deploy/DEPLOYMENT.md)

---

**修复完成时间**: 2025-12-19

**修复人员**: Claude Code AI Assistant

**测试状态**: ✅ 待用户验证
