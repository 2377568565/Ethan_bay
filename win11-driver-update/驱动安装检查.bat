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
# 驱动安装检查（独显重装后用）：
#   新 NVIDIA 驱动有没有装上、MX150 错误代码 43 有没有消失、显卡能不能真正工作、重装之后有没有再蓝屏（并分析是谁造成的）
# 只读取信息；唯一的改动「停用 MX150」只在它仍然出错时才会问你，不同意就不改。
# 报告保存到桌面：驱动安装检查报告.txt（边查边存，中途蓝屏也不会丢）

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '驱动安装检查' } catch {}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '需要管理员权限，请双击 bat 文件并在弹窗里点「是」。' -ForegroundColor Yellow
    exit 1
}

$desktop = [Environment]::GetFolderPath('Desktop')
$ReportPath = Join-Path $desktop '驱动安装检查报告.txt'
Set-Content -LiteralPath $ReportPath -Value '' -Encoding UTF8
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
function Get-Prop($id, $key) { try { return (Get-PnpDeviceProperty -InstanceId $id -KeyName $key -ErrorAction Stop).Data } catch { return $null } }
# Windows 驱动版本 32.0.15.8278 的最后 5 位就是 NVIDIA 版本 582.78
function Get-NvShort($ver) {
    $digits = "$ver" -replace '\D', ''
    if ($digits.Length -lt 5) { return '' }
    $t = $digits.Substring($digits.Length - 5)
    return '{0}.{1}' -f [int]$t.Substring(0, 3), $t.Substring(3)
}

$os = Get-CimInstance Win32_OperatingSystem
Out-Line "驱动安装检查报告    生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm')    本次开机：$($os.LastBootUpTime.ToString('yyyy-MM-dd HH:mm'))" 'Cyan'

# 以最近一次「重装独显驱动之前」（没有就用「更新显卡驱动之前」）还原点的时间作为起点
$since = (Get-Date).AddDays(-1)
$sinceName = ''
try {
    $rp = Get-ComputerRestorePoint -ErrorAction Stop |
        Where-Object { $_.Description -eq '重装独显驱动之前' -or $_.Description -eq '更新显卡驱动之前' } |
        Sort-Object { [Management.ManagementDateTimeConverter]::ToDateTime($_.CreationTime) } | Select-Object -Last 1
    if ($rp) {
        $since = [Management.ManagementDateTimeConverter]::ToDateTime($rp.CreationTime)
        $sinceName = $rp.Description
    }
} catch {}

# ---------------------------------------------------------------------------
Out-Title '1. 还原点'
if ($sinceName) { Out-Ok ("还原点「{0}」（{1:MM-dd HH:mm}）存在，出问题可以退回。下面的稳定性从这个时间开始统计" -f $sinceName, $since) }
else { Out-Bad '没找到重装前的还原点，稳定性按最近 24 小时统计' }

# ---------------------------------------------------------------------------
Out-Title '2. 显卡驱动'
$nvOk = $false; $nvCode = $null; $nvDisabled = $false; $nvFound = $false
foreach ($d in @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_(8086|10DE)' -and ($_.Class -eq 'Display' -or $_.InstanceId -match 'VEN_10DE') })) {
    $ver = "$(Get-Prop $d.InstanceId 'DEVPKEY_Device_DriverVersion')"
    $prov = "$(Get-Prop $d.InstanceId 'DEVPKEY_Device_DriverProvider')"
    $date = Get-Prop $d.InstanceId 'DEVPKEY_Device_DriverDate'
    $dateText = ''
    if ($date) { try { $dateText = ([datetime]$date).ToString('yyyy-MM-dd') } catch {} }
    $code = Get-Prop $d.InstanceId 'DEVPKEY_Device_ProblemCode'
    if ($null -eq $code) { $code = 0 }
    $name = $d.FriendlyName
    if (-not $name) { $name = '(无名称)' }
    Out-Info ("{0}  分类 {1}  状态 {2}  问题代码 {3}" -f $name, $d.Class, $d.Status, $code)
    Out-Info ("   驱动 {0} {1}（{2}）" -f $prov, $ver, $dateText)

    if ($d.InstanceId -match 'VEN_10DE') {
        $nvFound = $true
        $nvCode = [int]$code
        $short = Get-NvShort $ver
        $isNew = $false
        try { $isNew = ($prov -match 'NVIDIA') -and ([version]$short -ge [version]'500.0') } catch {}
        if ($isNew) { $nvOk = $true; Out-Ok "NVIDIA 新驱动已装上：$short" }
        else { Out-Bad "NVIDIA 驱动不是新版（现在是 $short）" }
        if ($nvCode -eq 22) { $nvDisabled = $true; Out-Bad 'MX150 现在是停用状态' }
        elseif ($nvCode -eq 43) { Out-Bad 'MX150 仍然是错误代码 43（显卡初始化失败）' }
        elseif ($nvCode -ne 0) { Out-Bad "MX150 有错误（代码 $nvCode）" }
        else { Out-Ok 'MX150 没有错误代码，状态正常' }
    } elseif ($code -ne 0) {
        Out-Bad "Intel 核显有错误（代码 $code）"
    }
}
if (-not $nvFound) { Out-Bad '没找到 NVIDIA 显卡' }

