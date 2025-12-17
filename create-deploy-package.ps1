# PowerShell 脚本 - 创建部署包

Write-Host "====================================" -ForegroundColor Green
Write-Host "创建 Feishu HR Translator 部署包" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# 设置变量
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packageName = "feishu-hr-deploy-$timestamp.tar.gz"
$tempDir = ".\deploy-temp"

Write-Host "[1/5] 检查必要文件..." -ForegroundColor Yellow

# 检查关键目录
$requiredDirs = @("src", "frontend", "deploy", "data")
$missingDirs = @()

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $missingDirs += $dir
    }
}

if ($missingDirs.Count -gt 0) {
    Write-Host "错误：缺少以下目录：" -ForegroundColor Red
    $missingDirs | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "✓ 所有必要文件存在" -ForegroundColor Green
Write-Host ""

Write-Host "[2/5] 创建临时目录..." -ForegroundColor Yellow

# 清理旧的临时目录
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}

New-Item -ItemType Directory -Path $tempDir | Out-Null
Write-Host "✓ 临时目录已创建" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] 复制文件..." -ForegroundColor Yellow

# 复制目录
Copy-Item -Path "src" -Destination "$tempDir\src" -Recurse
Copy-Item -Path "frontend" -Destination "$tempDir\frontend" -Recurse
Copy-Item -Path "deploy" -Destination "$tempDir\deploy" -Recurse
Copy-Item -Path "data" -Destination "$tempDir\data" -Recurse

# 复制文件
Copy-Item -Path "requirements.txt" -Destination "$tempDir\"
Copy-Item -Path ".env.example" -Destination "$tempDir\"
Copy-Item -Path "README.md" -Destination "$tempDir\"

if (Test-Path ".dockerignore") {
    Copy-Item -Path ".dockerignore" -Destination "$tempDir\"
}

Write-Host "✓ 文件复制完成" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] 清理不需要的文件..." -ForegroundColor Yellow

# 删除不需要的文件和目录
$excludeDirs = @(
    "$tempDir\frontend\node_modules",
    "$tempDir\frontend\dist",
    "$tempDir\frontend\.vite",
    "$tempDir\src\__pycache__",
    "$tempDir\.pytest_cache"
)

foreach ($dir in $excludeDirs) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
        Write-Host "  已删除: $dir" -ForegroundColor Gray
    }
}

# 删除 Python 缓存文件
Get-ChildItem -Path $tempDir -Filter "*.pyc" -Recurse | Remove-Item -Force
Get-ChildItem -Path $tempDir -Filter "__pycache__" -Recurse | Remove-Item -Force -Recurse

Write-Host "✓ 清理完成" -ForegroundColor Green
Write-Host ""

Write-Host "[5/5] 创建压缩包..." -ForegroundColor Yellow

# 检查是否有 tar 命令（Git Bash）
$tarExists = Get-Command tar -ErrorAction SilentlyContinue

if ($tarExists) {
    # 使用 tar 命令
    tar -czf $packageName -C $tempDir .
    Write-Host "✓ 使用 tar 创建压缩包" -ForegroundColor Green
} else {
    # 使用 PowerShell 压缩（zip 格式）
    $zipName = "feishu-hr-deploy-$timestamp.zip"
    Compress-Archive -Path "$tempDir\*" -DestinationPath $zipName
    Write-Host "✓ 使用 Compress-Archive 创建 ZIP 包" -ForegroundColor Green
    Write-Host "  注意：创建的是 ZIP 格式，到服务器需要用 unzip 解压" -ForegroundColor Yellow
    $packageName = $zipName
}

Write-Host ""

# 清理临时目录
Remove-Item -Recurse -Force $tempDir

# 显示结果
$packageSize = (Get-Item $packageName).Length / 1MB
Write-Host "====================================" -ForegroundColor Green
Write-Host "部署包创建成功！" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "文件名: $packageName" -ForegroundColor Cyan
Write-Host "大小: $([math]::Round($packageSize, 2)) MB" -ForegroundColor Cyan
Write-Host "位置: $(Resolve-Path $packageName)" -ForegroundColor Cyan
Write-Host ""

Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 上传到服务器：" -ForegroundColor White
Write-Host "   scp $packageName root@your-server-ip:/tmp/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. SSH 登录服务器：" -ForegroundColor White
Write-Host "   ssh root@your-server-ip" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 解压文件：" -ForegroundColor White
if ($packageName -like "*.tar.gz") {
    Write-Host "   cd /root/feishu-hr-translator" -ForegroundColor Gray
    Write-Host "   tar -xzf /tmp/$packageName" -ForegroundColor Gray
} else {
    Write-Host "   cd /root/feishu-hr-translator" -ForegroundColor Gray
    Write-Host "   unzip /tmp/$packageName" -ForegroundColor Gray
}
Write-Host ""
Write-Host "4. 执行部署：" -ForegroundColor White
Write-Host "   cd deploy" -ForegroundColor Gray
Write-Host "   chmod +x *.sh" -ForegroundColor Gray
Write-Host "   ./deploy.sh" -ForegroundColor Gray
Write-Host ""
