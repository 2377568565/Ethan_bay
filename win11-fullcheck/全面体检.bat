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
# 全面体检：软件 + 硬件，重点找蓝屏的真正原因
# 只读取信息；最后的「系统文件修复」「内存检测」都会先问你。
# 每写一行就立刻存到桌面的报告里——就算中途蓝屏，已经查完的部分也不会丢。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '全面体检' } catch {}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '需要管理员权限，请双击 bat 文件并在弹窗里点「是」。' -ForegroundColor Yellow
    exit 1
}

$desktop = [Environment]::GetFolderPath('Desktop')
$ReportPath = Join-Path $desktop '全面体检报告.txt'
Set-Content -LiteralPath $ReportPath -Value '' -Encoding UTF8
$findings = New-Object System.Collections.Generic.List[string]

function Out-Line($text, $color) {
    if (-not $color) { $color = 'White' }
    Write-Host $text -ForegroundColor $color
    Add-Content -LiteralPath $ReportPath -Value $text -Encoding UTF8
}
function Out-Title($m) { Out-Line ''; Out-Line "==== $m ====" 'Cyan' }
function Out-Ok($m)    { Out-Line "  [正常] $m" 'Green' }
function Out-Bad($m)   { Out-Line "  [注意] $m" 'Yellow' }
function Out-Info($m)  { Out-Line "  $m" 'White' }
function Get-EvSafe { try { Get-WinEvent @args -ErrorAction Stop } catch { } }
function Get-Field($e, $name) {
    try { $d = ([xml]$e.ToXml()).Event.EventData.Data | Where-Object { $_.Name -eq $name }; if ($d) { return "$($d.'#text')" } } catch {}
    return ''
}

$os = Get-CimInstance Win32_OperatingSystem
$boot = $os.LastBootUpTime
$since3 = (Get-Date).AddDays(-3)
Out-Line "全面体检报告    生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm')    本次开机：$($boot.ToString('yyyy-MM-dd HH:mm'))" 'Cyan'

# ---------------------------------------------------------------------------
Out-Title '1. 基本信息'
$cs = Get-CimInstance Win32_ComputerSystem
$bios = Get-CimInstance Win32_BIOS
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Out-Info "型号：$($cs.Manufacturer) $($cs.Model)    CPU：$($cpu.Name.Trim())"
Out-Info "系统：$($os.Caption) $($os.Version)    安装于 $($os.InstallDate.ToString('yyyy-MM-dd'))"
Out-Info "BIOS：$($bios.SMBIOSBIOSVersion)  $($bios.ReleaseDate.ToString('yyyy-MM-dd'))"
$rst = @(Get-EvSafe -FilterHashtable @{ LogName = 'Application'; ProviderName = 'Microsoft-Windows-RestoreOptimizer', 'System Restore'; StartTime = $since3 } -MaxEvents 3)
try {
    $rp = Get-ComputerRestorePoint -ErrorAction Stop | Select-Object -Last 4
    foreach ($r in $rp) { Out-Info ("还原点：{0:yyyy-MM-dd HH:mm}  {1}" -f [Management.ManagementDateTimeConverter]::ToDateTime($r.CreationTime), $r.Description) }
} catch {}

# ---------------------------------------------------------------------------
Out-Title '2. 显卡现状（确认系统还原后的状态）'
foreach ($d in @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.Class -eq 'Display' -or $_.InstanceId -match '^PCI\\VEN_10DE' })) {
    $ver = ''
    try { $ver = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverVersion -ErrorAction Stop).Data)" } catch {}
    $state = $d.Status
    if ($d.ConfigManagerErrorCode -eq 22) { $state = '已停用' }
    Out-Info ("{0}  分类 {1}  状态 {2}  问题代码 {3}  驱动 {4}" -f $d.FriendlyName, $d.Class, $state, $d.ConfigManagerErrorCode, $ver)
}

