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
# 黑屏深度诊断：分析蓝屏转储找出“肇事”驱动、显卡错误详情、第三方驱动、崩溃前后的系统事件、开机方式统计
# 只读取信息；唯一会安装东西的是微软官方调试工具 WinDbg（用来读蓝屏文件），安装前会先问你。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '黑屏深度诊断' } catch {}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '需要管理员权限，请双击 bat 文件并在弹窗里点“是”。' -ForegroundColor Yellow
    exit 1
}

$report = New-Object System.Collections.Generic.List[string]
function Out-Line($text, $color) {
    if (-not $color) { $color = 'White' }
    Write-Host $text -ForegroundColor $color
    $report.Add($text)
}
function Out-Title($m) { Out-Line ''; Out-Line "==== $m ====" 'Cyan' }
function Out-Ok($m)    { Out-Line "  [正常] $m" 'Green' }
function Out-Bad($m)   { Out-Line "  [注意] $m" 'Yellow' }
function Out-Info($m)  { Out-Line "  $m" 'White' }

function Get-EventField($e, $name) {
    try {
        $x = [xml]$e.ToXml()
        $d = $x.Event.EventData.Data | Where-Object { $_.Name -eq $name }
        if ($d) { return "$($d.'#text')" }
    } catch {}
    return ''
}
# 日志来源不存在时 Get-WinEvent 会直接报错（The parameter is incorrect），统一吞掉
function Get-EvSafe { try { Get-WinEvent @args -ErrorAction Stop } catch { } }

function To-Hex($v) {
    try { return ('0x{0:X}' -f [uint64]$v) } catch { return "$v" }
}

$desktop = [Environment]::GetFolderPath('Desktop')
$since = (Get-Date).AddDays(-60)
Out-Line "黑屏深度诊断报告    生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm')    统计范围：最近 60 天" 'Cyan'

# ---------------------------------------------------------------------------
Out-Title '1. 主板 / BIOS'
$bb = Get-CimInstance Win32_BaseBoard
$bios = Get-CimInstance Win32_BIOS
Out-Info "主板：$($bb.Manufacturer) $($bb.Product)  版本 $($bb.Version)"
Out-Info "BIOS：$($bios.Manufacturer) $($bios.SMBIOSBIOSVersion)  $($bios.ReleaseDate)"
$os = Get-CimInstance Win32_OperatingSystem
Out-Info "系统安装日期：$($os.InstallDate)    本次开机：$($os.LastBootUpTime)"

# ---------------------------------------------------------------------------
Out-Title '2. 所有蓝屏 / 意外关机记录（含参数）'
$kp41 = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 41; StartTime = $since })
$crashTimes = @()
foreach ($e in ($kp41 | Sort-Object TimeCreated)) {
    $bug = Get-EventField $e 'BugcheckCode'
    $p = 1..4 | ForEach-Object { To-Hex (Get-EventField $e "BugcheckParameter$_") }
    Out-Info ("{0:yyyy-MM-dd HH:mm:ss}  错误码 {1}  参数 {2}" -f $e.TimeCreated, (To-Hex $bug), ($p -join ', '))
    $crashTimes += $e.TimeCreated
}
if ($kp41.Count -eq 0) { Out-Ok '没有意外关机记录' }
$bc = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-WER-SystemErrorReporting'; Id = 1001; StartTime = $since })
foreach ($e in $bc) { Out-Info ("{0:yyyy-MM-dd HH:mm}  {1}" -f $e.TimeCreated, (($e.Message -replace '\s+', ' ').Trim())) }
$u6008 = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'EventLog'; Id = 6008; StartTime = $since })
foreach ($e in $u6008) { Out-Info ("{0:yyyy-MM-dd HH:mm}  {1}" -f $e.TimeCreated, (($e.Message -replace '\s+', ' ').Trim())) }

