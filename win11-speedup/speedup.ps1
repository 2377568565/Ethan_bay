# 电脑卡顿急救 / 降温 / 体检 脚本（Win10 / Win11）
# 用法: 双击同目录下的 speedup.bat（会自动请求管理员权限）
# 原则: 不改注册表、不永久关闭任何系统服务、不碰系统进程；所有改动都能一键恢复。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '电脑卡顿急救' } catch {}

function Write-Title($m) { Write-Host "`n==== $m ====" -ForegroundColor Cyan }
function Write-Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)   { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m)  { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限：请双击 speedup.bat 运行。'
    Read-Host '按回车退出' | Out-Null
    exit 1
}

$Cores = [Environment]::ProcessorCount

# 常见进程的中文说明
$Explain = @{
    'msmpeng'               = 'Windows 自带杀毒在扫描（新系统前几天常见，会自己停）'
    'mpdefendercoreservice' = 'Windows 自带杀毒'
    'tiworker'              = 'Windows 更新在安装（别打断，装完就好）'
    'trustedinstaller'      = 'Windows 更新在安装（别打断，装完就好）'
    'mousocoreworker'       = 'Windows 更新在检查/下载'
    'searchindexer'         = '系统搜索在建索引（新系统前几天常见）'
    'searchprotocolhost'    = '系统搜索在建索引'
    'searchfilterhost'      = '系统搜索在建索引'
    'compattelrunner'       = '微软兼容性检测，跑完会自己结束'
    'svchost'               = '系统服务'
    'dwm'                   = '桌面窗口显示'
    'system'                = '系统内核/驱动'
    'memory compression'    = '内存压缩（内存紧张时会升高）'
    'explorer'              = '资源管理器/任务栏'
    'chrome'                = 'Chrome 浏览器（标签页越多越吃资源）'
    'msedge'                = 'Edge 浏览器（标签页越多越吃资源）'
    'msedgewebview2'        = '网页组件（很多软件内置）'
    'wmiprvse'              = '系统管理组件'
    'audiodg'               = '系统声音'
    'powershell'            = '本脚本自身'
    'qqpcrtp'               = '腾讯电脑管家实时防护（在扫描文件）'
    'qqpctray'              = '腾讯电脑管家'
}

# 这些进程绝不提供「结束」选项
$ProtectedNames = @(
    'system', 'idle', 'registry', 'memory compression', 'smss', 'csrss', 'wininit', 'winlogon',
    'services', 'lsass', 'lsaiso', 'svchost', 'dwm', 'explorer', 'fontdrvhost', 'sihost', 'ctfmon',
    'audiodg', 'spoolsv', 'msmpeng', 'mpdefendercoreservice', 'nissrv', 'securityhealthservice',
    'searchindexer', 'tiworker', 'trustedinstaller', 'mousocoreworker', 'powershell', 'conhost',
    'cmd', 'wmiprvse', 'runtimebroker', 'taskhostw', 'startmenuexperiencehost',
    'shellexperiencehost', 'searchhost', 'textinputhost', 'wudfhost', 'dllhost'
)

function Test-Protected($name, $id) {
    if ($ProtectedNames -contains $name.ToLower()) { return $true }
    $p = Get-Process -Id $id -ErrorAction SilentlyContinue
    if (-not $p) { return $true }
    $path = $null
    try { $path = $p.Path } catch {}
    if (-not $path) { return $true }                         # 读不到路径的一般是受保护的系统进程
    if ($path -like "$env:WINDIR\*") { return $true }        # C:\Windows 下的都算系统组件
    if ($path -match '\\Windows Defender\\') { return $true }
    return $false
}

