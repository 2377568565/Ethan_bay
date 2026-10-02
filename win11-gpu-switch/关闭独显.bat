<# : hybrid file - batch part below, PowerShell part after the comment end
@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
set "PCFOCUS_SELF=%~f0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([IO.File]::ReadAllText($env:PCFOCUS_SELF, [Text.Encoding]::UTF8))"
if errorlevel 1 pause
exit /b
#>
# 关闭独显：停用 NVIDIA MX150。屏幕由 Intel 核显照常显示，日常使用不受影响
try { $Host.UI.RawUI.WindowTitle = '关闭独显' } catch {}

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

function Write-Ok($m)   { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)  { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m) { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限，请双击 bat 文件并在弹窗里点「是」。'
    exit 1
}

# VEN_10DE = NVIDIA。按硬件 ID 找，驱动坏了、名字变成「Display」也找得到
function Get-Gpu { Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_10DE' } | Select-Object -First 1 }
function Get-Code($d) {
    try { return [int](Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_ProblemCode -ErrorAction Stop).Data } catch { return -1 }
}
function Get-StateText($code) {
    switch ($code) {
        0       { return '已启用，工作正常（代码 0）' }
        22      { return '已停用（代码 22）' }
        43      { return '已启用，但显卡报告故障（代码 43）' }
        default { return "代码 $code" }
    }
}

$gpu = Get-Gpu
if (-not $gpu) {
    Write-Bad '没找到 NVIDIA 显卡。'
    Read-Host '按回车关闭' | Out-Null
    exit 0
}
$name = $gpu.FriendlyName
if (-not $name) { $name = 'NVIDIA 显卡' }
$code = Get-Code $gpu
Write-Host ''
Write-Info "显卡：$name"
Write-Info "现在：$(Get-StateText $code)"
Write-Host ''

if ($code -eq 22) {
    Write-Ok '独显已经是关闭状态，不需要再关。'
    Read-Host '按回车关闭' | Out-Null
    exit 0
}

Write-Info '关闭后：屏幕由 Intel 核显照常显示，上网/办公/看视频不受影响，只是没有独显加速。'
Write-Info '想重新打开：运行「打开独显.bat」。'
try {
    Disable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false -ErrorAction Stop
} catch {
    Write-Bad "关闭失败：$($_.Exception.Message)"
    Write-Info '   也可以手动：右键开始按钮 -> 设备管理器 -> 显示适配器 -> 右键 NVIDIA -> 禁用设备'
    Read-Host '按回车关闭' | Out-Null
    exit 0
}
Start-Sleep -Seconds 3
$code = Get-Code (Get-Gpu)
Write-Info "现在：$(Get-StateText $code)"
if ($code -eq 22) { Write-Ok '独显已关闭。' } else { Write-Bad '状态没有变成「已停用」，重启一次电脑后再运行本程序看看。' }
Read-Host '按回车关闭' | Out-Null
exit 0
