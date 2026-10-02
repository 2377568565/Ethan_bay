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
# 显卡驱动一键更新：Intel 核显 + NVIDIA MX150
# 流程：创建系统还原点 -> 从 Intel / NVIDIA 官网查最新版 -> 下载 -> 校验官方数字签名 -> 静默安装 -> 倒计时重启
# 下载地址都是运行时从官网实时查询的，不写死版本号。

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '显卡驱动一键更新' } catch {}
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

# 备用方案：从 Windows 更新（微软服务器）安装 NVIDIA 驱动，不经过 NVIDIA 的下载服务器
function Install-NvidiaFromWindowsUpdate {
    Write-Info '正在向 Windows 更新查询 NVIDIA 驱动（可能要 1~5 分钟）...'
    try {
        $session = New-Object -ComObject Microsoft.Update.Session
        $searcher = $session.CreateUpdateSearcher()
        $result = $searcher.Search("IsInstalled=0 and Type='Driver'")
        $coll = New-Object -ComObject Microsoft.Update.UpdateColl
        foreach ($u in $result.Updates) {
            if ($u.Title -match 'NVIDIA') { Write-Info "   找到：$($u.Title)"; [void]$coll.Add($u) }
        }
        if ($coll.Count -eq 0) { Write-Bad 'Windows 更新里没有可用的 NVIDIA 新驱动'; return $false }
        Write-Info '   正在下载...'
        $dl = $session.CreateUpdateDownloader(); $dl.Updates = $coll; [void]$dl.Download()
        Write-Info '   正在安装（屏幕可能会闪烁）...'
        $ins = $session.CreateUpdateInstaller(); $ins.Updates = $coll
        $r = $ins.Install()
        if ($r.ResultCode -eq 2 -or $r.ResultCode -eq 3) { Write-Ok '已通过 Windows 更新安装 NVIDIA 驱动'; return $true }
        Write-Bad "Windows 更新安装没成功（结果码 $($r.ResultCode)）"
    } catch {
        Write-Bad "Windows 更新查询失败：$($_.Exception.Message)"
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

# 判断装没装好以“驱动版本有没有变成新的”为准；安装程序的返回码各家不统一（Intel 装好了也可能返回 1000）
function Install-Package($file, $silentArgs, $name, $check) {
    Write-Info "正在安装 $name（大约 3~10 分钟，屏幕可能会闪烁）..."
    $p = Start-Process -FilePath $file -ArgumentList $silentArgs -Wait -PassThru
    Start-Sleep -Seconds 3
    if ($p.ExitCode -eq 0 -or $p.ExitCode -eq 3010 -or (& $check)) {
        Write-Ok "$name 安装完成（返回码 $($p.ExitCode)）"
        return $true
    }
    Write-Bad "$name 静默安装没成功（返回码 $($p.ExitCode)），改为打开安装界面，请按提示一路点“下一步”"
    Write-Host '       装完后点安装界面上的“完成”（不要点“立即重启”），本窗口会接着往下走。' -ForegroundColor Yellow
    $p = Start-Process -FilePath $file -Wait -PassThru
    Start-Sleep -Seconds 3
    return ($p.ExitCode -eq 0 -or $p.ExitCode -eq 3010 -or (& $check))
}

function Get-GpuVersion($pattern) {
    $g = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match $pattern } | Select-Object -First 1
    if ($g) { return "$($g.DriverVersion)" }
    return $null
}

$installed = @()

# ---------------------------------------------------------------------------
Write-Title '第 1 步：创建系统还原点（万一新驱动有问题可以退回）'
try {
    Enable-ComputerRestore -Drive "$env:SystemDrive\" -ErrorAction Stop
    # 默认 24 小时内只能建一个还原点，临时放开
    New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore' -Name SystemRestorePointCreationFrequency -Value 0 -PropertyType DWord -Force | Out-Null
    Checkpoint-Computer -Description '更新显卡驱动之前' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop
    Write-Ok '已创建还原点“更新显卡驱动之前”（出问题时：设置 -> 系统 -> 恢复 -> 高级启动 -> 系统还原）'
} catch {
    Write-Bad "还原点没创建成功：$($_.Exception.Message)"
    $ans = Read-Host '  没有还原点也继续安装吗？输入 y 继续，直接回车退出'
    if ($ans -notmatch '^[yY]') { exit 0 }
}

# ---------------------------------------------------------------------------
Write-Title '第 2 步：Intel 核显驱动'
$intelOld = Get-GpuVersion 'Intel'
if (-not $intelOld) {
    Write-Bad '没找到 Intel 核显，跳过'
} else {
    Write-Info "当前版本：$intelOld"
    $intelUrl = $null
    $intelVer = $null
    $pages = @(
        'https://www.intel.com/content/www/us/en/download/776137/intel-7th-10th-gen-processor-graphics-windows.html',
        'https://www.intel.cn/content/www/cn/zh/download/776137/intel-7th-10th-gen-processor-graphics-windows.html'
    )
    foreach ($pg in $pages) {
        try {
            $html = (Invoke-WebRequest -Uri $pg -UseBasicParsing -UserAgent $UA -TimeoutSec 60 -ErrorAction Stop).Content
            $ms = [regex]::Matches($html, 'https://downloadmirror\.intel\.com/\d+/gfx_win_101\.(\d+)\.exe')
            if ($ms.Count -gt 0) {
                $best = $ms | Sort-Object { [int]$_.Groups[1].Value } -Descending | Select-Object -First 1
                $intelUrl = $best.Value
                $intelVer = "31.0.101.$($best.Groups[1].Value)"
                break
            }
        } catch {}
    }
    if (-not $intelUrl) {
        # 官网页面读取失败时的备用地址（2026 年 9 月发布的版本）
        $intelUrl = 'https://downloadmirror.intel.com/929187/gfx_win_101.2145.exe'
        $intelVer = '31.0.101.2145'
        Write-Bad '没能从 Intel 官网页面读到最新地址，使用备用地址'
    }
    Write-Info "最新版本：$intelVer"
    $skip = $false
    try { if ([version]$intelOld -ge [version]$intelVer) { $skip = $true } } catch {}
    if ($skip) {
        Write-Ok '已经是最新版，跳过'
    } else {
        $file = Join-Path $WorkDir ([IO.Path]::GetFileName($intelUrl))
        if (Get-Download @($intelUrl) $file) {
            if (Test-Signed $file 'Intel') {
                if (Install-Package $file '-s' 'Intel 核显驱动' { $v = Get-GpuVersion 'Intel'; $v -and $v -ne $intelOld }) { $installed += 'Intel 核显驱动' }
            }
        } else {
            Write-Bad 'Intel 驱动下载失败。可以手动打开下面的网页下载安装：'
            Write-Info "   $($pages[1])"
        }
    }
}

# ---------------------------------------------------------------------------
Write-Title '第 3 步：NVIDIA MX150 驱动'
$nvOld = Get-GpuVersion 'NVIDIA'
if (-not $nvOld) {
    Write-Bad '没找到 NVIDIA 显卡，跳过'
} else {
    # Windows 驱动版本 24.21.13.9835 的最后 5 位就是 NVIDIA 版本 398.35
    $digits = ($nvOld -replace '\D', '')
    $nvOldShort = ''
    if ($digits.Length -ge 5) { $tail = $digits.Substring($digits.Length - 5); $nvOldShort = '{0}.{1}' -f [int]$tail.Substring(0, 3), $tail.Substring(3) }
    Write-Info "当前版本：$nvOldShort（$nvOld）"

    # 用 NVIDIA 官网驱动查询接口：853 = GeForce MX150（笔记本），osID 135 = Win11，57 = Win10 64 位
    $nvUrl = $null
    $nvVer = $null
    foreach ($apiHost in 'gfwsl.geforce.com', 'gfwsl.geforce.cn') {
        foreach ($osId in 135, 57) {
            try {
                $api = "https://$apiHost/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&pfid=853&osID=$osId&languageCode=2052&dch=1&isWHQL=1&beta=0&numberOfResults=1"
                $j = Invoke-RestMethod -Uri $api -UserAgent $UA -TimeoutSec 60 -ErrorAction Stop
                if ($j.Success -eq '1' -and $j.IDS) {
                    $info = $j.IDS[0].downloadInfo
                    $nvUrl = [Uri]::UnescapeDataString("$($info.DownloadURL)")
                    $nvVer = "$($info.Version)"
                    break
                }
            } catch {}
        }
        if ($nvUrl) { break }
    }
    if (-not $nvUrl) {
        Write-Bad '没能连上 NVIDIA 官网查询最新驱动。请手动打开 https://www.nvidia.cn/drivers/ 选 GeForce MX150 下载安装'
    } else {
        Write-Info "最新版本：$nvVer"
        $skip = $false
        try { if ($nvOldShort -and [version]$nvOldShort -ge [version]$nvVer) { $skip = $true } } catch {}
        if ($skip) {
            Write-Ok '已经是最新版，跳过'
        } else {
            $file = Join-Path $WorkDir ([IO.Path]::GetFileName(([Uri]$nvUrl).AbsolutePath))
            # 同一个文件在 NVIDIA 几个官方下载服务器上都有；每个地址都会先直连（绕过 clash 等代理）再走代理
            $path = ([Uri]$nvUrl).AbsolutePath
            $mirrors = @('cn.download.nvidia.com', 'us.download.nvidia.com', 'international.download.nvidia.com') |
                ForEach-Object { "https://$_$path" }
            if (Get-Download $mirrors $file) {
                if (Test-Signed $file 'NVIDIA') {
                    # -s 静默，-clean 清洁安装（清掉旧驱动的残留设置），-noreboot 最后统一重启
                    if (Install-Package $file '-s -clean -noreboot -noeula' 'NVIDIA 显卡驱动' { $v = Get-GpuVersion 'NVIDIA'; $v -and $v -ne $nvOld }) { $installed += 'NVIDIA 显卡驱动' }
                }
            } else {
                Write-Bad 'NVIDIA 官网所有下载地址都失败了，改用 Windows 更新安装 NVIDIA 驱动'
                if (Install-NvidiaFromWindowsUpdate) {
                    $installed += 'NVIDIA 显卡驱动（来自 Windows 更新）'
                } else {
                    Write-Bad '都没成功。请彻底退出 clash（右键托盘图标 -> 退出，TUN 模式也要关）后再运行一次；'
                    Write-Info "   或者用浏览器打开这个地址手动下载：https://us.download.nvidia.com$path"
                }
            }
        }
    }
}

# ---------------------------------------------------------------------------
Write-Title '结果'
if ($installed.Count -eq 0) {
    Write-Info '这次没有安装任何驱动，不需要重启。'
    Read-Host '按回车关闭' | Out-Null
    exit 0
}
Write-Ok ("已安装：{0}" -f ($installed -join '、'))
Write-Info '重启之后新驱动才会完全生效。重启后可以再运行一次“黑屏深度诊断.bat”，看 MX150 的错误代码 43 还在不在。'
Write-Info '安装包在 %TEMP%\DriverUpdate，确认没问题后可以删掉。'
Write-Host ''
Write-Host '  60 秒后自动重启。请先保存好正在编辑的文件。按 N 键取消重启。' -ForegroundColor Yellow
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
if ($cancel) {
    Write-Ok '已取消自动重启，请稍后自己重启一次。'
    Read-Host '按回车关闭' | Out-Null
    exit 0
}
Restart-Computer -Force