# ---------------------------------------------------------------------------
# 采样：整体 CPU / 内存 / 硬盘 + 各进程占用
# ---------------------------------------------------------------------------
function Get-Snapshot {
    # 性能计数器需要两次采样才有准确值
    $null = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process -ErrorAction SilentlyContinue
    $null = Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -ErrorAction SilentlyContinue
    $null = Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk -ErrorAction SilentlyContinue
    $null = Get-CimInstance Win32_PerfFormattedData_Counters_ProcessorInformation -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    $s = @{}
    $cpu = Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'" -ErrorAction SilentlyContinue
    $s.Cpu = if ($cpu) { [int]$cpu.PercentProcessorTime } else { -1 }

    $os = Get-CimInstance Win32_OperatingSystem
    $s.MemTotalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
    $s.Mem = [int][math]::Round((1 - $os.FreePhysicalMemory / $os.TotalVisibleMemorySize) * 100)

    $disk = Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk -Filter "Name='_Total'" -ErrorAction SilentlyContinue
    $s.Disk = if ($disk) { [int][math]::Max(0, [math]::Min(100, 100 - $disk.PercentIdleTime)) } else { -1 }

    # 实际频率百分比：低于 100 = 降频，高于 100 = 睿频
    $s.Perf = -1
    try {
        $pi = Get-CimInstance Win32_PerfFormattedData_Counters_ProcessorInformation -Filter "Name='_Total'" -ErrorAction Stop
        if ($pi.PercentProcessorPerformance) { $s.Perf = [int]$pi.PercentProcessorPerformance }
    } catch {}
    $s.BaseMHz = (Get-CimInstance Win32_Processor | Select-Object -First 1).MaxClockSpeed

    $rows = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne '_Total' -and $_.Name -ne 'Idle' -and $_.IDProcess -ne 0 }
    $s.Procs = foreach ($r in $rows) {
        [pscustomobject]@{
            Name  = ($r.Name -replace '#\d+$', '')
            Id    = [int]$r.IDProcess
            Cpu   = [math]::Round($r.PercentProcessorTime / $Cores, 1)
            MemMB = [int][math]::Round($r.WorkingSetPrivate / 1MB)
        }
    }
    return $s
}

function Show-Bar($label, $pct) {
    if ($pct -lt 0) { Write-Info "$label  无法读取"; return }
    $n = [int][math]::Round($pct / 5)
    $bar = ('#' * $n).PadRight(20, '.')
    $color = 'Green'
    if ($pct -ge 85) { $color = 'Red' } elseif ($pct -ge 60) { $color = 'Yellow' }
    Write-Host ("  {0}  [{1}] {2,3}%" -f $label, $bar, $pct) -ForegroundColor $color
}

function Test-DoubleAntivirus {
    $tencent = Get-Process -Name QQPCRTP -ErrorAction SilentlyContinue
    if (-not $tencent) { return $false }
    $mode = ''
    try { $mode = "$((Get-MpComputerStatus -ErrorAction Stop).AMRunningMode)" } catch { return $false }
    return ($mode -eq 'Normal')
}

function Write-DoubleAntivirusHint {
    Write-Bad '腾讯电脑管家和 Windows 自带杀毒（Defender）两个实时防护同时在运行！'
    Write-Info '   每个新文件、每次下载都会被两个杀毒各扫一遍，还会互相扫对方的文件，CPU 和硬盘占用翻倍。'
    Write-Info '   建议只留一个：'
    Write-Info '   A. 只用 Windows 自带杀毒（推荐，轻、和系统集成好）：卸载腾讯电脑管家，Defender 会自动全面接手。'
    Write-Info '   B. 只用腾讯电脑管家：在它的设置里接管 Windows 安全中心，接管成功后 Defender 会自动进入被动模式。'
    Write-Info '      接管后再运行菜单 6，「登记的杀毒软件」里应能看到腾讯电脑管家。'
}