# 让 NVIDIA 显卡「说句话」：nvidia-smi 能读出显卡信息，说明显卡和驱动真的能一起工作
$smiOk = $false
$smi = Join-Path $env:WINDIR 'System32\nvidia-smi.exe'
if ((Test-Path -LiteralPath $smi) -and -not $nvDisabled) {
    $q = & $smi --query-gpu=name,driver_version,temperature.gpu,pstate --format=csv,noheader 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -and $q.Trim()) { $smiOk = $true; Out-Ok "nvidia-smi 实测：显卡能正常工作（$($q.Trim())）" }
    else { Out-Bad "nvidia-smi 读不到显卡：$(($q -replace '\s+', ' ').Trim())" }
}

# ---------------------------------------------------------------------------
Out-Title ("3. 稳定性：{0:MM-dd HH:mm} 以来" -f $since)
$kp41 = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 41; StartTime = $since })
$tdr = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Display'; Id = 4101; StartTime = $since })
$nvErr = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'nvlddmkm'; StartTime = $since })
$whea = @(Get-EvSafe -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-WHEA-Logger'; StartTime = $since })
$dumps = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $since } | Sort-Object LastWriteTime -Descending)
if ($kp41.Count -eq 0) { Out-Ok '没有蓝屏 / 死机' } else { Out-Bad "蓝屏 / 死机 $($kp41.Count) 次" }
if ($tdr.Count -eq 0) { Out-Ok '没有「显卡驱动停止响应」' } else { Out-Bad "显卡驱动停止响应后恢复 $($tdr.Count) 次" }
if ($nvErr.Count -eq 0) { Out-Ok '没有 NVIDIA 驱动报错' } else { Out-Bad "NVIDIA 驱动报错 $($nvErr.Count) 次" }
if ($whea.Count -eq 0) { Out-Ok '没有硬件错误' } else { Out-Bad "硬件错误 $($whea.Count) 条" }

# 有新蓝屏就分析是谁造成的（需要之前装过的 WinDbg）
$culprits = @()
if ($dumps.Count -gt 0) {
    $cdb = $null
    foreach ($p in @("${env:ProgramFiles(x86)}\Windows Kits\10\Debuggers\x64\cdb.exe", "$env:ProgramFiles\Windows Kits\10\Debuggers\x64\cdb.exe")) { if (Test-Path -LiteralPath $p) { $cdb = $p } }
    if (-not $cdb) {
        $pkg = Get-AppxPackage -Name 'Microsoft.WinDbg*' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pkg) { $c = Get-ChildItem -LiteralPath $pkg.InstallLocation -Recurse -Filter cdb.exe -ErrorAction SilentlyContinue | Sort-Object { $_.FullName -notmatch 'amd64|x64' } | Select-Object -First 1; if ($c) { $cdb = $c.FullName } }
    }
    if ($cdb) {
        $symDir = Join-Path $env:SystemDrive 'symbols'
        foreach ($d in ($dumps | Select-Object -First 4)) {
            Write-Host ("  正在分析 {0:MM-dd HH:mm} 的蓝屏（约半分钟）..." -f $d.LastWriteTime) -ForegroundColor DarkGray
            $raw = & $cdb -z $d.FullName -y "srv*$symDir*https://msdl.microsoft.com/download/symbols" -c '!analyze -v; q' 2>&1 | Out-String
            $m = [regex]::Match($raw, '(?m)^IMAGE_NAME\s*:\s*(.+)$')
            $img = '?'
            if ($m.Success) { $img = $m.Groups[1].Value.Trim() }
            $culprits += $img
            Out-Info ("   {0:MM-dd HH:mm} 蓝屏，肇事模块：{1}" -f $d.LastWriteTime, $img)
        }
    } else {
        Out-Info '   没找到 WinDbg，没法分析蓝屏原因'
    }
}

