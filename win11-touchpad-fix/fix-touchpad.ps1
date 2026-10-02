# 笔记本触摸板失灵 一键修复脚本（Win10 / Win11）
# 用法: 双击同目录下的 fix-touchpad.bat（会自动请求管理员权限）

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Bad($msg)  { Write-Host "    [!]  $msg" -ForegroundColor Yellow }
function Write-Info($msg) { Write-Host "    $msg" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限：请双击 fix-touchpad.bat 运行。'
    exit 1
}

# 触摸板常见的名字 / 硬件 ID（I2C HID、精确式触摸板、ELAN、Synaptics、FocalTech 等）
$pattern = 'touch ?pad|触摸板|I2C HID|Precision|ELAN|Synaptics|SYNA|FocalTech|FTE\d|Goodix|MSFT0001'

# ---------------------------------------------------------------------------
Write-Step '1/4 查找触摸板设备'
$tp = @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue |
    Where-Object { "$($_.FriendlyName) $($_.InstanceId)" -match $pattern })
if ($tp.Count -eq 0) {
    Write-Bad '没有找到触摸板设备 —— 多半是缺驱动（见第 2 步）'
} else {
    foreach ($d in $tp) {
        $name = $d.FriendlyName
        if (-not $name) { $name = $d.InstanceId }
        if ($d.ConfigManagerErrorCode -eq 22) {
            try {
                Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop
                Write-Ok "$name 之前被禁用了，已重新启用"
            } catch {
                Write-Bad "$name 被禁用了，启用失败：$($_.Exception.Message)"
            }
        } elseif ($d.Status -eq 'OK') {
            pnputil.exe /restart-device "$($d.InstanceId)" | Out-Null
            Write-Ok "$name 正常，已重启该设备"
        } else {
            Write-Bad "$name 状态异常（$($d.Status)，错误代码 $($d.ConfigManagerErrorCode)）"
        }
    }
}

# ---------------------------------------------------------------------------
Write-Step '2/4 检查缺失的驱动'
$err = @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Error' -and $_.ConfigManagerErrorCode -ne 22 })
# Intel 串行 IO（I2C 控制器）：笔记本触摸板基本都挂在它下面，重装系统后最容易缺
$serial = @($err | Where-Object { $_.InstanceId -match '^ACPI\\(INT34|INT33|INTC)' -or "$($_.FriendlyName)" -match 'Serial IO|I2C|串行' })
$needDriver = $false
if ($serial.Count -gt 0) {
    Write-Bad '缺少 Intel 串行 IO（I2C）驱动 —— 触摸板就靠它工作，这很可能就是原因！'
    $needDriver = $true
}
if ($err.Count -gt 0) {
    Write-Info "共有 $($err.Count) 个设备没有驱动或出错："
    foreach ($d in $err) {
        $n = $d.FriendlyName
        if (-not $n) { $n = $d.InstanceId }
        Write-Info "   - $n"
    }
    $needDriver = $true
} else {
    Write-Ok '没有发现缺驱动的设备'
}

# ---------------------------------------------------------------------------
Write-Step '3/4 重新扫描硬件'
pnputil.exe /scan-devices | Out-Null
Start-Sleep -Seconds 3
Write-Ok '扫描完成'

# ---------------------------------------------------------------------------
Write-Step '4/4 检查系统设置里的触摸板开关'
$k = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\PrecisionTouchPad\Status'
$en = $null
try { $en = (Get-ItemProperty -Path $k -Name Enabled -ErrorAction Stop).Enabled } catch {}
if ($en -eq 0) {
    Write-Bad '触摸板在系统设置里被关掉了！马上为你打开设置页面，把「触摸板」开关打开即可'
} else {
    Write-Info '为你打开触摸板设置页面，请确认：'
}
Write-Info '   1) 最上面的「触摸板」开关是「开」'
Write-Info '   2) 展开它，勾选「连接鼠标时让触摸板保持打开状态」（不勾的话插着鼠标触摸板会自动失效）'
Start-Process 'ms-settings:devices-touchpad'

if ($needDriver) {
    Write-Host "`n下一步：安装缺失的驱动" -ForegroundColor Yellow
    Write-Info '方法 1：设置 -> Windows 更新 -> 高级选项 -> 可选更新 -> 驱动程序更新，全部勾上安装，然后重启'
    Write-Info '方法 2：去机械革命官网「服务支持」，按型号下载「芯片组 / Serial IO / 触摸板」驱动安装'
    Write-Info '方法 3：用 Intel 官方的「英特尔驱动程序和支持助理」自动检测安装'
    try { Start-Process 'ms-settings:windowsupdate-optionalupdates' } catch {}
}

Write-Host "`n如果还是不能用：" -ForegroundColor Cyan
Write-Info '- 按一下 Fn + 印着触摸板图标的 F 键（很多笔记本是 Fn+F1），它可能被快捷键关掉了'
Write-Info '- 重启一次电脑（装完驱动后必须重启）'
