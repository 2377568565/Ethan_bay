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
# 驱动安装检查：显卡驱动更新后，检查新驱动是否装上、MX150 错误代码 43 是否消失、更新后有没有再出现黑屏/蓝屏/驱动崩溃
# 只读取信息；唯一的改动“停用 MX150 独显”只在它仍然出错时才会问你，不同意就不改。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '驱动安装检查' } catch {}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '需要管理员权限，请双击 bat 文件并在弹窗里点“是”。' -ForegroundColor Yellow
    exit 1
}

$report = New-Object System.Collections.Generic.List[string]
$verdict = New-Object System.Collections.Generic.List[string]
function Out-Line($text, $color) {
    if (-not $color) { $color = 'White' }
    Write-Host $text -ForegroundColor $color
    $report.Add($text)
}
function Out-Title($m) { Out-Line ''; Out-Line "==== $m ====" 'Cyan' }
function Out-Ok($m)    { Out-Line "  [正常] $m" 'Green' }
function Out-Bad($m)   { Out-Line "  [注意] $m" 'Yellow' }
function Out-Info($m)  { Out-Line "  $m" 'White' }
function Get-EvSafe { try { Get-WinEvent @args -ErrorAction Stop } catch { } }

# 更新前的旧驱动版本（来自之前的诊断报告）
$OldIntel = '25.20.100.6471'
$OldNvidia = '24.21.13.9835'

$os = Get-CimInstance Win32_OperatingSystem
Out-Line "驱动安装检查报告    生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm')    本次开机：$($os.LastBootUpTime)" 'Cyan'

# 以“更新显卡驱动之前”还原点的时间作为更新时间；找不到就看最近 1 天
$since = (Get-Date).AddDays(-1)
$sinceText = '最近 24 小时'
try {
    $rp = Get-ComputerRestorePoint -ErrorAction Stop | Where-Object { $_.Description -eq '更新显卡驱动之前' } | Select-Object -Last 1
    if ($rp) {
        $since = [Management.ManagementDateTimeConverter]::ToDateTime($rp.CreationTime)
        $sinceText = "驱动更新之后（$($since.ToString('yyyy-MM-dd HH:mm')) 起）"
    }
} catch {}

# ---------------------------------------------------------------------------
Out-Title '1. 还原点'
if ($rp) { Out-Ok "还原点“更新显卡驱动之前”存在（$($since.ToString('yyyy-MM-dd HH:mm'))），新驱动有问题时可以退回" }
else { Out-Bad '没找到“更新显卡驱动之前”的还原点' }

# ---------------------------------------------------------------------------
Out-Title '2. 显卡驱动版本'
$intelOk = $false; $nvOk = $false; $nv43 = $false
foreach ($d in @(Get-PnpDevice -Class Display -ErrorAction SilentlyContinue)) {
    $ver = ''; $date = ''; $prov = ''; $code = 0
    try { $ver = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverVersion -ErrorAction Stop).Data)" } catch {}
    try { $date = ([datetime](Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverDate -ErrorAction Stop).Data).ToString('yyyy-MM-dd') } catch {}
    try { $prov = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverProvider -ErrorAction Stop).Data)" } catch {}
    try { $code = [int](Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_ProblemCode -ErrorAction Stop).Data } catch {}
    Out-Info ("{0}" -f $d.FriendlyName)
    Out-Info ("   驱动 {0}（{1}，{2}）  状态 {3}  问题代码 {4}" -f $ver, $date, $prov, $d.Status, $code)

    if ($d.FriendlyName -match 'Intel') {
        if ($ver -and $ver -ne $OldIntel) {
            $intelOk = $true
            Out-Ok "Intel 核显驱动已更新：$OldIntel -> $ver"
        } else {
            Out-Bad 'Intel 核显驱动还是 2018 年的旧版本，没有更新成功'
        }
        if ($code -ne 0) { Out-Bad "Intel 核显有错误（代码 $code）" }
    }
    if ($d.FriendlyName -match 'NVIDIA') {
        if ($ver -and $ver -ne $OldNvidia) {
            $nvOk = $true
            Out-Ok "NVIDIA 驱动已更新：$OldNvidia -> $ver"
        } else {
            Out-Bad 'NVIDIA 驱动还是 2018 年的旧版本，没有更新成功'
        }
        if ($code -eq 43) { $nv43 = $true; Out-Bad 'MX150 仍然是错误代码 43' }
        elseif ($code -ne 0) { Out-Bad "MX150 有错误（代码 $code）" }
        else { Out-Ok 'MX150 的错误代码 43 已经消失，工作正常' }
    }
}