# ---------------------------------------------------------------------------
Out-Title '结论'
$nvCrash = @($culprits | Where-Object { $_ -match '(?i)^nvlddmkm' }).Count
$verdict = ''
if ($nvDisabled) {
    $verdict = 'disabled'
    Out-Info 'MX150 现在是停用状态，所以没法判断新驱动好不好。想测试就去设备管理器启用它，用一段时间后再运行本检查。'
} elseif ($nvOk -and $nvCode -eq 0 -and $kp41.Count -eq 0) {
    $verdict = 'good'
    Out-Line '  [正常] 新驱动装好了，MX150 错误代码 43 已经消失，到目前为止没有蓝屏。' 'Green'
    if ($smiOk) { Out-Line '  [正常] nvidia-smi 实测显卡能正常工作。' 'Green' }
    Out-Info '  接下来正常用 2~3 天，每天运行一次本检查。一直没有蓝屏，独显就算修好了。'
} elseif ($nvOk -and $nvCode -eq 43) {
    $verdict = 'hw'
    Out-Bad '新驱动已经装好，MX150 却仍然是错误代码 43 —— 驱动没问题，问题在显卡本身（很可能是硬件老化/损坏）。'
    Out-Info '  建议停用 MX150。日常使用不受影响；想彻底修只能送修（更换主板/显卡芯片，通常不划算）。'
} elseif ($kp41.Count -gt 0) {
    $verdict = 'crash'
    if ($nvCrash -gt 0) { Out-Bad "重装后又蓝屏 $($kp41.Count) 次，其中 $nvCrash 次是 NVIDIA 驱动造成的 —— MX150 不稳定，建议停用。" }
    else { Out-Bad "重装后又蓝屏 $($kp41.Count) 次，肇事模块：$((@($culprits | Sort-Object -Unique)) -join '、')。把报告发给我。" }
} elseif (-not $nvOk) {
    $verdict = 'notinstalled'
    Out-Bad '新驱动没装上。把「独显驱动重装」窗口的截图和本报告发给我。'
} else {
    Out-Bad "MX150 有其他错误（代码 $nvCode），把报告发给我。"
}

# 显卡仍然有问题时，可以直接停用它（先问你）
$nvDev = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_10DE' } | Select-Object -First 1
if ($nvDev -and ($verdict -eq 'hw' -or ($verdict -eq 'crash' -and $nvCrash -gt 0))) {
    Write-Host ''
    Write-Host '  停用 MX150 后：屏幕由 Intel 核显照常显示，上网/办公/看视频不受影响，只是没有独显加速；随时可以在设备管理器里重新启用。' -ForegroundColor Cyan
    $ans = Read-Host '  现在停用 MX150 吗？输入 y 回车（推荐），直接回车跳过'
    if ($ans -match '^[yY]') {
        try {
            Disable-PnpDevice -InstanceId $nvDev.InstanceId -Confirm:$false -ErrorAction Stop
            Out-Ok '已停用 MX150'
        } catch {
            Out-Bad "停用失败：$($_.Exception.Message)（可以在设备管理器里右键它 -> 禁用设备）"
        }
    }
}

Write-Host "`n报告已保存到桌面：驱动安装检查报告.txt（发给我）" -ForegroundColor Green
Read-Host '按回车关闭' | Out-Null
exit 0