# ---------------------------------------------------------------------------
# 1. 卡顿急救
# ---------------------------------------------------------------------------
function Invoke-LagRescue {
    Write-Title '正在检测（约 2 秒）'
    $s = Get-Snapshot

    Show-Bar 'CPU ' $s.Cpu
    Show-Bar '内存' $s.Mem
    Show-Bar '硬盘' $s.Disk
    if ($s.Perf -gt 0 -and $s.BaseMHz) {
        $ghz = [math]::Round($s.BaseMHz * $s.Perf / 100 / 1000, 2)
        Write-Info ("CPU 实际频率约 {0} GHz（标称 {1} GHz）" -f $ghz, [math]::Round($s.BaseMHz / 1000, 2))
    }

    Write-Title '诊断结果'
    $found = $false
    if ($s.Cpu -ge 80) { Write-Bad 'CPU 快跑满了 —— 看下面列表里谁占得最多'; $found = $true }
    if ($s.Mem -ge 85) { Write-Bad "内存快用完了（共 $($s.MemTotalGB) GB）—— 关掉一些程序或浏览器标签页"; $found = $true }
    if ($s.Disk -ge 90) { Write-Bad '硬盘一直在满负荷读写 —— 新系统常见于更新/杀毒/搜索索引，等它跑完'; $found = $true }
    if ($s.Perf -gt 0 -and $s.Perf -lt 60 -and $s.Cpu -ge 30) {
        Write-Bad 'CPU 频率被压得很低，很可能是过热降频 —— 建议开启菜单 2「降温模式」，并清灰换硅脂'
        $found = $true
    }
    # 系统后台任务专挑「电脑空闲」时运行，所以常见「放一会儿再回来就很卡」
    $bgNames = 'msmpeng', 'mpdefendercoreservice', 'tiworker', 'trustedinstaller', 'mousocoreworker',
               'searchindexer', 'searchprotocolhost', 'searchfilterhost', 'compattelrunner'
    $bg = @($s.Procs | Where-Object { $bgNames -contains $_.Name.ToLower() -and $_.Cpu -ge 5 })
    if ($bg.Count -gt 0) {
        $bgCpu = [math]::Round(($bg | Measure-Object Cpu -Sum).Sum)
        Write-Bad "系统后台任务（杀毒扫描 / 系统更新 / 搜索索引）正在占用约 $bgCpu% 的 CPU"
        Write-Info '   Windows 会专门挑电脑「空闲没人用」的时候做这些事，所以放一会儿再回来会特别卡。'
        Write-Info '   新装的系统前几天尤其多：插着电源开机放一晚上让它跑完，之后会好很多。不要强行关掉它们。'
        $found = $true
    }
    if (Test-DoubleAntivirus) { Write-DoubleAntivirusHint; $found = $true }
    if (-not $found) { Write-Ok '资源占用不高。如果仍然卡，多半是过热降频或驱动问题，可以运行菜单 4「电脑体检」' }

    # 列出最占资源的程序：CPU 前 8 + 内存前 5
    $byCpu = $s.Procs | Sort-Object Cpu -Descending | Select-Object -First 8
    $byMem = $s.Procs | Sort-Object MemMB -Descending | Select-Object -First 5
    $list = @($byCpu)
    foreach ($p in $byMem) { if (-not ($list | Where-Object { $_.Id -eq $p.Id })) { $list += $p } }

    Write-Title '最占资源的程序'
    Write-Host ('  {0,4}  {1,-28} {2,6} {3,8}  {4}' -f '编号', '程序', 'CPU%', '内存MB', '说明') -ForegroundColor Gray
    $i = 0
    $items = @()
    foreach ($p in $list) {
        $i++
        $prot = Test-Protected $p.Name $p.Id
        $note = $Explain[$p.Name.ToLower()]
        if (-not $note) { $note = '' }
        if ($prot) { $note = "[系统，不能结束] $note" }
        $items += [pscustomobject]@{ No = $i; Name = $p.Name; Id = $p.Id; Protected = $prot }
        $color = 'White'
        if ($prot) { $color = 'DarkGray' }
        Write-Host ('  {0,4}  {1,-28} {2,6} {3,8}  {4}' -f $i, $p.Name, $p.Cpu, $p.MemMB, $note) -ForegroundColor $color
    }

    Write-Host ''
    $ans = Read-Host '  要结束哪个程序？输入编号（多个用空格隔开），直接回车跳过'
    $targets = @()
    foreach ($tok in ($ans -split '\s+' | Where-Object { $_ -match '^\d+$' })) {
        $it = $items | Where-Object { $_.No -eq [int]$tok }
        if (-not $it) { continue }
        if ($it.Protected) { Write-Bad "$($it.Name) 是系统程序，为了安全不结束它"; continue }
        if (-not ($targets | Where-Object { $_.Name -eq $it.Name })) { $targets += $it }
    }
    if ($targets.Count -gt 0) {
        $names = ($targets | ForEach-Object { $_.Name }) -join '、'
        $ok = Read-Host "  将关闭：$names（这些程序里没保存的内容会丢失）。确定吗？输入 y 回车"
        if ($ok -match '^[yY]') {
            foreach ($t in $targets) {
                # 按名字结束，浏览器这类多进程程序会整体关掉
                Get-Process -Name $t.Name -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
                Write-Ok "已关闭 $($t.Name)"
            }
        }
    }

    Write-Title '清理临时文件（只删 1 天前的，正在用的会自动跳过）'
    Clear-TempFiles
}

function Clear-TempFiles {
    $cut = (Get-Date).AddDays(-1)
    $freed = 0
    foreach ($dir in @($env:TEMP, (Join-Path $env:WINDIR 'Temp'))) {
        if (-not $dir -or -not (Test-Path -LiteralPath $dir)) { continue }
        $files = Get-ChildItem -LiteralPath $dir -Recurse -Force -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt $cut }
        foreach ($f in $files) {
            $len = $f.Length
            try { Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop; $freed += $len } catch {}
        }
    }
    Write-Ok ('已清理 {0} MB' -f [math]::Round($freed / 1MB))
}

