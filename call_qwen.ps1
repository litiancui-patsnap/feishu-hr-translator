if ([string]::IsNullOrWhiteSpace($env:DASHSCOPE_API_KEY)) {
    Write-Error "请先在环境变量中配置 DASHSCOPE_API_KEY"
    exit 1
}

$bodyObject = @{
    model    = "qwen-plus"
    messages = @(
        @{ role = "system"; content = "You are a helpful assistant." }
        @{ role = "user"; content = "你是谁？" }
    )
}

$bodyJson = $bodyObject | ConvertTo-Json -Depth 5 -Compress
$tempFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tempFile, $bodyJson, [System.Text.Encoding]::UTF8)

try {
    curl.exe -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" `
      -H "Authorization: Bearer $env:DASHSCOPE_API_KEY" `
      -H "Content-Type: application/json" `
      --data-binary "@$tempFile"
}
finally {
    Remove-Item $tempFile -ErrorAction SilentlyContinue
}