# ---------------------------------------------------------------------------
Out-Title '3. 蓝屏 / 死机记录（最近 3 天）'
$kp41 = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 41; StartTime = $since3 })
$afterBoot = 0
foreach ($e in ($kp41 | Sort-Object TimeCreated)) {
    $bug = Get-Field $e 'BugcheckCode'
    $kind = '死机（没有蓝屏，被强制关机）'
    if ($bug -and $bug -ne '0') { $kind = ('蓝屏 0x{0:X}' -f [int64]$bug) }
    Out-Info ("{0:MM-dd HH:mm}  {1}" -f $e.TimeCreated, $kind)
}
Out-Info "合计 $($kp41.Count) 次"
$crashSinceBoot = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $boot.AddMinutes(1) })
if ($kp41.Count -gt 0) { $findings.Add("最近 3 天有 $($kp41.Count) 次蓝屏/死机") }

# ---------------------------------------------------------------------------
Out-Title '4. 逐个分析蓝屏文件，找出「肇事者」'
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
$dumps = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $since3 } | Sort-Object LastWriteTime -Descending | Select-Object -First 8)
$culprits = @()
$cdb = Find-Cdb
if ($dumps.Count -eq 0) {
    Out-Info '没有蓝屏文件'
} elseif (-not $cdb) {
    Out-Bad '没装 WinDbg，无法分析（运行「黑屏深度诊断.bat」问到时输入 y 安装）'
} else {
    $symDir = Join-Path $env:SystemDrive 'symbols'
    foreach ($d in $dumps) {
        Write-Host ("  正在分析 {0:MM-dd HH:mm} 的蓝屏（约半分钟）..." -f $d.LastWriteTime) -ForegroundColor DarkGray
        $raw = & $cdb -z $d.FullName -y "srv*$symDir*https://msdl.microsoft.com/download/symbols" -c '!analyze -v; q' 2>&1 | Out-String
        $g = { param($k) $m = [regex]::Match($raw, "(?m)^$k\s*:\s*(.+)$"); if ($m.Success) { $m.Groups[1].Value.Trim() } else { '?' } }
        $img = & $g 'IMAGE_NAME'
        $culprits += $img
        Out-Info ("{0:MM-dd HH:mm}  错误 {1}  肇事模块 {2,-22} 进程 {3}" -f $d.LastWriteTime, (& $g 'BUGCHECK_CODE'), $img, (& $g 'PROCESS_NAME'))
    }
    Out-Info ''
    Out-Info '肇事模块统计：'
    foreach ($grp in ($culprits | Group-Object | Sort-Object Count -Descending)) { Out-Info ("   {0,-24} {1} 次" -f $grp.Name, $grp.Count) }
}

# ---------------------------------------------------------------------------
Out-Title '5. 内存条'
foreach ($m in @(Get-CimInstance Win32_PhysicalMemory)) {
    Out-Info ("{0} {1}  {2} GB  {3} MHz" -f "$($m.Manufacturer)".Trim(), "$($m.PartNumber)".Trim(), [math]::Round($m.Capacity / 1GB), $m.ConfiguredClockSpeed)
}
$md = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-MemoryDiagnostics-Results' })
if ($md.Count -gt 0) { foreach ($e in $md | Select-Object -First 2) { Out-Info ("内存检测 {0:MM-dd HH:mm}：{1}" -f $e.TimeCreated, (($e.Message -replace '\s+', ' ').Trim())) } }
else { Out-Bad '还没做过内存检测' }
$whea = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-WHEA-Logger'; StartTime = $since3 })
if ($whea.Count -gt 0) { Out-Bad "硬件错误（WHEA）$($whea.Count) 条"; $findings.Add('有硬件错误（WHEA）记录') } else { Out-Ok '没有硬件错误（WHEA）记录' }

