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
function Get-Download($urls, $dest) {
    foreach ($u in $urls) {
        if (-not $u) { continue }
        Write-Info "下载：$u"
        Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
        try {
            Start-BitsTransfer -Source $u -Destination $dest -DisplayName '下载显卡驱动' -ErrorAction Stop
            if ((Test-Path -LiteralPath $dest) -and (Get-Item -LiteralPath $dest).Length -gt 10MB) { return $true }
        } catch {}
        try {
            Invoke-WebRequest -Uri $u -OutFile $dest -UseBasicParsing -UserAgent $UA -TimeoutSec 3600 -ErrorAction Stop
            if ((Test-Path -LiteralPath $dest) -and (Get-Item -LiteralPath $dest).Length -gt 10MB) { return $true }
        } catch {
            Write-Bad "这个地址下载失败：$($_.Exception.Message)"
        }
    }
    return $false
}

# 只安装带有效官方签名的文件
function Test-Signed($file, $vendorPattern) {
    $sig = Get-AuthenticodeSignature -LiteralPath $file
    $subject = "$($sig.SignerCertificate.Subject)"
    if ($sig.Status -eq 'Valid' -and $subject -match $vendorPattern) {
        Write-Ok "数字签名校验通过：$(($subject -split ',')[0])"
        return $true
    }
    Write-Bad "数字签名校验没通过（$($sig.Status) / $subject），为了安全不安装这个文件"
    return $false
}

function Install-Package($file, $silentArgs, $name) {
    Write-Info "正在安装 $name（大约 3~10 分钟，屏幕可能会闪烁）..."
    $p = Start-Process -FilePath $file -ArgumentList $silentArgs -Wait -PassThru
    if ($p.ExitCode -eq 0 -or $p.ExitCode -eq 3010) {
        Write-Ok "$name 安装完成（返回码 $($p.ExitCode)）"
        return $true
    }
    Write-Bad "$name 静默安装没成功（返回码 $($p.ExitCode)），改为打开安装界面，请按提示一路点“下一步”"
    $p = Start-Process -FilePath $file -Wait -PassThru
    return ($p.ExitCode -eq 0 -or $p.ExitCode -eq 3010)
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
                if (Install-Package $file '-s' 'Intel 核显驱动') { $installed += 'Intel 核显驱动' }
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
            $alt = $nvUrl -replace '://us\.download\.nvidia\.com', '://cn.download.nvidia.com'
            if (Get-Download @($nvUrl, $alt) $file) {
                if (Test-Signed $file 'NVIDIA') {
                    # -s 静默，-clean 清洁安装（清掉旧驱动的残留设置），-noreboot 最后统一重启
                    if (Install-Package $file '-s -clean -noreboot -noeula' 'NVIDIA 显卡驱动') { $installed += 'NVIDIA 显卡驱动' }
                }
            } else {
                Write-Bad 'NVIDIA 驱动下载失败。请手动打开 https://www.nvidia.cn/drivers/ 选 GeForce MX150 下载安装'
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