# ---------------------------------------------------------------------------
# 2/3. 降温模式（关闭睿频）/ 恢复默认
# ---------------------------------------------------------------------------
function Get-MaxCpuState {
    $out = (powercfg /q SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 2>$null) -join "`n"
    # 输出最后两个十六进制值分别是「插电」和「电池」时的设置
    $m = [regex]::Matches($out, '0x([0-9a-fA-F]{8})')
    if ($m.Count -ge 2) {
        return @([Convert]::ToInt32($m[$m.Count - 2].Groups[1].Value, 16),
                 [Convert]::ToInt32($m[$m.Count - 1].Groups[1].Value, 16))
    }
    return $null
}

function Set-MaxCpuState([int]$v) {
    powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX $v | Out-Null
    powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX $v | Out-Null
    powercfg /setactive SCHEME_CURRENT | Out-Null
}

function Get-CoolModeText {
    $st = Get-MaxCpuState
    if (-not $st) { return '未知' }
    if ($st[0] -lt 100 -and $st[1] -lt 100) { return '已开启' }
    return '未开启'
}

function Enable-CoolMode {
    Write-Title '开启降温模式'
    # 高性能 / 卓越性能方案发热大，先切回「平衡」
    $active = (powercfg /getactivescheme) -join ''
    if ($active -match '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c|e9a42b02-d5df-448d-aa00-03f14749eb61') {
        powercfg /setactive SCHEME_BALANCED | Out-Null
        Write-Ok '电源计划已从「高性能」切回「平衡」'
    }
    Set-MaxCpuState 99
    Write-Ok 'CPU 最大状态设为 99%（= 关闭睿频）'
    Write-Info '效果：满载温度通常能降 10~20 度，风扇更安静，日常上网/办公/看视频基本感觉不到变慢。'
    Write-Info '      CPU 不会再因为过热反复降频，反而更不容易卡。'
    Write-Info '需要打游戏/剪视频时，运行菜单 3 恢复即可。'
}

function Disable-CoolMode {
    Write-Title '恢复默认性能'
    Set-MaxCpuState 100
    Write-Ok 'CPU 最大状态已恢复为 100%（睿频开启）'
}