# 驱动装一半时 NVIDIA 卡可能跑到“其他设备”里（不在显示适配器分类），单独找一下
foreach ($x in @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_10DE' -and $_.Class -ne 'Display' })) {
    Out-Bad ("NVIDIA 显卡不在“显示适配器”里：{0}  分类 {1}  状态 {2}  —— 驱动没装好" -f $x.FriendlyName, $x.Class, $x.Status)
}

# 让 NVIDIA 显卡“说句话”：nvidia-smi 能读出显卡信息，说明显卡和驱动真的能用
$smi = Join-Path $env:WINDIR 'System32\nvidia-smi.exe'
if (Test-Path -LiteralPath $smi) {
    $q = & $smi --query-gpu=name,driver_version,temperature.gpu,pstate --format=csv,noheader 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -and $q.Trim()) { Out-Ok "nvidia-smi 能正常读取显卡：$($q.Trim())" }
    else { Out-Bad "nvidia-smi 读不到显卡：$($q.Trim())" }
}

$igcc = Get-AppxPackage -Name '*IntelGraphicsExperience*' -ErrorAction SilentlyContinue
if ($igcc) { Out-Ok '“英特尔显卡控制中心”已安装（可以在里面关闭“面板自刷新”）' }
else { Out-Info '“英特尔显卡控制中心”没有安装（可在微软应用商店搜索安装，用来关闭“面板自刷新”）' }

# ---------------------------------------------------------------------------
Out-Title '3. 驱动安装记录'
$pnp = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-UserPnp'; Id = 20001; StartTime = $since.AddMinutes(-5) })
$gpuInstalls = $pnp | Where-Object { $_.Message -match 'NVIDIA|Intel\(R\) (UHD|HD)|Display|显示' }
if (-not $gpuInstalls) { Out-Info '没找到显卡驱动安装记录' }
foreach ($e in ($gpuInstalls | Sort-Object TimeCreated)) {
    $msg = ($e.Message -replace '\s+', ' ').Trim()
    if ($msg.Length -gt 160) { $msg = $msg.Substring(0, 160) + '...' }
    Out-Info ("{0:MM-dd HH:mm}  {1}" -f $e.TimeCreated, $msg)
}

# ---------------------------------------------------------------------------
Out-Title "4. 稳定性：$sinceText"
$kp41 = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 41; StartTime = $since })
$tdr = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Display'; Id = 4101; StartTime = $since })
$nvErr = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'nvlddmkm'; StartTime = $since })
$whea = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-WHEA-Logger'; StartTime = $since })
$sleeps = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 42; StartTime = $since })
$resumes = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Power-Troubleshooter'; Id = 1; StartTime = $since })
$dumps = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $since })

if ($kp41.Count -eq 0) { Out-Ok '没有强制关机 / 意外断电' } else {
    Out-Bad "强制关机 / 意外断电 $($kp41.Count) 次"
    foreach ($e in $kp41) {
        $x = [xml]$e.ToXml()
        $bug = ($x.Event.EventData.Data | Where-Object { $_.Name -eq 'BugcheckCode' }).'#text'
        $note = '（不是蓝屏，是卡死后被强制关机）'
        if ($bug -and $bug -ne '0') { $note = ('（蓝屏 0x{0:X}）' -f [int64]$bug) }
        Out-Info ("   {0:MM-dd HH:mm} {1}" -f $e.TimeCreated, $note)
    }
}
if ($dumps.Count -eq 0) { Out-Ok '没有新的蓝屏' } else { Out-Bad "新的蓝屏 $($dumps.Count) 次" }
if ($tdr.Count -eq 0) { Out-Ok '没有“显卡驱动停止响应”' } else { Out-Bad "显卡驱动停止响应后恢复 $($tdr.Count) 次" }
if ($nvErr.Count -eq 0) { Out-Ok '没有 NVIDIA 驱动报错' } else { Out-Bad "NVIDIA 驱动报错 $($nvErr.Count) 次" }
if ($whea.Count -eq 0) { Out-Ok '没有硬件错误' } else { Out-Bad "硬件错误 $($whea.Count) 条" }
Out-Info "睡眠 $($sleeps.Count) 次，成功唤醒 $($resumes.Count) 次"

