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
# 黑屏诊断：开机黑屏 / 合盖睡眠后唤醒黑屏 / 放着不动屏幕黑了后唤不醒，只能强制关机
# 只读取系统日志和硬件信息；最后的几个修复项都会先问你，不同意就不改。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '黑屏诊断' } catch {}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '需要管理员权限，请双击 bat 文件并在弹窗里点“是”。' -ForegroundColor Yellow
    exit 1
}

# 屏幕输出的同时记进报告
$report = New-Object System.Collections.Generic.List[string]
$findings = New-Object System.Collections.Generic.List[string]
function Out-Line($text, $color) {
    if (-not $color) { $color = 'White' }
    Write-Host $text -ForegroundColor $color
    $report.Add($text)
}
function Out-Title($m) { Out-Line ''; Out-Line "==== $m ====" 'Cyan' }
function Out-Ok($m)    { Out-Line "  [正常] $m" 'Green' }
function Out-Bad($m)   { Out-Line "  [注意] $m" 'Yellow' }
function Out-Info($m)  { Out-Line "  $m" 'White' }

$Days = 30
$since = (Get-Date).AddDays(-$Days)

function Get-SysEvents($provider, $ids) {
    $f = @{ LogName = 'System'; StartTime = $since; ProviderName = $provider }
    if ($ids) { $f.Id = $ids }
    # 日志来源不存在时 Get-WinEvent 会直接报错（The parameter is incorrect），这里吞掉
    try { return @(Get-WinEvent -FilterHashtable $f -ErrorAction Stop) } catch { return @() }
}

function Get-EventField($e, $name) {
    try {
        $x = [xml]$e.ToXml()
        $d = $x.Event.EventData.Data | Where-Object { $_.Name -eq $name }
        if ($d) { return "$($d.'#text')" }
    } catch {}
    return ''
}

function Get-PowerValue($sub, $alias) {
    $out = (powercfg /q SCHEME_CURRENT $sub $alias 2>$null) -join "`n"
    $m = [regex]::Matches($out, '0x([0-9a-fA-F]{8})')
    if ($m.Count -ge 2) {
        return @{ AC = [Convert]::ToInt32($m[$m.Count - 2].Groups[1].Value, 16)
                  DC = [Convert]::ToInt32($m[$m.Count - 1].Groups[1].Value, 16) }
    }
    return $null
}

Out-Line "黑屏诊断报告    生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm')    统计范围：最近 $Days 天" 'Cyan'

# ---------------------------------------------------------------------------
Out-Title '1. 电脑基本信息'
$cs = Get-CimInstance Win32_ComputerSystem
$bios = Get-CimInstance Win32_BIOS
$os = Get-CimInstance Win32_OperatingSystem
Out-Info "型号：$($cs.Manufacturer) $($cs.Model)"
Out-Info "系统：$($os.Caption) $($os.Version)"
$biosDate = $bios.ReleaseDate
Out-Info ("BIOS：{0}  日期：{1}" -f $bios.SMBIOSBIOSVersion, $(if ($biosDate) { $biosDate.ToString('yyyy-MM-dd') } else { '未知' }))
if ($biosDate -and $biosDate -lt (Get-Date '2020-01-01')) {
    Out-Bad 'BIOS 比较旧，新版 BIOS 常会修复“睡眠唤醒黑屏”这类问题，可以去官网查有没有更新'
    $findings.Add('BIOS 较旧：去官网查有没有新版 BIOS（刷 BIOS 时必须插着电源，过程中不能断电）')
}

