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
# 独显驱动重装：先彻底清掉旧的/装了一半的 NVIDIA 驱动，再从干净状态装新驱动
# 上次是在旧驱动还在运行时覆盖安装，安装途中旧驱动崩溃蓝屏，导致装了一半。这次的顺序：
#   还原点 -> 停用独显（让旧驱动停下来）-> 删除所有 NVIDIA 驱动包 -> 暂停 Windows 更新自动装驱动
#   -> 重新启用独显（此时没有 NVIDIA 驱动，不会崩）-> 安装新驱动 -> 检查 -> 重启

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '独显驱动重装' } catch {}
try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}

function Write-Title($m) { Write-Host "`n==== $m ====" -ForegroundColor Cyan }
function Write-Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)   { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m)  { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限，请双击 bat 文件并在弹窗里点“是”。'
    exit 1
}

$UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 Edg/130.0'
$WorkDir = Join-Path $env:TEMP 'DriverUpdate'
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null

Write-Host ''
Write-Host '  注意：安装显卡驱动时屏幕会闪烁、黑几秒，都是正常的，请不要强制关机，也不要合上盖子。' -ForegroundColor Yellow
Write-Host '  全程需要联网，下载约 1GB，插上电源。' -ForegroundColor Yellow

# ---------------------------------------------------------------------------
$Referer = 'https://www.nvidia.com/'

# 系统代理（clash 等打开“系统代理”后写在这里）
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
    Write-Info '正在校验数字签名（文件很大，约需 1~3 分钟，窗口不动是正常的）...'
    $sig = Get-AuthenticodeSignature -LiteralPath $file
    $subject = "$($sig.SignerCertificate.Subject)"
    if ($sig.Status -eq 'Valid' -and $subject -match $vendorPattern) {
        Write-Ok "数字签名校验通过：$(($subject -split ',')[0])"
        return $true
    }
    Write-Bad "数字签名校验没通过（$($sig.Status) / $subject），为了安全不安装这个文件"
    return $false
}


function Get-NvDevices { @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -match '^PCI\\VEN_10DE' }) }

Write-Host ''
Write-Host '  全程约 15~25 分钟。屏幕闪烁、黑几秒都正常，不要强制关机、不要合盖，插上电源。' -ForegroundColor Yellow

# ---------------------------------------------------------------------------
Write-Title '第 0 步：检查'
if (Get-Process -Name QQPCRTP, QQPCTray -ErrorAction SilentlyContinue) {
    Write-Bad '腾讯电脑管家还在运行。它的内核驱动会拦截驱动安装，也是蓝屏的常见来源。'
    Write-Info '   强烈建议先卸载它（设置 -> 应用 -> 已安装的应用 -> 腾讯电脑管家 -> 卸载），重启后再运行本程序。'
    $ans = Read-Host '  仍然继续吗？输入 y 继续，直接回车退出'
    if ($ans -notmatch '^[yY]') { exit 0 }
}
$nv = Get-NvDevices
if ($nv.Count -eq 0) { Write-Bad '没找到 NVIDIA 显卡（BIOS 里被关掉了？）'; Read-Host '按回车关闭' | Out-Null; exit 0 }
foreach ($d in $nv) { Write-Info ("找到：{0}  分类 {1}  状态 {2}" -f $d.FriendlyName, $d.Class, $d.Status) }

# ---------------------------------------------------------------------------
Write-Title '第 1 步：创建还原点'
try {
    New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore' -Name SystemRestorePointCreationFrequency -Value 0 -PropertyType DWord -Force | Out-Null
    Checkpoint-Computer -Description '重装独显驱动之前' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop
    Write-Ok '已创建还原点“重装独显驱动之前”'
} catch { Write-Bad "还原点没创建成功：$($_.Exception.Message)" }

# ---------------------------------------------------------------------------
Write-Title '第 2 步：准备新驱动安装包'
$WorkDir = Join-Path $env:TEMP 'DriverUpdate'
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
$pkg = Get-ChildItem -LiteralPath $WorkDir -Filter '*notebook*.exe' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($pkg -and $pkg.Length -gt 100MB) {
    Write-Ok "使用之前下载好的：$($pkg.Name)"
    $file = $pkg.FullName
} else {
    $file = $null
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
        if (-not (Get-Download $mirrors $file)) { $file = $null }
    }
}
if (-not $file) { Write-Bad '没拿到 NVIDIA 驱动安装包，先不动任何东西。关掉 clash 再试，或把截图发给我。'; Read-Host '按回车关闭' | Out-Null; exit 0 }
if (-not (Test-Signed $file 'NVIDIA')) { Read-Host '按回车关闭' | Out-Null; exit 0 }