# ---------------------------------------------------------------------------
# 4. 电脑体检
# ---------------------------------------------------------------------------
function Invoke-Checkup {
    Write-Title '基本信息'
    $cs = Get-CimInstance Win32_ComputerSystem
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    Write-Info "型号：$($cs.Manufacturer) $($cs.Model)"
    Write-Info "CPU ：$($cpu.Name.Trim())"
    Write-Info "系统：$($os.Caption) $($os.Version)"
    $up = (Get-Date) - $os.LastBootUpTime
    Write-Info ("已连续运行：{0} 天 {1} 小时" -f $up.Days, $up.Hours)
    if ($up.TotalDays -gt 3) {
        Write-Bad '很久没重启了。注意「关机」在 Win11 下不会真正清空，要点「重启」才行'
    }

    Write-Title '内存条'
    $mods = @(Get-CimInstance Win32_PhysicalMemory)
    foreach ($m in $mods) {
        $gb = [math]::Round($m.Capacity / 1GB)
        $speed = $m.ConfiguredClockSpeed
        if (-not $speed) { $speed = $m.Speed }
        $pn = "$($m.PartNumber)".Trim()
        Write-Info ("{0}：{1} GB  {2} MHz  {3} {4}" -f $m.DeviceLocator, $gb, $speed, "$($m.Manufacturer)".Trim(), $pn)
    }
    $totalGB = [math]::Round(($mods | Measure-Object Capacity -Sum).Sum / 1GB)
    Write-Info "合计识别到 $($mods.Count) 根，共 $totalGB GB"
    if ($mods.Count -eq 1) {
        Write-Bad '只识别到 1 根内存。如果你装了两根，说明有一根没插好、不兼容或者是坏的'
    } elseif ($mods.Count -ge 2) {
        $speeds = $mods | ForEach-Object { $_.Speed } | Sort-Object -Unique
        $caps = $mods | ForEach-Object { $_.Capacity } | Sort-Object -Unique
        if (@($speeds).Count -gt 1) { Write-Info '两根内存标称频率不同，会统一按低的那根运行（正常，不影响稳定）' }
        if (@($caps).Count -gt 1) { Write-Info '两根内存容量不同，只有一部分能双通道（正常，影响不大）' }
        if (@($speeds).Count -eq 1 -and @($caps).Count -eq 1) { Write-Ok '两根内存规格一致，双通道正常' }
    }

    Write-Title '硬盘'
    try {
        Get-PhysicalDisk -ErrorAction Stop | ForEach-Object {
            $type = "$($_.MediaType)"
            if ($type -eq 'SSD') { $type = '固态' } elseif ($type -eq 'HDD') { $type = '机械' } else { $type = '未知类型' }
            $health = "$($_.HealthStatus)"
            Write-Info ("{0}  {1} GB  {2}  健康：{3}" -f $_.FriendlyName, [math]::Round($_.Size / 1GB), $type, $health)
            if ($health -and $health -ne 'Healthy') { Write-Bad "$($_.FriendlyName) 健康状态异常，建议尽快备份数据！" }
        }
    } catch {}
    $c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    if ($c) {
        $freeGB = [math]::Round($c.FreeSpace / 1GB, 1)
        $pct = [math]::Round($c.FreeSpace / $c.Size * 100)
        if ($pct -lt 10) { Write-Bad "C 盘只剩 $freeGB GB（$pct%），空间不足会明显变卡" }
        else { Write-Ok "C 盘剩余 $freeGB GB（$pct%）" }
    }

    Write-Title '驱动'
    $bad = @(Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Error' })
    if ($bad.Count -eq 0) {
        Write-Ok '没有发现缺驱动或出错的设备'
    } else {
        Write-Bad "$($bad.Count) 个设备驱动有问题（重装系统后很常见）："
        foreach ($d in $bad) {
            $n = $d.FriendlyName
            if (-not $n) { $n = $d.InstanceId }
            Write-Info "   - $n"
        }
        Write-Info '   解决：设置 -> Windows 更新 -> 高级选项 -> 可选更新 -> 驱动程序更新，全部安装；'
        Write-Info '         或去机械革命官网「服务支持」下载对应型号的驱动（芯片组、散热/电源管理驱动尤其重要）'
    }

    Write-Title '温度与散热'
    Write-Info ("降温模式：{0}" -f (Get-CoolModeText))
    $plan = (powercfg /getactivescheme) -join ''
    if ($plan -match '\((.+)\)') { Write-Info "电源计划：$($Matches[1])" }
    try {
        $tz = Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop
        foreach ($t in $tz) {
            $celsius = [math]::Round($t.CurrentTemperature / 10 - 273.15)
            Write-Info "主板温度传感器：$celsius °C（仅供参考，准确的 CPU 温度请用 HWiNFO 或 Core Temp 查看）"
        }
    } catch {
        Write-Info '这台电脑不提供系统温度读数，准确的 CPU 温度请用 HWiNFO 或 Core Temp 查看'
    }

    Write-Title '后台活动'
    $busy = @()
    if (Get-Process -Name TiWorker, TrustedInstaller -ErrorAction SilentlyContinue) { $busy += 'Windows 更新正在安装' }
    if (Get-Process -Name MoUsoCoreWorker -ErrorAction SilentlyContinue) { $busy += 'Windows 更新正在检查/下载' }
    if ($busy.Count -gt 0) {
        foreach ($b in $busy) { Write-Bad $b }
        Write-Info '   新装的系统前几天会在后台装更新、扫描杀毒、建立搜索索引，期间又热又卡是正常的。'
        Write-Info '   插着电源、开着机放一晚上，让它跑完，通常就好了。'
    } else {
        Write-Ok '没有发现系统更新在后台运行'
    }

    Write-Title '开机自启动'
    $startup = @(Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue)
    Write-Info "共 $($startup.Count) 个开机自启动项："
    foreach ($st in $startup) { Write-Info "   - $($st.Name)" }
    if ($startup.Count -gt 6) {
        Write-Bad '自启动项偏多。按 Ctrl+Shift+Esc 打开任务管理器 -> 启动应用，把用不到的设为「已禁用」'
    }

    Write-Title '建议'
    Write-Info '2018 年的笔记本，CPU 温度高最常见的原因是：风扇和散热鳍片积灰、导热硅脂干了。'
    Write-Info '找电脑店清灰 + 换硅脂（一般几十块钱），通常能降 15~25 度，是最根本的解决办法。'
    Write-Info '平时使用：别放在床上/被子上用（会堵住底部进风口），可以垫个散热支架。'
}

# ---------------------------------------------------------------------------
# 5. 重启资源管理器
# ---------------------------------------------------------------------------
function Restart-Explorer {
    Write-Title '重启资源管理器'
    Write-Info '任务栏和桌面会消失 1~2 秒，然后自动回来；已打开的文件夹窗口会被关闭。'
    Get-Process -Name explorer -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe }
    Write-Ok '已重启'
}

