# 部署路由顺序修复

## 📋 修复内容

修复了报告列表 CSV 导出的 422 错误，原因是 FastAPI 路由定义顺序不正确。

## 🚀 部署步骤

### 方法一：通过 Git（推荐）

在服务器上执行：

```bash
cd ~/feishu-hr-translator

# 拉取最新代码
git pull origin master

# 重新构建后端容器
cd deploy
docker-compose -f docker-compose.production.yml build --no-cache backend

# 重启容器
docker-compose -f docker-compose.production.yml up -d

# 查看后端日志，确认启动成功
docker-compose -f docker-compose.production.yml logs -f backend
```

### 方法二：手动上传文件

如果服务器无法访问 Git，可以手动上传修改的文件：

**1. 上传文件到服务器**

从本地将 `backend/api/dashboard.py` 上传到服务器：

```bash
# Windows PowerShell
scp backend\api\dashboard.py root@服务器IP:~/feishu-hr-translator/backend/api/

# Linux/Mac
scp backend/api/dashboard.py root@服务器IP:~/feishu-hr-translator/backend/api/
```

**2. 在服务器上重新构建并启动**

```bash
ssh root@服务器IP

cd ~/feishu-hr-translator/deploy

# 重新构建后端容器
docker-compose -f docker-compose.production.yml build --no-cache backend

# 重启容器
docker-compose -f docker-compose.production.yml up -d

# 查看日志
docker-compose -f docker-compose.production.yml logs -f backend
```

## ✅ 验证修复

1. 访问 Web UI：`http://服务器IP:8888`
2. 登录系统
3. 进入 "报告管理" 页面
4. 点击 "导出 CSV (全部)" 按钮
5. 应该能成功下载 CSV 文件，不再出现 422 错误

## 🔍 故障排查

### 问题：后端容器启动失败

**检查日志**：
```bash
docker-compose -f docker-compose.production.yml logs backend
```

**常见错误**：
- Python 语法错误：检查 `dashboard.py` 文件是否完整上传
- 端口占用：确保 8080 端口未被其他进程占用

### 问题：CSV 导出仍然报错

**1. 确认后端容器已重新构建**

```bash
# 检查容器镜像创建时间
docker images | grep backend
```

应该显示最新的创建时间。

**2. 确认路由顺序正确**

在服务器上检查文件：
```bash
grep -n "@router.get(\"/reports" ~/feishu-hr-translator/backend/api/dashboard.py
```

应该显示：
```
97:@router.get("/reports/export")
190:@router.get("/reports/{report_id}/export")
292:@router.get("/reports/{report_id}", response_model=ReportDetail)
376:@router.get("/reports")
```

**3. 清除浏览器缓存**

有时浏览器会缓存旧的 API 响应，清除缓存后重试。

## 📚 技术说明

### 修复的问题

FastAPI 路由按定义顺序匹配。原代码中：
- `/reports/{report_id}` 定义在前
- `/reports/export` 定义在后

导致请求 `/reports/export` 时，FastAPI 匹配到 `/reports/{report_id}`，将 "export" 作为 `report_id` 参数，因类型不匹配（期望 int，实际 str）返回 422 错误。

### 修复方案

调整路由定义顺序，将具体路由放在泛型路由之前：
1. `/reports/export` - 静态路径，最具体
2. `/reports/{report_id}/export` - 带参数的具体路径
3. `/reports/{report_id}` - 泛型路径参数
4. `/reports` - 基础路由

这样确保 FastAPI 优先匹配具体路径，避免被泛型路由误匹配。

---

**修复时间**: 2025-12-19
**相关文档**: [BUGFIX_EXPORT_CSV.md](BUGFIX_EXPORT_CSV.md)
