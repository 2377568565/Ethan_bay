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
# 停用独显并分析蓝屏：
#   1. 停用 NVIDIA MX150（先问你）。笔记本屏幕由 Intel 核显显示，停用后照常使用，NVIDIA 驱动不再运行就不会再因它蓝屏
#   2. 用 WinDbg 分析最近 3 次蓝屏，确认肇事驱动
# 想恢复独显：设备管理器 -> 显示适配器（或「其他设备」）-> 右键 NVIDIA / 视频控制器 -> 启用设备

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '停用独显并分析蓝屏' } catch {}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '需要管理员权限，请双击 bat 文件并在弹窗里点「是」。' -ForegroundColor Yellow
    exit 1
}

$report = New-Object System.Collections.Generic.List[string]
function Out-Line($text, $color) {
    if (-not $color) { $color = 'White' }
    Write-Host $text -ForegroundColor $color
    $report.Add($text)
}
function Out-Title($m) { Out-Line ''; Out-Line "==== $m ====" 'Cyan' }
function Out-Ok($m)    { Out-Line "  [OK] $m" 'Green' }
function Out-Bad($m)   { Out-Line "  [!]  $m" 'Yellow' }
function Out-Info($m)  { Out-Line "  $m" 'White' }

Out-Line "停用独显并分析蓝屏    $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 'Cyan'

# ---------------------------------------------------------------------------
Out-Title '1. 找到 NVIDIA 独显（不管它现在在哪个分类、有没有驱动）'
# VEN_10DE = NVIDIA；驱动装一半时它可能不在「显示适配器」里，而在「其他设备」里叫「视频控制器 / 3D 视频控制器」
$nv = @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_10DE' })
if ($nv.Count -eq 0) {
    Out-Bad '没找到 NVIDIA 设备（可能已经被停用或 BIOS 里关掉了）'
} else {
    foreach ($d in $nv) {
        $name = $d.FriendlyName
        if (-not $name) { $name = '(无名称，驱动没装好)' }
        Out-Info ("{0}  分类 {1}  状态 {2}  问题代码 {3}" -f $name, $d.Class, $d.Status, $d.ConfigManagerErrorCode)
    }
    Write-Host ''
    Write-Host '  建议现在停用 MX150：屏幕由 Intel 核显显示，上网、看视频、办公都不受影响，' -ForegroundColor Cyan
    Write-Host '  只是大型游戏没有独显加速；NVIDIA 驱动不再运行，就不会再因为它蓝屏。随时可以重新启用。' -ForegroundColor Cyan
    $ans = Read-Host '  现在停用吗？输入 y 回车（推荐），直接回车跳过'
    if ($ans -match '^[yY]') {
        foreach ($d in $nv) {
            try {
                Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop
                Out-Ok "已停用：$($d.FriendlyName) $($d.InstanceId)"
            } catch {
                Out-Bad "停用失败：$($_.Exception.Message)"
            }
        }
    } else {
        Out-Info '没有停用'
    }
}

# ---------------------------------------------------------------------------
Out-Title '2. 分析最近 3 次蓝屏'
function Find-Cdb {
    foreach ($p in @("${env:ProgramFiles(x86)}\Windows Kits\10\Debuggers\x64\cdb.exe", "$env:ProgramFiles\Windows Kits\10\Debuggers\x64\cdb.exe")) {
        if (Test-Path -LiteralPath $p) { return $p }
    }
    $pkg = Get-AppxPackage -Name 'Microsoft.WinDbg*' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pkg) {
        $c = Get-ChildItem -LiteralPath $pkg.InstallLocation -Recurse -Filter cdb.exe -ErrorAction SilentlyContinue |
            Sort-Object { $_.FullName -notmatch 'amd64|x64' } | Select-Object -First 1
        if ($c) { return $c.FullName }
    }
    return $null
}
$dumps = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3)
$cdb = Find-Cdb
$culprits = @()
if ($dumps.Count -eq 0) {
    Out-Info '没有蓝屏转储文件'
} elseif (-not $cdb) {
    Out-Bad '没找到 WinDbg（先运行一次「黑屏深度诊断.bat」并在问到时输入 y 安装）'
} else {
    $symDir = Join-Path $env:SystemDrive 'symbols'
    $desktop = [Environment]::GetFolderPath('Desktop')
    $i = 0
    foreach ($d in $dumps) {
        $i++
        Write-Host ("  正在分析 {0}（{1:MM-dd HH:mm}），约半分钟..." -f $d.Name, $d.LastWriteTime) -ForegroundColor DarkGray
        $raw = & $cdb -z $d.FullName -y "srv*$symDir*https://msdl.microsoft.com/download/symbols" -c '!analyze -v; q' 2>&1 | Out-String
        $raw | Out-File -LiteralPath (Join-Path $desktop "蓝屏分析详情_$i.txt") -Encoding UTF8
        $get = { param($k) $m = [regex]::Match($raw, "(?m)^$k\s*:\s*(.+)$"); if ($m.Success) { $m.Groups[1].Value.Trim() } else { '?' } }
        $img = & $get 'IMAGE_NAME'
        $culprits += $img
        Out-Info ("{0:MM-dd HH:mm}  错误码 {1}  肇事模块 {2}  进程 {3}  {4}" -f $d.LastWriteTime, (& $get 'BUGCHECK_CODE'), $img, (& $get 'PROCESS_NAME'), (& $get 'FAILURE_BUCKET_ID'))
    }
}

# ---------------------------------------------------------------------------
Out-Title '结论'
$nvCount = @($culprits | Where-Object { $_ -match '(?i)^nvlddmkm' }).Count
$memCount = @($culprits | Where-Object { $_ -match '(?i)memory_corruption|hardware' }).Count
$tcCount = @($culprits | Where-Object { $_ -match '(?i)^(TS|TAO|QQ|TFs|QMU|tchard)' }).Count
if ($nvCount -gt 0) {
    Out-Bad "$nvCount 次蓝屏是 NVIDIA 驱动（nvlddmkm.sys）造成的 —— 停用 MX150 就能解决"
}
if ($memCount -gt 0) {
    Out-Bad "$memCount 次蓝屏指向内存损坏 —— 需要做内存检测，或换回原来的 8G 内存条试试"
}
if ($tcCount -gt 0) {
    Out-Bad "$tcCount 次蓝屏是腾讯电脑管家的驱动造成的 —— 卸载腾讯电脑管家"
}
$other = @($culprits | Where-Object { $_ -and $_ -ne '?' -and $_ -notmatch '(?i)^nvlddmkm|memory_corruption|hardware|^(TS|TAO|QQ|TFs|QMU|tchard)' })
foreach ($o in ($other | Sort-Object -Unique)) { Out-Bad "肇事模块 $o —— 把报告发给我" }
Out-Info '停用独显后正常使用，如果还蓝屏，再运行一次本程序把报告发给我。'

$desktop = [Environment]::GetFolderPath('Desktop')
try {
    $report | Out-File -LiteralPath (Join-Path $desktop '停用独显并分析蓝屏报告.txt') -Encoding UTF8
    Write-Host "`n报告已保存到桌面：停用独显并分析蓝屏报告.txt（发给我）" -ForegroundColor Green
} catch {}
Write-Host ''
Read-Host '按回车关闭' | Out-Null
exit 0
