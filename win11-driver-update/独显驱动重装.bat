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
# 独显驱动重装：先彻底清掉旧的/装了一半的 NVIDIA 驱动，再从干净状态装新驱动（带进度条）
# 上次是在旧驱动还在运行时覆盖安装，安装途中旧驱动崩溃蓝屏，导致装了一半。这次的顺序：
#   还原点 -> 准备安装包 -> 确保独显停用（旧驱动不运行）-> 删除所有 NVIDIA 驱动包 -> 暂停 Windows 更新自动装驱动
#   -> 重新启用独显（此时没有 NVIDIA 驱动，不会崩）-> 安装新驱动 -> 检查 -> 重启

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '独显驱动重装' } catch {}
try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}

function Write-Title($m) { Write-Host "`n==== $m ====" -ForegroundColor Cyan }
function Write-Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)   { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m)  { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限，请双击 bat 文件并在弹窗里点「是」。'
    exit 1
}

# ---------------------------------------------------------------------------
# 进度条
# ---------------------------------------------------------------------------
$TotalSteps = 8
function Set-Step($n, $text) {
    Write-Title "第 $n/$TotalSteps 步：$text"
    Write-Progress -Id 0 -Activity '独显驱动重装 —— 总进度' -Status "第 $n/$TotalSteps 步：$text" -PercentComplete ([int](($n - 1) / $TotalSteps * 100))
}

# 把耗时的操作放到后台跑，前台显示进度条（按预计时间推进，最多到 95%，完成时跳到 100%）
function Invoke-WithProgress($activity, [scriptblock]$sb, $estSec, $argList) {
    if ($argList -and @($argList).Count -gt 0) { $job = Start-Job -ScriptBlock $sb -ArgumentList $argList } else { $job = Start-Job -ScriptBlock $sb }
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($job.State -eq 'Running' -or $job.State -eq 'NotStarted') {
        $pct = [math]::Min(95, [int]($sw.Elapsed.TotalSeconds / $estSec * 100))
        Write-Progress -Id 1 -ParentId 0 -Activity $activity -Status ("已用时 {0:mm\:ss}，预计约 {1} 分钟" -f $sw.Elapsed, [math]::Max(1, [math]::Ceiling($estSec / 60))) -PercentComplete $pct
        Start-Sleep -Milliseconds 500
    }
    Write-Progress -Id 1 -ParentId 0 -Activity $activity -Completed
    $r = Receive-Job $job -Wait
    Remove-Job $job -Force
    return $r
}

