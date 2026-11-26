# 一键重签 StudyHub 的未签名 IPA
#
# 用法（证书与描述文件自己放好）：
#   .\tools\resign.ps1 -Ipa .\StudyHub-unsigned.ipa `
#       -P12 C:\path\cert.p12 -P12Password 你的密码 `
#       -Provision C:\path\dev.mobileprovision
#
# 输出：签名后的 ipa，默认放在 ipa 同目录、文件名后缀 -signed
#
# 逻辑：
#   1. 找 zsign（PATH 或 tools\zsign.exe；没有就尝试从 GitHub 下载）
#   2. zsign 会自动处理里面的 .appex（Widget），并沿用 App 里的 entitlements
#   3. 检查产物里有没有 mobileprovision

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Ipa,
    [Parameter(Mandatory = $true)][string]$P12,
    [Parameter(Mandatory = $true)][string]$Provision,
    [string]$P12Password = "",
    [string]$OutDir = "",
    [string]$Zsign = "",
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Fail($msg) { Write-Host "[x] $msg" -ForegroundColor Red; exit 1 }

if (-not (Test-Path $Ipa)) { Fail "找不到 IPA：$Ipa" }
if (-not (Test-Path $P12)) { Fail "找不到 p12：$P12" }
if (-not (Test-Path $Provision)) { Fail "找不到描述文件：$Provision" }

# ---- 找 zsign ----
if (-not $Zsign) {
    $cand = @(
        (Join-Path $PSScriptRoot 'zsign.exe'),
        (Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\zsign.exe')
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($cand) {
        $Zsign = $cand
    } else {
        $cmd = Get-Command zsign.exe -ErrorAction SilentlyContinue
        if ($cmd) { $Zsign = $cmd.Source }
    }
}

if (-not $Zsign) {
    Write-Host "[i] 没找到 zsign.exe，尝试下载 Windows 版…" -ForegroundColor Yellow
    $rel = 'https://github.com/zhlynn/zsign/releases/latest/download/zsign_win.zip'
    $zip = Join-Path $env:TEMP 'zsign_win.zip'
    try {
        Invoke-WebRequest -Uri $rel -OutFile $zip -UseBasicParsing -TimeoutSec 60
        $dest = Join-Path $PSScriptRoot 'zsign'
        Expand-Archive -Path $zip -DestinationPath $dest -Force
        $Zsign = Get-ChildItem $dest -Recurse -Filter 'zsign*.exe' | Select-Object -First 1 -ExpandProperty FullName
    } catch {
        Fail "下载 zsign 失败（$($_.Exception.Message)）。手动放一个 zsign.exe 到 tools\ 再跑一次。"
    }
}

Write-Host "[i] zsign: $Zsign"
Write-Host "[i] IPA   : $Ipa"

# ---- 输出路径 ----
if (-not $OutDir) { $OutDir = Split-Path $Ipa -Parent }
$base = [IO.Path]::GetFileNameWithoutExtension($Ipa) -replace '-unsigned$', ''
$out = Join-Path $OutDir ("$base-signed.ipa")
if ((Test-Path $out) -and -not $Force) { Fail "输出已存在：$out（加 -Force 覆盖）" }

# ---- 重签 ----
$args = @('-k', $P12, '-m', $Provision, '-o', $out, '-z', '9', $Ipa)
if ($P12Password) { $args = @('-k', $P12, '-p', $P12Password, '-m', $Provision, '-o', $out, '-z', '9', $Ipa) }

Write-Host "[i] 开始签名…"
& $Zsign @args
$code = $LASTEXITCODE
if ($code -ne 0 -or -not (Test-Path $out)) { Fail "zsign 失败（exit $code）" }

# ---- 检查产物 ----
$size = (Get-Item $out).Length
Write-Host ("[✓] 已生成 {0}（{1:N0} 字节）" -f $out, $size) -ForegroundColor Green

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::OpenRead($out)
try {
    $prov = $zip.Entries | Where-Object { $_.FullName -like '*.app/embedded.mobileprovision' }
    $appex = $zip.Entries | Where-Object { $_.FullName -like '*.appex/*' } |
             ForEach-Object { ($_.FullName -split '/')[2] } | Sort-Object -Unique
    if ($prov) { Write-Host "[✓] 已嵌入描述文件" } else { Write-Host "[!] 没看到 embedded.mobileprovision" -ForegroundColor Yellow }
    if ($appex) { Write-Host ("[i] 内含扩展：{0}" -f ($appex -join ', ')) } else { Write-Host "[i] 没有扩展（Widget 不会装）" -ForegroundColor Yellow }
} finally { $zip.Dispose() }

Write-Host ""
Write-Host "下一步：用 AltStore / SideStore / Sideloadly 把这个 -signed.ipa 装到手机。" -ForegroundColor Cyan
Write-Host "如果 Widget 不显示，多半是自签工具没保留 App Group（entitlements 被裁剪），不是包的问题。" -ForegroundColor DarkGray