# ---------------------------------------------------------------------------
Out-Title '3. 每次出事前 30 分钟内的错误和警告（找线索）'
foreach ($t in $crashTimes) {
    # 意外关机记录是在下一次开机时写的，往前找上一次开机之前的最后一批事件
    $prevEvents = @()
    foreach ($log in 'System', 'Application') {
        $prevEvents += @(Get-EvSafe -FilterHashtable @{ LogName = $log; StartTime = $t.AddHours(-12); EndTime = $t.AddSeconds(-1); Level = 1, 2, 3 })
    }
    $bootStart = Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-General'; Id = 12; StartTime = $t.AddMinutes(-10); EndTime = $t.AddMinutes(1) } -MaxEvents 1
    if ($bootStart) { $prevEvents = @($prevEvents | Where-Object { $_.TimeCreated -lt $bootStart.TimeCreated }) }
    $last = $prevEvents | Sort-Object TimeCreated -Descending | Select-Object -First 1
    Out-Info ("-- {0:yyyy-MM-dd HH:mm} 那次 --" -f $t)
    if (-not $last) { Out-Info '   出事前没有错误或警告记录'; continue }
    $window = $prevEvents | Where-Object { $_.TimeCreated -ge $last.TimeCreated.AddMinutes(-30) } | Sort-Object TimeCreated | Select-Object -Last 20
    foreach ($e in $window) {
        $msg = (($e.Message -split "`n")[0] -replace '\s+', ' ').Trim()
        if ($msg.Length -gt 110) { $msg = $msg.Substring(0, 110) + '...' }
        Out-Info ("   {0:HH:mm:ss} [{1}] {2} #{3}: {4}" -f $e.TimeCreated, $e.LevelDisplayName, $e.ProviderName, $e.Id, $msg)
    }
}
if ($crashTimes.Count -eq 0) { Out-Info '没有可分析的意外关机' }

# ---------------------------------------------------------------------------
Out-Title '4. 开机方式统计（快速启动 / 冷启动 / 休眠恢复）'
$kb = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Boot'; Id = 27; StartTime = $since })
$types = @{ '0' = 0; '1' = 0; '2' = 0 }
foreach ($e in $kb) {
    $bt = Get-EventField $e 'BootType'
    if ($types.ContainsKey($bt)) { $types[$bt]++ }
}
Out-Info ("冷启动 {0} 次，快速启动 {1} 次，从休眠恢复 {2} 次" -f $types['0'], $types['1'], $types['2'])

# ---------------------------------------------------------------------------
Out-Title '5. 显卡详情（NVIDIA 错误代码 43 重点看）'
foreach ($d in @(Get-PnpDevice -Class Display -ErrorAction SilentlyContinue)) {
    $props = @{}
    foreach ($k in 'DEVPKEY_Device_DriverVersion', 'DEVPKEY_Device_DriverDate', 'DEVPKEY_Device_DriverInfPath', 'DEVPKEY_Device_DriverProvider', 'DEVPKEY_Device_ProblemCode', 'DEVPKEY_Device_HardwareIds') {
        try { $props[$k] = (Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName $k -ErrorAction Stop).Data } catch {}
    }
    $hw = @($props['DEVPKEY_Device_HardwareIds'])[0]
    Out-Info ("{0}  状态 {1}  问题代码 {2}" -f $d.FriendlyName, $d.Status, $props['DEVPKEY_Device_ProblemCode'])
    Out-Info ("   驱动 {0} / {1} / {2} / {3}" -f $props['DEVPKEY_Device_DriverVersion'], $props['DEVPKEY_Device_DriverDate'], $props['DEVPKEY_Device_DriverProvider'], $props['DEVPKEY_Device_DriverInfPath'])
    Out-Info "   硬件 ID：$hw"
}
foreach ($svc in 'NVDisplay.ContainerLocalSystem', 'igfxCUIService2.0.0.0', 'cplspcon') {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) { Out-Info "服务 $($s.DisplayName)：$($s.Status)" }
}
$nvPkgs = @(pnputil /enum-drivers 2>$null | Out-String) -split "(\r?\n){2,}" | Where-Object { $_ -match 'nvidia|nvlddmkm|nv_dispi|nvmi|nvhm' }
Out-Info "系统里的 NVIDIA 驱动包：$($nvPkgs.Count) 个"
$nvEvents = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'nvlddmkm'; StartTime = $since })
Out-Info "NVIDIA 驱动报错事件：$($nvEvents.Count) 条"