# ---------------------------------------------------------------------------
Write-Title '第 3 步：停用独显，让旧驱动停下来'
foreach ($d in Get-NvDevices) {
    if ($d.Status -ne 'Error' -or $d.ConfigManagerErrorCode -ne 22) {
        try { Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop; Write-Ok '已停用独显' } catch { Write-Bad "停用失败：$($_.Exception.Message)" }
    } else { Write-Ok '独显已经是停用状态' }
}
foreach ($svc in 'NVDisplay.ContainerLocalSystem', 'NvContainerLocalSystem') { Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 3

# ---------------------------------------------------------------------------
Write-Title '第 4 步：删除系统里所有 NVIDIA 驱动包（旧的 398.35 和装了一半的）'
Write-Info '正在列出第三方驱动包（约 1 分钟）...'
$pkgs = @(Get-WindowsDriver -Online -ErrorAction SilentlyContinue | Where-Object { $_.ProviderName -match 'NVIDIA' })
if ($pkgs.Count -eq 0) { Write-Ok '没有 NVIDIA 驱动包需要删除' }
foreach ($p in $pkgs) {
    $out = pnputil.exe /delete-driver $p.Driver /uninstall /force 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) { Write-Ok ("已删除 {0}（{1} {2}）" -f $p.Driver, $p.OriginalFileName.Split('\')[-1], $p.Version) }
    else { Write-Bad ("{0} 删除失败：{1}" -f $p.Driver, ($out -replace '\s+', ' ').Trim()) }
}

# ---------------------------------------------------------------------------
Write-Title '第 5 步：暂停 Windows 更新自动安装驱动'
# 否则 Windows 更新可能又把 2018 年的旧 NVIDIA 驱动装回来
$dsKey = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\DriverSearching'
New-Item -Path $dsKey -Force | Out-Null
Set-ItemProperty -Path $dsKey -Name SearchOrderConfig -Value 0 -Type DWord
Write-Ok '已关闭“自动从 Windows 更新下载驱动”（以后想打开：设置 -> 系统 -> 系统信息 -> 高级系统设置 -> 硬件 -> 设备安装设置 -> 是）'

# ---------------------------------------------------------------------------
Write-Title '第 6 步：重新启用独显（现在没有 NVIDIA 驱动，不会再崩）'
foreach ($d in Get-NvDevices) { try { Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop } catch {} }
Start-Sleep -Seconds 5
foreach ($d in Get-NvDevices) { Write-Info ("现在：{0}  分类 {1}  状态 {2}" -f $d.FriendlyName, $d.Class, $d.Status) }

# ---------------------------------------------------------------------------
Write-Title '第 7 步：安装新 NVIDIA 驱动（清洁安装，约 5~10 分钟，窗口不动是正常的）'
$p = Start-Process -FilePath $file -ArgumentList '-s -clean -noreboot -noeula' -Wait -PassThru
Write-Info "安装程序结束，返回码 $($p.ExitCode)"
Start-Sleep -Seconds 5

# ---------------------------------------------------------------------------
Write-Title '第 8 步：检查结果'
$ok = $false
foreach ($d in Get-NvDevices) {
    $ver = ''; $prov = ''
    try { $ver = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverVersion -ErrorAction Stop).Data)" } catch {}
    try { $prov = "$((Get-PnpDeviceProperty -InstanceId $d.InstanceId -KeyName DEVPKEY_Device_DriverProvider -ErrorAction Stop).Data)" } catch {}
    Write-Info ("{0}  分类 {1}  状态 {2}  问题代码 {3}  驱动 {4} {5}" -f $d.FriendlyName, $d.Class, $d.Status, $d.ConfigManagerErrorCode, $prov, $ver)
    if ($d.Class -eq 'Display' -and $prov -match 'NVIDIA' -and $ver -and $ver -ne '24.21.13.9835') { $ok = $true }
}
if ($ok) {
    Write-Ok '新 NVIDIA 驱动已装上（问题代码 43 要重启后才能看出是否消失）'
} else {
    Write-Bad '新驱动没装上。如果装的时候出现安装界面，请按提示装完；仍不行就截图发给我。'
    $ans = Read-Host '  先把独显停用，避免继续蓝屏吗？输入 y 停用（推荐），直接回车不停用'
    if ($ans -match '^[yY]') { foreach ($d in Get-NvDevices) { Disable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }; Write-Ok '已停用独显' }
    Read-Host '按回车关闭' | Out-Null
    exit 0
}

Write-Info '重启后运行“驱动安装检查.bat”，把报告发给我。如果之后还蓝屏，就运行“停用独显并分析蓝屏.bat”停用独显。'
Write-Host ''
Write-Host '  60 秒后自动重启，按 N 取消。' -ForegroundColor Yellow
$cancel = $false
for ($i = 60; $i -gt 0; $i--) {
    Write-Host ("`r  {0,2} 秒后重启...（按 N 取消）" -f $i) -NoNewline
    for ($k = 0; $k -lt 5; $k++) {
        Start-Sleep -Milliseconds 200
        while ([Console]::KeyAvailable) { if (([Console]::ReadKey($true)).Key -eq 'N') { $cancel = $true } }
        if ($cancel) { break }
    }
    if ($cancel) { break }
}
Write-Host ''
if ($cancel) { Write-Ok '已取消自动重启，请稍后自己重启。'; Read-Host '按回车关闭' | Out-Null; exit 0 }
Restart-Computer -Force