# ---------------------------------------------------------------------------
Out-Title '2. 强制关机 / 意外断电记录（每次你长按电源键都会留一条）'
$kp41 = Get-SysEvents 'Microsoft-Windows-Kernel-Power' 41
$cntSleep = 0; $cntBsod = 0; $cntHang = 0
if ($kp41.Count -eq 0) {
    Out-Ok '最近没有强制关机记录'
} else {
    Out-Info '（记录时间是“下一次开机”的时间，不是黑屏发生的时间）'
    foreach ($e in ($kp41 | Sort-Object TimeCreated)) {
        $sleep = Get-EventField $e 'SleepInProgress'
        $cs0 = Get-EventField $e 'ConnectedStandbyInProgress'
        $bug = Get-EventField $e 'BugcheckCode'
        $btn = Get-EventField $e 'PowerButtonTimestamp'
        $inSleep = ($sleep -and $sleep -ne '0' -and $sleep -ne 'false') -or ($cs0 -eq 'true')
        if ($bug -and $bug -ne '0') {
            $cntBsod++
            $kind = '蓝屏死机（错误码 0x{0:X}）' -f [int64]$bug
        } elseif ($inSleep) {
            $cntSleep++
            $kind = '睡眠中 / 唤醒过程中卡死'
        } else {
            $cntHang++
            $kind = '开机或使用过程中卡死'
        }
        if ($btn -and $btn -ne '0') { $kind += '，长按了电源键' }
        Out-Info ("{0:yyyy-MM-dd HH:mm}   {1}" -f $e.TimeCreated, $kind)
    }
    Out-Info ''
    Out-Info "合计 $($kp41.Count) 次：睡眠/唤醒中卡死 $cntSleep 次，开机或使用中卡死 $cntHang 次，蓝屏 $cntBsod 次"
}

# ---------------------------------------------------------------------------
Out-Title '3. 睡眠和唤醒'
$sleeps = Get-SysEvents 'Microsoft-Windows-Kernel-Power' 42
$resumes = Get-SysEvents 'Microsoft-Windows-Power-Troubleshooter' 1
Out-Info "进入睡眠 $($sleeps.Count) 次，成功唤醒 $($resumes.Count) 次"
if ($sleeps.Count -gt $resumes.Count) {
    Out-Bad ("有 {0} 次进入睡眠后没有成功唤醒" -f ($sleeps.Count - $resumes.Count))
}
$pa = @(powercfg /a 2>$null)
Out-Info '这台电脑支持的睡眠方式（powercfg /a）：'
foreach ($l in ($pa | Select-Object -First 12)) { if ("$l".Trim()) { Out-Info "    $("$l".Trim())" } }
$fast = $null
try { $fast = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled -ErrorAction Stop).HiberbootEnabled } catch {}
if ($fast -eq 1) {
    Out-Bad '“快速启动”是开着的 —— 它会让开机变成“从休眠恢复”，驱动有问题时很容易开机黑屏'
} else {
    Out-Ok '“快速启动”已关闭'
}
$lid = Get-PowerValue 'SUB_BUTTONS' 'LIDACTION'
$lidName = @{ 0 = '不采取任何操作'; 1 = '睡眠'; 2 = '休眠'; 3 = '关机' }
if ($lid) { Out-Info ("合盖时：插电 = {0}，用电池 = {1}" -f $lidName[$lid.AC], $lidName[$lid.DC]) }

# 放着不动时：多久关屏幕、多久睡眠、屏幕保护
function Format-Idle($sec) { if (-not $sec) { return '从不' } ; if ($sec -lt 60) { return "$sec 秒" } ; return ('{0} 分钟' -f [math]::Round($sec / 60)) }
$vid = Get-PowerValue 'SUB_VIDEO' 'VIDEOIDLE'
$slp = Get-PowerValue 'SUB_SLEEP' 'STANDBYIDLE'
if ($vid) { Out-Info ("放着不动多久关屏幕：插电 {0}，用电池 {1}" -f (Format-Idle $vid.AC), (Format-Idle $vid.DC)) }
if ($slp) { Out-Info ("放着不动多久自动睡眠：插电 {0}，用电池 {1}" -f (Format-Idle $slp.AC), (Format-Idle $slp.DC)) }
$ss = $null
try { $ss = Get-ItemProperty 'HKCU:\Control Panel\Desktop' -ErrorAction Stop } catch {}
$ssOn = $ss -and "$($ss.ScreenSaveActive)" -eq '1' -and "$($ss.'SCRNSAVE.EXE')"
if ($ssOn) {
    Out-Info ("屏幕保护：开启（{0}，{1}）" -f [IO.Path]::GetFileName("$($ss.'SCRNSAVE.EXE')"), (Format-Idle ([int]$ss.ScreenSaveTimeOut)))
} else {
    Out-Info '屏幕保护：未开启（你看到的“变黑”是系统关屏幕或自动睡眠）'
}
$idleSleeps = Get-SysEvents 'Microsoft-Windows-Kernel-Power' @(506, 507)
if ($idleSleeps.Count -gt 0) { Out-Info "现代待机（屏幕关闭后的低功耗状态）进入/退出记录 $($idleSleeps.Count) 条" }

