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
# 打开独显：启用 NVIDIA MX150，并检查它能不能正常工作；还是故障的话，可以马上再关掉
try { $Host.UI.RawUI.WindowTitle = '打开独显' } catch {}

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

if ($code -ne 22) {
    Write-Ok '独显已经是启用状态，不需要再打开。'
    if ($code -eq 43) { Write-Bad '不过它现在报故障（代码 43），没法真正使用。' }
    Read-Host '按回车关闭' | Out-Null
    exit 0
}

Write-Bad '提醒：这块 MX150 之前诊断为硬件故障（代码 43），启用后它的驱动曾经引起过蓝屏。'
Write-Info '   启用后如果出现蓝屏，开机后运行「关闭独显.bat」即可。'
$ans = Read-Host '  确定要打开独显吗？输入 y 回车，直接回车取消'
if ($ans -notmatch '^[yY]') { Write-Info '已取消，什么都没改。'; Read-Host '按回车关闭' | Out-Null; exit 0 }

try {
    Enable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false -ErrorAction Stop
} catch {
    Write-Bad "启用失败：$($_.Exception.Message)"
    Read-Host '按回车关闭' | Out-Null
    exit 0
}
Write-Info '已发出启用命令，等待显卡初始化（约 10 秒，屏幕可能闪一下）...'
Start-Sleep -Seconds 10

$code = Get-Code (Get-Gpu)
Write-Info "现在：$(Get-StateText $code)"
if ($code -eq 0) {
    Write-Ok '独显已打开，工作正常！'
    $smi = Join-Path $env:WINDIR 'System32\nvidia-smi.exe'
    if (Test-Path -LiteralPath $smi) {
        $q = & $smi --query-gpu=name,driver_version,temperature.gpu --format=csv,noheader 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) { Write-Ok "显卡实测：$($q.Trim())" }
    }
    Write-Info '用一段时间看看稳不稳定；出现蓝屏就运行「关闭独显.bat」。'
} else {
    Write-Bad '独显已启用，但还是报故障，没法正常使用。'
    $ans = Read-Host '  要马上把它关掉吗？输入 y 回车（推荐），直接回车保持启用'
    if ($ans -match '^[yY]') {
        try {
            Disable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Ok '已关闭独显。'
        } catch { Write-Bad "关闭失败：$($_.Exception.Message)" }
    }
}
Read-Host '按回车关闭' | Out-Null
exit 0