# ---------------------------------------------------------------------------
Out-Title '6. 第三方内核驱动（蓝屏 0x50 最常见的来源）'
Write-Host '  正在逐个检查驱动签名，需要几十秒...' -ForegroundColor DarkGray
$third = @()
foreach ($drv in @(Get-CimInstance Win32_SystemDriver | Where-Object { $_.State -eq 'Running' })) {
    $path = "$($drv.PathName)" -replace '^\\\?\?\\', '' -replace '^\\SystemRoot', $env:WINDIR
    if ($path -match '^(?i)system32\\') { $path = Join-Path $env:WINDIR $path }
    if (-not (Test-Path -LiteralPath $path)) { continue }
    $signer = ''
    try { $signer = "$((Get-AuthenticodeSignature -LiteralPath $path).SignerCertificate.Subject)" } catch {}
    if ($signer -match 'O=Microsoft Corporation') { continue }
    $ver = ''
    try { $ver = (Get-Item -LiteralPath $path).VersionInfo.FileVersion } catch {}
    $org = ''
    if ($signer -match 'O="?([^,"]+)') { $org = $Matches[1] }
    $third += [pscustomobject]@{ Name = $drv.Name; File = [IO.Path]::GetFileName($path); Org = $org; Ver = $ver }
}
foreach ($t in ($third | Sort-Object Org, Name)) {
    $flag = ''
    if ("$($t.Org) $($t.Name) $($t.File)" -match '(?i)tencent|qqpc|qihoo|360|kingsoft|ludashi|2345|huorong|TAO|TSSK|TFsFlt') { $flag = '  <== 安全/优化软件驱动，蓝屏常见来源' }
    $color = 'White'
    if ($flag) { $color = 'Yellow' }
    Out-Line ("  {0,-22} {1,-22} {2,-28} {3}{4}" -f $t.Name, $t.File, $t.Org, $t.Ver, $flag) $color
}
Out-Info "共 $($third.Count) 个非微软驱动在运行"

# ---------------------------------------------------------------------------
Out-Title '7. 内存条详情'
foreach ($m in @(Get-CimInstance Win32_PhysicalMemory)) {
    Out-Info ("{0} {1}  {2} GB  {3} MHz  电压 {4} mV  类型代码 {5}" -f "$($m.Manufacturer)".Trim(), "$($m.PartNumber)".Trim(), [math]::Round($m.Capacity / 1GB), $m.ConfiguredClockSpeed, $m.ConfiguredVoltage, $m.SMBIOSMemoryType)
    if ("$($m.PartNumber)" -match 'HMA82G6AFR8N-UH') {
        Out-Ok '这是 SK hynix 原厂 16GB DDR4-2400 笔记本内存（双面 2Rx8），规格和这台电脑完全匹配，纸面兼容性没问题'
        Out-Info '   但“规格对”不等于“这根条子没坏”，蓝屏 0x50 仍然需要做内存检测来排除'
    }
}
$md = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-MemoryDiagnostics-Results' })
foreach ($e in $md) { Out-Info ("内存检测 {0:yyyy-MM-dd}：{1}" -f $e.TimeCreated, (($e.Message -replace '\s+', ' ').Trim())) }
if ($md.Count -eq 0) { Out-Bad '还没有做过内存检测' }

# ---------------------------------------------------------------------------
Out-Title '8. 锁屏后关屏时间'
$out = (powercfg /qh SCHEME_CURRENT SUB_VIDEO VIDEOCONLOCK 2>$null) -join "`n"
$mm = [regex]::Matches($out, '0x([0-9a-fA-F]{8})')
if ($mm.Count -ge 2) {
    $ac = [Convert]::ToInt32($mm[$mm.Count - 2].Groups[1].Value, 16)
    Out-Info "锁屏状态下 $ac 秒后关闭屏幕（电脑锁屏后屏幕会自己黑掉，属于正常）"
}