# ---------------------------------------------------------------------------
Out-Title '6. 硬盘'
try {
    foreach ($pd in Get-PhysicalDisk) {
        $rc = $pd | Get-StorageReliabilityCounter -ErrorAction SilentlyContinue
        $type = "$($pd.MediaType)"
        Out-Info ("{0}  {1} GB  {2}  健康 {3}" -f $pd.FriendlyName, [math]::Round($pd.Size / 1GB), $type, $pd.HealthStatus)
        if ($rc) { Out-Info ("   温度 {0}°C  磨损 {1}%  读取错误 {2}  通电 {3} 小时" -f $rc.Temperature, $rc.Wear, $rc.ReadErrorsUncorrected, $rc.PowerOnHours) }
        if ("$($pd.HealthStatus)" -ne 'Healthy') { $findings.Add("硬盘 $($pd.FriendlyName) 健康状态异常，尽快备份") }
    }
} catch {}
$c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
Out-Info ("C 盘剩余 {0} GB / {1} GB" -f [math]::Round($c.FreeSpace / 1GB, 1), [math]::Round($c.Size / 1GB))
$diskErr = @()
$diskErr += Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'disk'; Id = 7, 11, 51, 153; StartTime = $since3 }
$diskErr += Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Ntfs'; Id = 55, 98; StartTime = $since3 }
$diskErr += Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'stornvme', 'storahci'; StartTime = $since3; Level = 1, 2, 3 }
$diskErr = @($diskErr | Where-Object { $_ })
if ($diskErr.Count -gt 0) { Out-Bad "硬盘读写错误/超时 $($diskErr.Count) 条"; $findings.Add('硬盘有读写错误记录') } else { Out-Ok '没有硬盘错误记录' }

# ---------------------------------------------------------------------------
Out-Title '7. 系统文件完整性（快速检查）'
$dism = (dism.exe /Online /Cleanup-Image /CheckHealth 2>&1 | Out-String)
$dismLast = ($dism -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 2) -join ' / '
Out-Info "DISM：$dismLast"
$sysCorrupt = ($dism -match '(?i)repairable|可以修复|损坏|corrupt')
if ($sysCorrupt) { Out-Bad '系统映像有损坏'; $findings.Add('系统文件有损坏（下面可以一键修复）') }

# ---------------------------------------------------------------------------
Out-Title '8. 第三方内核驱动'
$third = @()
foreach ($drv in @(Get-CimInstance Win32_SystemDriver | Where-Object { $_.State -eq 'Running' })) {
    $path = "$($drv.PathName)" -replace '^\\\?\?\\', '' -replace '^\\SystemRoot', $env:WINDIR
    if ($path -match '^(?i)system32\\') { $path = Join-Path $env:WINDIR $path }
    if (-not (Test-Path -LiteralPath $path)) { continue }
    $signer = ''
    try { $signer = "$((Get-AuthenticodeSignature -LiteralPath $path).SignerCertificate.Subject)" } catch {}
    if ($signer -match 'O=Microsoft Corporation') { continue }
    $org = ''
    if ($signer -match 'O="?([^,"]+)') { $org = $Matches[1] }
    $third += [pscustomobject]@{ Name = $drv.Name; Org = $org }
}
foreach ($t in ($third | Sort-Object Org, Name)) { Out-Info ("{0,-22} {1}" -f $t.Name, $t.Org) }
$tencent = @($third | Where-Object { $_.Org -match 'Tencent' })
if ($tencent.Count -gt 0) { Out-Bad "腾讯电脑管家的 $($tencent.Count) 个内核驱动还在运行"; $findings.Add('卸载腾讯电脑管家（它有内核驱动，是蓝屏常见来源）') }

# ---------------------------------------------------------------------------
Out-Title '9. 有问题的设备'
$bad = @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Error' })
if ($bad.Count -eq 0) { Out-Ok '没有出错的设备' }
foreach ($d in $bad) {
    $s = "错误代码 $($d.ConfigManagerErrorCode)"
    if ($d.ConfigManagerErrorCode -eq 22) { $s = '已停用' }
    Out-Info ("{0}  ({1})  {2}" -f $d.FriendlyName, $d.Class, $s)
}

# ---------------------------------------------------------------------------
Out-Title '10. 温度和降频'
$thr = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Processor-Power'; Id = 37; StartTime = $since3 })
if ($thr.Count -gt 0) { Out-Bad "最近 3 天 BIOS 强制给 CPU 降速 $($thr.Count) 次（通常是过热或供电不足）"; $findings.Add('CPU 经常被 BIOS 强制降速：散热需要清灰换硅脂') }
else { Out-Ok '没有被 BIOS 强制降速的记录' }
try {
    $tz = Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop
    foreach ($t in $tz) { Out-Info ("主板温度传感器：{0} °C" -f [math]::Round($t.CurrentTemperature / 10 - 273.15)) }
} catch {}