# ---------------------------------------------------------------------------
Out-Title '4. 显卡和驱动'
$gpus = @(Get-CimInstance Win32_VideoController)
foreach ($g in $gpus) {
    $dd = $g.DriverDate
    $ddText = '未知'
    if ($dd) { $ddText = $dd.ToString('yyyy-MM-dd') }
    Out-Info ("{0}   驱动 {1}（{2}）" -f $g.Name, $g.DriverVersion, $ddText)
    if ($g.Name -match 'Basic|基本') {
        Out-Bad '这是 Windows 的“基本显示适配器”，说明显卡驱动没装上！'
        $findings.Add('显卡驱动没装：设置 -> Windows 更新 -> 高级选项 -> 可选更新，或去官网下载 Intel 核显驱动')
    } elseif ($g.ConfigManagerErrorCode -and $g.ConfigManagerErrorCode -ne 0) {
        Out-Bad "这块显卡状态异常（错误代码 $($g.ConfigManagerErrorCode)）"
        $findings.Add("显卡 $($g.Name) 有错误，需要重装驱动")
    } elseif ($dd -and $dd -lt (Get-Date '2021-01-01')) {
        Out-Bad '驱动比较旧，旧的 Intel 核显驱动常见“唤醒后黑屏”问题'
    }
}
$tdr = Get-SysEvents 'Display' 4101
$nv = Get-SysEvents 'nvlddmkm' $null
$ig = @()
foreach ($p in 'igfx', 'igfxn', 'igfxnd') { $ig += Get-SysEvents $p $null }
if ($tdr.Count + $nv.Count + $ig.Count -eq 0) {
    Out-Ok '没有显卡驱动崩溃记录'
} else {
    Out-Bad ("显卡驱动出错：画面卡死后恢复 {0} 次，NVIDIA 驱动报错 {1} 次，Intel 驱动报错 {2} 次" -f $tdr.Count, $nv.Count, $ig.Count)
    $findings.Add('显卡驱动不稳定：重装 Intel 核显驱动 + NVIDIA 驱动（官网下载最新版）')
}