# ---------------------------------------------------------------------------
# 6. 杀毒减负（Antimalware Service Executable 占 CPU 高）
# ---------------------------------------------------------------------------
function Invoke-DefenderTune {
    Write-Title 'Windows 自带杀毒（任务管理器里叫 Antimalware Service Executable）'
    try {
        $av = @(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -ErrorAction Stop)
        Write-Info '在 Windows 安全中心登记的杀毒软件：'
        foreach ($a in $av) { Write-Info "   - $($a.displayName)" }
    } catch {}

    $st = $null
    try { $st = Get-MpComputerStatus -ErrorAction Stop } catch {}
    $mode = ''
    if ($st) { $mode = "$($st.AMRunningMode)" }
    if (-not $st -or $mode -match 'Passive|Not running') {
        Write-Ok "Windows 自带杀毒已让位给其他杀毒软件（$mode），基本不占资源，不用处理"
        return
    }

    Write-Info "运行模式：$mode —— 说明它现在是这台电脑的主力杀毒。"
    if (Test-DoubleAntivirus) { Write-DoubleAntivirusHint }
    Write-Info '   如果上面列表里只有 Windows Defender、没有腾讯电脑管家，'
    Write-Info '   说明电脑管家没有接管系统杀毒，删掉 Defender 等于电脑没有完整的病毒防护。'
    Write-Info '   新装的系统它会先做一遍全盘扫描、更新病毒库，前几天占用高是正常的，之后会安静很多。'

    $pref = Get-MpPreference
    Write-Info ("当前：扫描时 CPU 上限 {0}%，低优先级扫描 {1}" -f $pref.ScanAvgCPULoadFactor, $pref.EnableLowCpuPriority)
    $ans = Read-Host '  输入 y 开启减负（扫描 CPU 上限 20% + 低优先级），输入 r 恢复默认，直接回车跳过'
    try {
        if ($ans -match '^[yY]') {
            Set-MpPreference -ScanAvgCPULoadFactor 20 -EnableLowCpuPriority $true -ErrorAction Stop
            Write-Ok '已开启：杀毒扫描最多占 20% CPU，并且会给你正在用的程序让路'
        } elseif ($ans -match '^[rR]') {
            Set-MpPreference -ScanAvgCPULoadFactor 50 -EnableLowCpuPriority $false -ErrorAction Stop
            Write-Ok '已恢复默认设置'
        }
    } catch {
        Write-Bad "设置失败：$($_.Exception.Message)"
    }
}

# ---------------------------------------------------------------------------
# 菜单
# ---------------------------------------------------------------------------
while ($true) {
    Write-Host ''
    Write-Host '================== 电脑卡顿急救 ==================' -ForegroundColor Cyan
    Write-Host ("  当前降温模式：{0}" -f (Get-CoolModeText))
    Write-Host '  1. 卡顿急救   看谁在占资源、可选择关掉它、清理临时文件'
    Write-Host '  2. 降温模式   关闭 CPU 睿频，温度明显下降（推荐日常开着）'
    Write-Host '  3. 恢复默认   重新开启睿频（打游戏 / 剪视频时用）'
    Write-Host '  4. 电脑体检   内存条、硬盘、驱动、后台更新、开机自启'
    Write-Host '  5. 重启任务栏 任务栏 / 桌面卡死、点不动时用'
    Write-Host '  6. 杀毒减负   Antimalware Service Executable 占 CPU 高时用'
    Write-Host '  0. 退出'
    $choice = Read-Host '请输入数字后回车'
    switch ($choice.Trim()) {
        '1' { Invoke-LagRescue }
        '2' { Enable-CoolMode }
        '3' { Disable-CoolMode }
        '4' { Invoke-Checkup }
        '5' { Restart-Explorer }
        '6' { Invoke-DefenderTune }
        '0' { exit 0 }
        default { Write-Bad '请输入 0~6 之间的数字' }
    }
}