# ---------------------------------------------------------------------------
Out-Title '5. 其他设置'
$fast = $null
try { $fast = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled -ErrorAction Stop).HiberbootEnabled } catch {}
if ($fast -eq 0) { Out-Ok '快速启动已关闭' } else { Out-Bad '快速启动还开着（建议关闭：再运行黑屏诊断，问到时输入 y）' }
$md = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-MemoryDiagnostics-Results' })
if ($md.Count -gt 0) { Out-Info ("内存检测结果（{0:yyyy-MM-dd}）：{1}" -f $md[0].TimeCreated, (($md[0].Message -replace '\s+', ' ').Trim())) }
else { Out-Info '还没做过内存检测' }

# ---------------------------------------------------------------------------
Out-Title '结论'
if ($intelOk -and $nvOk -and -not $nv43) {
    Out-Ok '两个显卡驱动都更新成功，MX150 也恢复正常了'
} else {
    if (-not $intelOk) { Out-Bad 'Intel 核显驱动没更新成功 —— 把“显卡驱动一键更新”的窗口截图发给我' }
    if (-not $nvOk) { Out-Bad 'NVIDIA 驱动没更新成功 —— 把“显卡驱动一键更新”的窗口截图发给我' }
    if ($nvOk -and $nv43) { Out-Bad '驱动更新了但 MX150 还是错误代码 43 —— 更可能是 BIOS 或显卡硬件的问题，不影响笔记本屏幕显示（屏幕由 Intel 核显负责）' }
}
Out-Info '接下来正常用几天，再黑屏或蓝屏时，重新运行本检查，把报告发给我对比。'

# 上次蓝屏就是 NVIDIA 驱动（nvlddmkm.sys）引起的。驱动更新后 MX150 仍然出错时，可以直接停用它：
# 笔记本屏幕本来就由 Intel 核显负责显示，停用独显后 NVIDIA 驱动不再运行，也就不会再因它蓝屏。
$nvDev = Get-PnpDevice -Class Display -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'NVIDIA' } | Select-Object -First 1
if ($nvDev -and ($nv43 -or $nvErr.Count -gt 0 -or $dumps.Count -gt 0)) {
    Write-Host ''
    Write-Host '  MX150 仍然有问题。可以先把它停用：屏幕照常由 Intel 核显显示，日常使用、看视频都不受影响，' -ForegroundColor Cyan
    Write-Host '  只是玩大型游戏时没有独显加速；而 NVIDIA 驱动不再运行，就不会再因为它蓝屏/黑屏。' -ForegroundColor Cyan
    $ans = Read-Host '  现在停用 MX150 吗？输入 y 回车，直接回车跳过'
    if ($ans -match '^[yY]') {
        try {
            Disable-PnpDevice -InstanceId $nvDev.InstanceId -Confirm:$false -ErrorAction Stop
            Out-Ok '已停用 MX150（想恢复：右键开始按钮 -> 设备管理器 -> 显示适配器 -> 右键 NVIDIA GeForce MX150 -> 启用设备）'
        } catch {
            Out-Bad "停用失败：$($_.Exception.Message)"
        }
    }
}

$desktop = [Environment]::GetFolderPath('Desktop')
try {
    $report | Out-File -LiteralPath (Join-Path $desktop '驱动安装检查报告.txt') -Encoding UTF8
    Write-Host "`n报告已保存到桌面：驱动安装检查报告.txt（发给我核查）" -ForegroundColor Green
} catch {}
Write-Host ''
Read-Host '按回车关闭' | Out-Null
exit 0