# ---------------------------------------------------------------------------
Out-Title '5. 内存条（8G 换成了 16G，这里重点看）'
$mods = @(Get-CimInstance Win32_PhysicalMemory)
foreach ($m in $mods) {
    $speed = $m.ConfiguredClockSpeed
    if (-not $speed) { $speed = $m.Speed }
    Out-Info ("{0}：{1} GB  标称 {2} MHz，实际运行 {3} MHz  {4} {5}" -f $m.DeviceLocator, [math]::Round($m.Capacity / 1GB), $m.Speed, $speed, "$($m.Manufacturer)".Trim(), "$($m.PartNumber)".Trim())
}
if ($mods.Count -eq 1) {
    Out-Info '这台电脑只有一个内存插槽，你把原来的 8G 换成了 16G。'
    Out-Info '“通电了、键盘灯亮了但屏幕不亮、连 LOGO 都没有”，是内存条兼容性不好的典型表现：'
    Out-Info '开机时主板要先“认”内存条，认不好就卡在这一步，画面出不来。'
    $findings.Add('重点怀疑新换的 16G 内存条：做内存检测（下面可一键启动）；最直接的验证是换回原来的 8G 用几天，黑屏不再出现就是新内存条的问题，找卖家换一根兼容性好的（DDR4 2400/2666，单根 16G）')
}
$memDiag = @()
try { $memDiag = @(Get-WinEvent -FilterHashtable @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-MemoryDiagnostics-Results' } -MaxEvents 1 -ErrorAction Stop) } catch {}
if ($memDiag.Count -gt 0) {
    Out-Info ("上次内存检测（{0:yyyy-MM-dd}）：{1}" -f $memDiag[0].TimeCreated, ($memDiag[0].Message -split "`n")[0])
} else {
    Out-Info '还没有做过 Windows 内存检测'
}

# ---------------------------------------------------------------------------
Out-Title '6. 硬件错误和蓝屏'
$whea = Get-SysEvents 'Microsoft-Windows-WHEA-Logger' $null
if ($whea.Count -gt 0) {
    Out-Bad "有 $($whea.Count) 条硬件错误（WHEA）记录 —— 通常指向内存、CPU 或主板"
    $findings.Add('有硬件错误记录：优先做内存检测，问题持续建议送修检查')
} else {
    Out-Ok '没有硬件错误记录'
}
$dumps = @(Get-ChildItem -LiteralPath (Join-Path $env:WINDIR 'Minidump') -Filter *.dmp -ErrorAction SilentlyContinue)
if ($dumps.Count -gt 0) {
    Out-Bad "有 $($dumps.Count) 个蓝屏转储文件（C:\Windows\Minidump），最近一次：$(($dumps | Sort-Object LastWriteTime -Descending)[0].LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
} else {
    Out-Ok '没有蓝屏转储文件'
}
$diskErr = @()
$diskErr += Get-SysEvents 'disk' @(7, 11, 51, 153)
$diskErr += Get-SysEvents 'Ntfs' @(55)
$diskErr += Get-SysEvents 'stornvme' @(11, 129)
$diskErr += Get-SysEvents 'storahci' @(129)
if ($diskErr.Count -gt 0) {
    Out-Bad "有 $($diskErr.Count) 条硬盘读写错误/超时记录 —— 硬盘卡住时也会表现为黑屏不动"
    $findings.Add('硬盘有错误记录：尽快备份重要资料，用 CrystalDiskInfo 看硬盘健康度')
} else {
    Out-Ok '没有硬盘错误记录'
}

# ---------------------------------------------------------------------------
Out-Title '诊断结论'
if ($cntSleep -gt 0 -and $cntSleep -ge $cntHang) {
    $findings.Insert(0, '主要问题是“睡眠后唤醒失败”：多半是 Intel 核显驱动 / 芯片组驱动 / BIOS 与睡眠不兼容。先更新这三样；在修好之前，把合盖改成“休眠”可以绕开（下面可以一键设置）')
}
if ($cntHang -gt 0) {
    $findings.Add('有开机或使用中卡死的记录：如果开机时连品牌 LOGO 都不出现，就是 Windows 启动之前的问题（最常见是内存条，其次是 BIOS）；如果 LOGO 出现过再黑，多半是显卡驱动 + 快速启动')
}
# 放着不动黑屏后唤不醒
$idleSleepOn = $slp -and ($slp.AC -gt 0 -or $slp.DC -gt 0)
if ($idleSleepOn) {
    $findings.Add('“放着不动黑了就唤不醒”：这台电脑设置了放一会儿就自动睡眠，所以这和“合盖睡眠唤醒黑屏”很可能是同一个问题——唤醒失败。修好唤醒（驱动/BIOS/内存）就都好了；临时办法是插电时不自动睡眠（下面可一键设置）')
} else {
    $findings.Add('“放着不动黑了就唤不醒”：这台电脑不会自动睡眠，变黑只是关闭了屏幕，这时唤不醒基本是 Intel 核显驱动的问题。更新 Intel 核显驱动；并在“英特尔显卡控制中心 -> 系统/电源”里关闭“面板自刷新（Panel Self-Refresh）”')
}
if ($fast -eq 1) {
    $findings.Add('建议关闭“快速启动”（下面可以一键关闭），这是 Win10/11 开机黑屏最常见的诱因之一')
}
if ($findings.Count -eq 0) {
    Out-Ok '日志里没有发现明显问题。下次黑屏时请按下面“黑屏时自测”的方法试一下，再运行一次本诊断。'
} else {
    $i = 0
    foreach ($f in $findings) { $i++; Out-Line "  $i. $f" 'Yellow' }
}

Out-Title '黑屏时自测（下次黑屏时，强制关机之前按顺序试）'
Out-Info '1. 按一下 Caps Lock：大写指示灯能亮能灭 = 系统其实没死机，只是屏幕没画面'
Out-Info '2. 同时按 Win + Ctrl + Shift + B（重启显卡驱动，会“嘀”一声）：画面回来了 = 显卡驱动问题'
Out-Info '3. 按 Fn + 亮度加 几下：画面出来了 = 只是背光被关到最暗'
Out-Info '4. 插一根 HDMI 线接电视/显示器：外接屏有画面 = 笔记本屏幕或屏线的问题（硬件，需要送修）'
Out-Info '5. 开机时注意：连品牌 LOGO 都不出现就黑 = Windows 之前就卡住了，重点怀疑新换的 16G 内存条'
Out-Info '6. 另外回忆一下：黑屏是换内存条之前就有，还是换了之后才开始的？这一点很关键'

# 保存报告
$desktop = [Environment]::GetFolderPath('Desktop')
$reportPath = Join-Path $desktop '黑屏诊断报告.txt'
try {
    $report | Out-File -LiteralPath $reportPath -Encoding UTF8
    Write-Host "`n报告已保存到桌面：黑屏诊断报告.txt（可以发给我帮你看）" -ForegroundColor Green
} catch {}

# ---------------------------------------------------------------------------
Write-Host "`n==== 可选修复（每一项都会先问你） ====" -ForegroundColor Cyan
if ($fast -eq 1) {
    $ans = Read-Host '  关闭“快速启动”？开机会慢几秒，但能避免很多开机黑屏。输入 y 回车，直接回车跳过'
    if ($ans -match '^[yY]') {
        Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled -Value 0 -Type DWord
        Write-Host '  [OK] 已关闭快速启动' -ForegroundColor Green
    }
}
if ($cntSleep -gt 0 -and $lid -and ($lid.AC -eq 1 -or $lid.DC -eq 1)) {
    $ans = Read-Host '  把“合盖”从睡眠改成休眠？休眠更稳定（唤醒要多等 10 秒左右），可以绕开唤醒黑屏。输入 y 回车，直接回车跳过'
    if ($ans -match '^[yY]') {
        powercfg /hibernate on | Out-Null
        powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 2 | Out-Null
        powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 2 | Out-Null
        powercfg /setactive SCHEME_CURRENT | Out-Null
        Write-Host '  [OK] 合盖已改为休眠（想改回：设置 -> 系统 -> 电源 -> 盖子和电源按钮）' -ForegroundColor Green
    }
}
if ($slp -and $slp.AC -gt 0) {
    $ans = Read-Host '  插电时“放着不动”改成只关屏幕、不自动睡眠？可以绕开唤醒黑屏，也能帮你判断问题出在睡眠还是关屏。输入 y 回车，直接回车跳过'
    if ($ans -match '^[yY]') {
        powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 0 | Out-Null
        powercfg /setactive SCHEME_CURRENT | Out-Null
        Write-Host '  [OK] 插电时不再自动睡眠（想改回：设置 -> 系统 -> 电源 -> 屏幕和睡眠）' -ForegroundColor Green
        Write-Host '       之后如果放着不动黑屏后还是唤不醒 = 关屏幕本身有问题（显卡驱动）；不再出现 = 问题在睡眠唤醒' -ForegroundColor Green
    }
}
$ans = Read-Host '  运行 Windows 内存检测？会弹出窗口让你选“立即重启并检查”，检测约 10~20 分钟。输入 y 回车，直接回车跳过'
if ($ans -match '^[yY]') {
    Start-Process mdsched.exe
    Write-Host '  检测完重启进系统后，再运行一次本诊断，第 5 部分会显示检测结果。' -ForegroundColor Green
}

Write-Host ''
Read-Host '按回车关闭' | Out-Null
exit 0