function Get-FolderMB($p) {
    if (-not (Test-Path -LiteralPath $p)) { return 0 }
    return [math]::Round(((Get-ChildItem -LiteralPath $p -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum) / 1MB)
}

$UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 Edg/130.0'
# ---------------------------------------------------------------------------
$Referer = 'https://www.nvidia.com/'

# 系统代理（clash 等打开「系统代理」后写在这里）
function Get-SystemProxy {
    try {
        $p = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction Stop
        if ($p.ProxyEnable -eq 1 -and $p.ProxyServer) {
            $v = "$($p.ProxyServer)"
            if ($v -match 'https=([^;]+)') { return $Matches[1] }
            if ($v -match '^[^=;]+$') { return $v }
        }
    } catch {}
    return $null
}

function Test-Downloaded($dest) {
    return ((Test-Path -LiteralPath $dest) -and (Get-Item -LiteralPath $dest).Length -gt 10MB)
}

# 依次尝试：curl 直连（绕过代理） -> curl 走系统代理 -> BITS -> Invoke-WebRequest
function Get-Download($urls, $dest) {
    $curl = Join-Path $env:WINDIR 'System32\curl.exe'
    $proxy = Get-SystemProxy
    foreach ($u in $urls) {
        if (-not $u) { continue }
        Write-Info "下载：$u"
        $ways = @()
        if (Test-Path -LiteralPath $curl) {
            $ways += @{ Name = '直连（绕过代理）'; Args = @('--noproxy', '*') }
            if ($proxy) { $ways += @{ Name = "走代理 $proxy"; Args = @('--proxy', "http://$proxy") } }
        }
        foreach ($w in $ways) {
            Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
            $a = @('-L', '-f', '--retry', '2', '--connect-timeout', '20', '-A', $UA, '-e', $Referer, '-o', $dest) + $w.Args + @($u)
            & $curl @a
            if ($LASTEXITCODE -eq 0 -and (Test-Downloaded $dest)) { Write-Ok "下载成功（$($w.Name)）"; return $true }
            Write-Bad "$($w.Name) 失败（curl 返回 $LASTEXITCODE）"
        }
        Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
        try {
            Start-BitsTransfer -Source $u -Destination $dest -DisplayName '下载显卡驱动' -ErrorAction Stop
            if (Test-Downloaded $dest) { Write-Ok '下载成功（BITS）'; return $true }
        } catch {}
        try {
            Invoke-WebRequest -Uri $u -OutFile $dest -UseBasicParsing -UserAgent $UA -Headers @{ Referer = $Referer } -TimeoutSec 3600 -ErrorAction Stop
            if (Test-Downloaded $dest) { Write-Ok '下载成功（WebRequest）'; return $true }
        } catch {
            Write-Bad "这个地址下载失败：$($_.Exception.Message)"
        }
    }
    return $false
}

# 只安装带有效官方签名的文件
function Test-Signed($file, $vendorPattern) {
    $sig = Invoke-WithProgress '校验 NVIDIA 数字签名' { param($f) $x = Get-AuthenticodeSignature -LiteralPath $f; [pscustomobject]@{ Status = "$($x.Status)"; SignerCertificate = [pscustomobject]@{ Subject = "$($x.SignerCertificate.Subject)" } } } 120 @($file)
    $subject = "$($sig.SignerCertificate.Subject)"
    if ($sig.Status -eq 'Valid' -and $subject -match $vendorPattern) {
        Write-Ok "数字签名校验通过：$(($subject -split ',')[0])"
        return $true
    }
    Write-Bad "数字签名校验没通过（$($sig.Status) / $subject），为了安全不安装这个文件"
    return $false
}


function Get-NvDevices { @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_10DE' }) }
function Get-NvDriverInfo($d) {
    $ver = ''; $prov = ''
    try { $ver = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverVersion -ErrorAction Stop).Data)" } catch {}
    try { $prov = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverProvider -ErrorAction Stop).Data)" } catch {}
    # Windows 驱动版本 32.0.15.8278 的最后 5 位就是 NVIDIA 版本 582.78
    $short = ''
    $digits = $ver -replace '\D', ''
    if ($digits.Length -ge 5) { $t = $digits.Substring($digits.Length - 5); $short = '{0}.{1}' -f [int]$t.Substring(0, 3), $t.Substring(3) }
    return @{ Ver = $ver; Provider = $prov; Short = $short }
}

Write-Host ''
Write-Host '  全程约 15~25 分钟，窗口顶部有进度条。屏幕闪烁、黑几秒都正常，不要强制关机、不要合盖，插上电源。' -ForegroundColor Yellow