# ---------------------------------------------------------------------------
Out-Title '11. 电池'
try {
    $full = (Get-CimInstance -Namespace root/wmi -ClassName BatteryFullChargedCapacity -ErrorAction Stop | Select-Object -First 1).FullChargedCapacity
    $design = (Get-CimInstance -Namespace root/wmi -ClassName BatteryStaticData -ErrorAction Stop | Select-Object -First 1).DesignedCapacity
    if ($full -and $design) {
        $pct = [math]::Round($full / $design * 100)
        Out-Info ("电池健康度：{0}%（设计 {1} mWh，现在充满 {2} mWh）" -f $pct, $design, $full)
        if ($pct -lt 60) { Out-Bad '电池老化明显，续航会短很多' }
    }
} catch { Out-Info '读不到电池信息' }

# ---------------------------------------------------------------------------
Out-Title '12. 设置'
$fast = $null
try { $fast = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled -ErrorAction Stop).HiberbootEnabled } catch {}
if ($fast -eq 0) { Out-Ok '快速启动已关闭' } else { Out-Bad '快速启动开着' }

# ---------------------------------------------------------------------------
Out-Title '结论'
$nv = @($culprits | Where-Object { $_ -match '(?i)^nvlddmkm' }).Count
$ig = @($culprits | Where-Object { $_ -match '(?i)^igdkmd' }).Count
$mem = @($culprits | Where-Object { $_ -match '(?i)memory_corruption|hardware|ntkrnlmp|ntoskrnl' }).Count
$tc = @($culprits | Where-Object { $_ -match '(?i)^(TS|TAO|QQ|TFs|QMU|tchard)' }).Count
$distinct = @($culprits | Where-Object { $_ -ne '?' } | Sort-Object -Unique).Count
if ($culprits.Count -gt 0) {
    if ($nv -gt 0)  { $findings.Add("$nv 次蓝屏是 NVIDIA 驱动 —— 保持停用 MX150") }
    if ($ig -gt 0)  { $findings.Add("$ig 次蓝屏是 Intel 核显驱动 —— 保持还原后的旧版本，不要再更新") }
    if ($tc -gt 0)  { $findings.Add("$tc 次蓝屏是腾讯电脑管家的驱动 —— 卸载它") }
    if ($mem -gt 0 -or $distinct -ge 3) {
        $findings.Add('蓝屏指向内存损坏 / 系统内核，或者每次肇事模块都不一样 —— 这是内存条有问题的典型特征。做内存检测（下面可一键启动），或换回原来的 8G 内存条试几天')
    }
}
if ($crashSinceBoot.Count -eq 0) { $findings.Add('本次开机（系统还原之后）到现在还没有蓝屏 —— 继续观察') }
$i = 0
foreach ($f in $findings) { $i++; Out-Line "  $i. $f" 'Yellow' }

Write-Host "`n报告已保存到桌面：全面体检报告.txt（发给我）" -ForegroundColor Green

# ---------------------------------------------------------------------------
Write-Host "`n==== 可选（每一项都会先问你） ====" -ForegroundColor Cyan
$ans = Read-Host '  运行系统文件修复（sfc /scannow，约 10~20 分钟，会修复被损坏的系统文件）？输入 y 回车，直接回车跳过'
if ($ans -match '^[yY]') {
    sfc.exe /scannow
    Add-Content -LiteralPath $ReportPath -Value "`n系统文件修复已运行，返回码 $LASTEXITCODE" -Encoding UTF8
}
$ans = Read-Host '  运行 Windows 内存检测（会弹窗让你选「立即重启并检查」，约 15~30 分钟）？输入 y 回车，直接回车跳过'
if ($ans -match '^[yY]') { Start-Process mdsched.exe }

Read-Host '按回车关闭' | Out-Null
exit 0