# ---------------------------------------------------------------------------
Out-Title '9. 蓝屏转储分析（找出是哪个驱动导致的）'
$dumps = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
if ($dumps.Count -eq 0) {
    Out-Info '没有蓝屏转储文件'
} else {
    foreach ($d in $dumps) { Out-Info ("{0}  {1:yyyy-MM-dd HH:mm}  {2} KB" -f $d.Name, $d.LastWriteTime, [math]::Round($d.Length / 1KB)) }

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

    $cdb = Find-Cdb
    if (-not $cdb) {
        Write-Host ''
        Write-Host '  读蓝屏文件需要微软官方的调试工具 WinDbg（免费，约 100MB，来自微软官方）。' -ForegroundColor Cyan
        $ans = Read-Host '  现在用 winget 自动安装吗？输入 y 回车，直接回车跳过'
        if ($ans -match '^[yY]') {
            if (Get-Command winget -ErrorAction SilentlyContinue) {
                winget install --id Microsoft.WinDbg -e --accept-source-agreements --accept-package-agreements
                $cdb = Find-Cdb
            } else {
                Out-Bad '这台电脑没有 winget，请在微软应用商店搜索“WinDbg”安装，然后再运行一次本诊断'
            }
        }
    }

    if ($cdb) {
        $dump = $dumps[0].FullName
        Write-Host '  正在分析最近一次蓝屏（第一次要从微软下载符号文件，可能需要 2~5 分钟，请耐心等）...' -ForegroundColor Cyan
        $symDir = Join-Path $env:SystemDrive 'symbols'
        $raw = & $cdb -z $dump -y "srv*$symDir*https://msdl.microsoft.com/download/symbols" -c '!analyze -v; q' 2>&1 | Out-String
        $detailPath = Join-Path $desktop '蓝屏分析详情.txt'
        $raw | Out-File -LiteralPath $detailPath -Encoding UTF8
        foreach ($k in 'BUGCHECK_CODE', 'BUGCHECK_STR', 'PROCESS_NAME', 'MODULE_NAME', 'IMAGE_NAME', 'SYMBOL_NAME', 'FAILURE_BUCKET_ID', 'DEFAULT_BUCKET_ID') {
            $m = [regex]::Match($raw, "(?m)^$k\s*:\s*(.+)$")
            if ($m.Success) { Out-Info ("{0,-18} {1}" -f $k, $m.Groups[1].Value.Trim()) }
        }
        $img = [regex]::Match($raw, '(?m)^IMAGE_NAME\s*:\s*(.+)$')
        if ($img.Success) {
            $n = $img.Groups[1].Value.Trim()
            if ($n -match '(?i)^nvlddmkm') { Out-Bad 'NVIDIA 显卡驱动导致的蓝屏 —— 重装 NVIDIA 驱动' }
            elseif ($n -match '(?i)^igdkmd') { Out-Bad 'Intel 核显驱动导致的蓝屏 —— 更新 Intel 核显驱动' }
            elseif ($n -match '(?i)^(memory_corruption|ntkrnlmp|ntoskrnl|hardware)') { Out-Bad '指向内存损坏 / 系统内核 —— 内存条嫌疑很大，务必做内存检测' }
            else { Out-Bad "肇事驱动是 $n" }
        }
        if (-not $img.Success) {
            Out-Bad '没能自动读出肇事驱动（可能符号没下载成功）。请把桌面上的“蓝屏分析详情.txt”发给我；'
            Out-Info '   或者下载 NirSoft 的 BlueScreenView（免费绿色版）打开 C:\Windows\Minidump 查看。'
        }
        Out-Info '完整分析已保存到桌面：蓝屏分析详情.txt'
    } else {
        Out-Info '没有分析转储文件。也可以下载 NirSoft 的 BlueScreenView（免费绿色版）打开 C:\Windows\Minidump 查看“肇事驱动”。'
    }
}

# ---------------------------------------------------------------------------
$reportPath = Join-Path $desktop '黑屏深度诊断报告.txt'
try {
    $report | Out-File -LiteralPath $reportPath -Encoding UTF8
    Write-Host "`n报告已保存到桌面：黑屏深度诊断报告.txt（还有“蓝屏分析详情.txt”如果生成了的话），发给我分析" -ForegroundColor Green
} catch {}
Write-Host ''
Read-Host '按回车关闭' | Out-Null
exit 0