# ---------------------------------------------------------------------------
Set-Step 1 '检查'
# 托盘程序退出了，内核驱动也可能还在，所以按驱动服务判断
$tencentDrv = @(Get-Service -Name TFsFlt, QQSysMonX64, TSSysKit, TAOKernelDriver -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Running' })
if ($tencentDrv.Count -gt 0 -or (Get-Process -Name QQPCRTP, QQPCTray -ErrorAction SilentlyContinue)) {
    Write-Bad '腾讯电脑管家（及其内核驱动）还在运行。它的文件过滤驱动会拦截、扫描正在写入的驱动文件，可能让安装失败或装一半。'
    Write-Info '   强烈建议先卸载它（设置 -> 应用 -> 已安装的应用 -> 腾讯电脑管家 -> 卸载），重启后再运行本程序。'
    $ans = Read-Host '  仍然继续吗？输入 y 继续，直接回车退出'
    if ($ans -notmatch '^[yY]') { exit 0 }
}
$nv = Get-NvDevices
if ($nv.Count -eq 0) { Write-Bad '没找到 NVIDIA 显卡（BIOS 里被关掉了？）'; Read-Host '按回车关闭' | Out-Null; exit 0 }
foreach ($d in $nv) {
    $i = Get-NvDriverInfo $d
    Write-Info ("找到：{0}  分类 {1}  状态 {2}  问题 {3}  驱动 {4} {5}" -f $d.FriendlyName, $d.Class, $d.Status, $d.ConfigManagerErrorCode, $i.Provider, $i.Ver)
}

# ---------------------------------------------------------------------------
Set-Step 2 '创建还原点'
try {
    Enable-ComputerRestore -Drive "$env:SystemDrive\" -ErrorAction SilentlyContinue
    New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore' -Name SystemRestorePointCreationFrequency -Value 0 -PropertyType DWord -Force | Out-Null
    Checkpoint-Computer -Description '重装独显驱动之前' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop
    Write-Ok '已创建还原点「重装独显驱动之前」'
} catch {
    Write-Bad "还原点没创建成功：$($_.Exception.Message)"
    $ans = Read-Host '  没有还原点也继续吗？输入 y 继续，直接回车退出'
    if ($ans -notmatch '^[yY]') { exit 0 }
}

# ---------------------------------------------------------------------------
Set-Step 3 '准备新驱动安装包（下载 + 校验签名）'
$WorkDir = Join-Path $env:TEMP 'DriverUpdate'
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
$pkg = Get-ChildItem -LiteralPath $WorkDir -Filter '*notebook*.exe' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$file = $null
$signedOk = $false
if ($pkg -and $pkg.Length -gt 100MB) {
    Write-Info "找到之前下载好的：$($pkg.Name)，先校验它是否完整"
    if (Test-Signed $pkg.FullName 'NVIDIA') {
        $file = $pkg.FullName
        $signedOk = $true
    } else {
        Write-Bad '之前下载的文件不完整或损坏，删掉重新下载'
        Remove-Item -LiteralPath $pkg.FullName -Force -ErrorAction SilentlyContinue
    }
}
if (-not $file) {
    $nvUrl = $null
    foreach ($apiHost in 'gfwsl.geforce.com', 'gfwsl.geforce.cn') {
        foreach ($osId in 135, 57) {
            try {
                $api = "https://$apiHost/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&pfid=853&osID=$osId&languageCode=2052&dch=1&isWHQL=1&beta=0&numberOfResults=1"
                $j = Invoke-RestMethod -Uri $api -UserAgent $UA -TimeoutSec 60 -ErrorAction Stop
                if ($j.Success -eq '1' -and $j.IDS) { $nvUrl = [Uri]::UnescapeDataString("$($j.IDS[0].downloadInfo.DownloadURL)"); break }
            } catch {}
        }
        if ($nvUrl) { break }
    }
    if ($nvUrl) {
        $path = ([Uri]$nvUrl).AbsolutePath
        $file = Join-Path $WorkDir ([IO.Path]::GetFileName($path))
        $mirrors = @('cn.download.nvidia.com', 'us.download.nvidia.com', 'international.download.nvidia.com') | ForEach-Object { "https://$_$path" }
        Write-Info '（下载进度看下面 curl 显示的百分比）'
        if (-not (Get-Download $mirrors $file)) { $file = $null }
    }
}
if (-not $file) { Write-Bad '没拿到 NVIDIA 驱动安装包。到这里为止没有改动任何东西。关掉 clash 再试，或把截图发给我。'; Read-Host '按回车关闭' | Out-Null; exit 0 }
if (-not $signedOk -and -not (Test-Signed $file 'NVIDIA')) { Read-Host '按回车关闭' | Out-Null; exit 0 }
$target = ''
if ([IO.Path]::GetFileName($file) -match '^(\d{3}\.\d{2})') { $target = $Matches[1] }
Write-Info "将要安装的版本：$target"

# ---------------------------------------------------------------------------
Set-Step 4 '确保独显是停用状态（旧驱动不运行）'
foreach ($d in Get-NvDevices) {
    if ($d.ConfigManagerErrorCode -eq 22) {
        Write-Ok '独显已经是停用状态'
    } else {
        try { Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop; Write-Ok '已停用独显' } catch { Write-Bad "停用失败：$($_.Exception.Message)" }
    }
}
foreach ($svc in 'NVDisplay.ContainerLocalSystem', 'NvContainerLocalSystem') { Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 3

# ---------------------------------------------------------------------------
Set-Step 5 '删除系统里所有 NVIDIA 驱动包（旧的和装了一半的）'
$pkgs = @(Invoke-WithProgress '列出系统里的第三方驱动包' { Get-WindowsDriver -Online -ErrorAction SilentlyContinue | Where-Object { $_.ProviderName -match 'NVIDIA' } | Select-Object Driver, OriginalFileName, Version, ClassName } 60 @() |
    Where-Object { $_ -and $_.Driver })
if ($pkgs.Count -eq 0) { Write-Ok '没有 NVIDIA 驱动包需要删除' }
$k = 0
foreach ($p in $pkgs) {
    $k++
    Write-Progress -Id 1 -ParentId 0 -Activity '删除旧驱动包' -Status "$k / $($pkgs.Count)：$($p.Driver)" -PercentComplete ([int]($k / $pkgs.Count * 100))
    $out = pnputil.exe /delete-driver $p.Driver /uninstall /force 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) { Write-Ok ("已删除 {0}（{1}，{2}，版本 {3}）" -f $p.Driver, "$($p.OriginalFileName)".Split('\')[-1], $p.ClassName, $p.Version) }
    else { Write-Bad ("{0} 删除失败：{1}" -f $p.Driver, ($out -replace '\s+', ' ').Trim()) }
}
Write-Progress -Id 1 -ParentId 0 -Activity '删除旧驱动包' -Completed

# 暂停 Windows 更新自动安装驱动，否则它可能马上又把旧 NVIDIA 驱动装回来
$dsKey = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\DriverSearching'
New-Item -Path $dsKey -Force | Out-Null
Set-ItemProperty -Path $dsKey -Name SearchOrderConfig -Value 0 -Type DWord
Write-Ok '已关闭「自动从 Windows 更新下载驱动」（以后想打开：设置 -> 系统 -> 系统信息 -> 高级系统设置 -> 硬件 -> 设备安装设置 -> 是）'

# ---------------------------------------------------------------------------
Set-Step 6 '重新启用独显（现在没有 NVIDIA 驱动，不会崩）'
foreach ($d in Get-NvDevices) { try { Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop } catch { Write-Bad "启用失败：$($_.Exception.Message)" } }
Start-Sleep -Seconds 5
foreach ($d in Get-NvDevices) { Write-Info ("现在：{0}  分类 {1}  状态 {2}" -f $d.FriendlyName, $d.Class, $d.Status) }

# ---------------------------------------------------------------------------
Set-Step 7 '安装新 NVIDIA 驱动（清洁安装）'
$extractDir = 'C:\NVIDIA\DisplayDriver'
$extractStart = Get-FolderMB $extractDir
$proc = Start-Process -FilePath $file -ArgumentList '-s -clean -noreboot -noeula' -PassThru
$null = $proc.Handle   # 先取一次句柄，结束后才能读到返回码
$sw = [Diagnostics.Stopwatch]::StartNew()
$estSec = 600
$maxSec = 40 * 60
$phase = ''
$timedOut = $false
while ($true) {
    if ($sw.Elapsed.TotalSeconds -gt $maxSec) { $timedOut = $true; break }
    $children = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        ($_.ExecutablePath -match '\\NVIDIA' -and $_.Name -match 'setup|nvi2|install') -or $_.Name -match '^(drvinst|dpinst)\.exe$' })
    $running = (-not $proc.HasExited) -or $children.Count -gt 0
    if (-not $running) { break }
    $extracted = (Get-FolderMB $extractDir) - $extractStart
    if ($children | Where-Object { $_.Name -match 'drvinst|dpinst' }) {
        $phase = '正在把驱动写入系统（屏幕可能会闪烁、黑几秒）'
        $pct = [math]::Min(95, 60 + [int]($sw.Elapsed.TotalSeconds / $estSec * 35))
    } elseif ($children.Count -gt 0) {
        $phase = '正在安装驱动组件'
        $pct = [math]::Min(90, 35 + [int]($sw.Elapsed.TotalSeconds / $estSec * 55))
    } else {
        $phase = '正在解压安装包'
        if ($extracted -gt 0) { $phase += "（已解压 $extracted MB）" }
        $pct = [math]::Min(35, [math]::Max([int]($extracted / 1500 * 35), [int]($sw.Elapsed.TotalSeconds / 180 * 30)))
    }
    Write-Progress -Id 1 -ParentId 0 -Activity '安装 NVIDIA 驱动' -Status ("{0}    已用时 {1:mm\:ss}，通常 5~10 分钟" -f $phase, $sw.Elapsed) -PercentComplete $pct
    Start-Sleep -Seconds 2
}
Write-Progress -Id 1 -ParentId 0 -Activity '安装 NVIDIA 驱动' -Completed
if ($timedOut) {
    Write-Bad '已经等了 40 分钟，安装还没有结束。不再等待，直接检查结果（安装程序可能还在后台运行）。'
} else {
    Write-Info ("安装程序结束，用时 {0:mm\:ss}，返回码 {1}" -f $sw.Elapsed, $proc.ExitCode)
}
Start-Sleep -Seconds 5

# ---------------------------------------------------------------------------
Set-Step 8 '检查结果'
$ok = $false
foreach ($d in Get-NvDevices) {
    $i = Get-NvDriverInfo $d
    Write-Info ("{0}  分类 {1}  状态 {2}  问题代码 {3}  驱动 {4} {5}（{6}）" -f $d.FriendlyName, $d.Class, $d.Status, $d.ConfigManagerErrorCode, $i.Provider, $i.Short, $i.Ver)
    if ($i.Provider -match 'NVIDIA' -and (($target -and $i.Short -eq $target) -or (-not $target -and $d.Class -eq 'Display'))) { $ok = $true }
}
Write-Progress -Id 0 -Activity '独显驱动重装 —— 总进度' -Completed
if ($ok) {
    Write-Ok "新 NVIDIA 驱动 $target 已装上（错误代码 43 要重启后才能看出是否消失）"
} else {
    Write-Bad '新驱动没装上。截图发给我。'
    $ans = Read-Host '  先把独显停用，避免蓝屏吗？输入 y 停用（推荐），直接回车不停用'
    if ($ans -match '^[yY]') { foreach ($d in Get-NvDevices) { Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }; Write-Ok '已停用独显' }
    Read-Host '按回车关闭' | Out-Null
    exit 0
}

Write-Info '重启后运行「驱动安装检查.bat」，把报告发给我。如果之后又蓝屏，运行「停用独显并分析蓝屏.bat」把独显停用。'
Write-Host ''
Write-Host '  60 秒后自动重启，按 N 取消。' -ForegroundColor Yellow
$cancel = $false
for ($s = 60; $s -gt 0; $s--) {
    Write-Host ("`r  {0,2} 秒后重启...（按 N 取消）" -f $s) -NoNewline
    for ($q = 0; $q -lt 5; $q++) {
        Start-Sleep -Milliseconds 200
        while ([Console]::KeyAvailable) { if (([Console]::ReadKey($true)).Key -eq 'N') { $cancel = $true } }
        if ($cancel) { break }
    }
    if ($cancel) { break }
}
Write-Host ''
if ($cancel) { Write-Ok '已取消自动重启，请稍后自己重启。'; Read-Host '按回车关闭' | Out-Null; exit 0 }
Restart-Computer -Force
