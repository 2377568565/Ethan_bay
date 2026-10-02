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
# 老电脑一键加速：开启专注模式 -> 降低 CPU 温度 -> 磁盘清理 -> 回收内存 -> 实时专注（后台小窗口）-> 关闭占 CPU 的程序（需确认）
# 原则: 只删缓存和临时文件，不碰个人文件和回收站；系统进程不碰；专注模式设置可用“恢复默认设置.bat”撤销。
$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

function Write-Title($m) { Write-Host "`n==== $m ====" -ForegroundColor Cyan }
function Write-Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)   { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m)  { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限，请双击 bat 文件并在弹窗里点“是”。'
    exit 1
}
try { $Host.UI.RawUI.WindowTitle = "老电脑一键加速" } catch {}
if (-not ('PcClean.Mem' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace PcClean {
    public static class Mem {
        [StructLayout(LayoutKind.Sequential, Pack = 4)]
        struct TokenPrivileges { public int Count; public long Luid; public int Attr; }

        [DllImport("advapi32.dll", SetLastError = true)]
        static extern bool OpenProcessToken(IntPtr process, int access, out IntPtr token);
        [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        static extern bool LookupPrivilegeValue(string system, string name, out long luid);
        [DllImport("advapi32.dll", SetLastError = true)]
        static extern bool AdjustTokenPrivileges(IntPtr token, bool disableAll, ref TokenPrivileges state, int length, IntPtr prev, IntPtr retLength);
        [DllImport("kernel32.dll")]
        static extern IntPtr GetCurrentProcess();
        [DllImport("kernel32.dll")]
        static extern bool CloseHandle(IntPtr handle);
        [DllImport("ntdll.dll")]
        static extern int NtSetSystemInformation(int infoClass, ref int info, int length);

        static void EnablePrivilege(string name) {
            IntPtr token;
            if (!OpenProcessToken(GetCurrentProcess(), 0x28, out token)) return; // ADJUST_PRIVILEGES | QUERY
            var tp = new TokenPrivileges { Count = 1, Attr = 2 };                  // SE_PRIVILEGE_ENABLED
            if (LookupPrivilegeValue(null, name, out tp.Luid))
                AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
            CloseHandle(token);
        }

        // command: 2 = 回收所有程序闲置的内存（工作集）, 4 = 清空备用内存（缓存）
        public static int Run(int command) {
            EnablePrivilege("SeProfileSingleProcessPrivilege");
            EnablePrivilege("SeIncreaseQuotaPrivilege");
            int c = command;
            return NtSetSystemInformation(80, ref c, sizeof(int)); // 80 = SystemMemoryListInformation
        }
    }
}
'@
}

function Get-MemUsedGB {
    $os = Get-CimInstance Win32_OperatingSystem
    $mem = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
    return [math]::Round(($os.TotalVisibleMemorySize / 1KB - $mem.AvailableMBytes) / 1KB, 2)
}

function Invoke-MemoryReclaim {
    $r1 = [PcClean.Mem]::Run(2)   # 回收各程序暂时不用的内存
    $r2 = [PcClean.Mem]::Run(4)   # 清空备用缓存
    if ($r1 -ne 0 -and $r2 -ne 0) {
        Write-Bad ('内存回收没有成功（错误码 0x{0:X8}）' -f $r1)
        return $false
    }
    Start-Sleep -Seconds 1
    return $true
}
if (-not ('FocusNative' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class FocusNative {
    [DllImport("user32.dll")]
    static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll", SetLastError = true)]
    static extern bool SystemParametersInfo(uint action, uint param, ref int pvParam, uint winIni);
    [DllImport("user32.dll", SetLastError = true)]
    static extern bool SystemParametersInfo(uint action, uint param, IntPtr pvParam, uint winIni);

    public static int GetForegroundPid() {
        uint pid;
        GetWindowThreadProcessId(GetForegroundWindow(), out pid);
        return (int)pid;
    }

    // SPI_GETCLIENTAREAANIMATION / SPI_SETCLIENTAREAANIMATION：系统设置里的“动画效果”开关
    public static bool GetAnimation() {
        int v = 1;
        SystemParametersInfo(0x1042, 0, ref v, 0);
        return v != 0;
    }
    public static void SetAnimation(bool on) {
        SystemParametersInfo(0x1043, 0, on ? new IntPtr(1) : IntPtr.Zero, 3); // UPDATEINIFILE | SENDCHANGE
    }
}
'@
}

$BackupDir  = Join-Path $env:LOCALAPPDATA 'PcFocusMode'
$BackupFile = Join-Path $BackupDir 'backup.json'
$ClassicMenuKey = 'HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}'

function Restart-Shell {
    Get-Process -Name explorer -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe }
}
$ProtectedNames = @(
    'system', 'idle', 'registry', 'memory compression', 'memcompression', 'smss', 'csrss', 'wininit',
    'winlogon', 'services', 'lsass', 'lsaiso', 'svchost', 'dwm', 'explorer', 'fontdrvhost', 'sihost',
    'ctfmon', 'audiodg', 'spoolsv', 'msmpeng', 'mpdefendercoreservice', 'nissrv',
    'securityhealthservice', 'searchindexer', 'tiworker', 'trustedinstaller', 'mousocoreworker',
    'powershell', 'conhost', 'cmd', 'wmiprvse', 'runtimebroker', 'taskhostw',
    'startmenuexperiencehost', 'shellexperiencehost', 'searchhost', 'textinputhost', 'wudfhost',
    'dllhost', 'applicationframehost', 'taskmgr'
)

# 系统进程（C:\Windows 下的程序、杀毒、读不到路径的受保护进程）一律不碰
function Test-ProtectedProc($p) {
    if ($ProtectedNames -contains $p.ProcessName.ToLower()) { return $true }
    $path = $null
    try { $path = $p.Path } catch {}
    if (-not $path) { return $true }
    if ($path -like "$env:WINDIR\*") { return $true }
    if ($path -match '\\Windows Defender\\') { return $true }
    return $false
}

$Cores = [Environment]::ProcessorCount

# 专注模式要改的设置（每一项都会先备份原值）
$Tweaks = @(
    @{ Key = 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl'; Name = 'Win32PrioritySeparation'; Type = 'DWord'; Value = 38;
       Desc = '前台程序获得更多 CPU 时间' },
    @{ Key = 'HKCU:\Control Panel\Desktop'; Name = 'MenuShowDelay'; Type = 'String'; Value = '100';
       Desc = '菜单弹出等待 400 毫秒 -> 100 毫秒' },
    @{ Key = 'HKCU:\Control Panel\Desktop\WindowMetrics'; Name = 'MinAnimate'; Type = 'String'; Value = '0';
       Desc = '关闭窗口最小化/最大化动画' },
    @{ Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'; Name = 'TaskbarAnimations'; Type = 'DWord'; Value = 0;
       Desc = '关闭任务栏动画' },
    @{ Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'; Name = 'EnableTransparency'; Type = 'DWord'; Value = 0;
       Desc = '关闭毛玻璃透明效果' },
    @{ Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications'; Name = 'GlobalUserDisabled'; Type = 'DWord'; Value = 1;
       Desc = '禁止应用商店类应用在后台运行' }
)

function Get-RegValue($key, $name) {
    try {
        $item = Get-ItemProperty -Path $key -Name $name -ErrorAction Stop
        return @{ Exists = $true; Value = $item.$name }
    } catch {
        return @{ Exists = $false; Value = $null }
    }
}

function Get-CFreeGB {
    $c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    return [math]::Round($c.FreeSpace / 1GB, 2)
}

# 删除目录里早于 $cut 的文件；不进入链接/挂载点，正在使用的文件自动跳过
function Remove-OldFiles([string]$dir, [datetime]$cut) {
    $freed = [long]0
    if (-not $dir -or -not (Test-Path -LiteralPath $dir)) { return $freed }
    $stack = New-Object System.Collections.Stack
    $stack.Push($dir)
    while ($stack.Count -gt 0) {
        $d = $stack.Pop()
        foreach ($e in @(Get-ChildItem -LiteralPath $d -Force -ErrorAction SilentlyContinue)) {
            if ($e.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            if ($e.PSIsContainer) { $stack.Push($e.FullName); continue }
            if ($e.LastWriteTime -lt $cut) {
                $len = $e.Length
                try { Remove-Item -LiteralPath $e.FullName -Force -ErrorAction Stop; $freed += $len } catch {}
            }
        }
    }
    return $freed
}

# ---------------------------------------------------------------------------
# 降温：彻底关闭睿频 + CPU 最大状态 99% + 主动散热 + 杀毒扫描限速（都会先备份，可恢复）
# ---------------------------------------------------------------------------
$CoolBackupFile = Join-Path $BackupDir 'cooling-backup.json'
$CoolSettings = @(
    @{ Alias = 'PERFBOOSTMODE';   Value = 0;  Desc = '彻底关闭睿频（最有效的一项，满载温度通常降 10~20 度）' },
    @{ Alias = 'PROCTHROTTLEMAX'; Value = 99; Desc = 'CPU 最大状态 99%（关闭睿频的双保险）' },
    @{ Alias = 'SYSCOOLPOL';      Value = 1;  Desc = '散热方式改为“主动”：先让风扇转快，不够再降频' }
)

function Get-ActiveSchemeGuid {
    $m = [regex]::Match(((powercfg /getactivescheme) -join ''), '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    if ($m.Success) { return $m.Value }
    return $null
}

# 读取电源设置的当前值；输出里最后两个十六进制数分别是“插电”和“电池”时的值
function Get-PowerValue($scheme, $alias) {
    # 用 /qh：睿频、散热方式默认是隐藏设置，/q 查不到
    $out = (powercfg /qh $scheme SUB_PROCESSOR $alias 2>$null) -join "`n"
    $m = [regex]::Matches($out, '0x([0-9a-fA-F]{8})')
    if ($m.Count -ge 2) {
        return @{ AC = [Convert]::ToInt32($m[$m.Count - 2].Groups[1].Value, 16)
                  DC = [Convert]::ToInt32($m[$m.Count - 1].Groups[1].Value, 16) }
    }
    return $null
}

function Enable-Cooling {
    # 高性能 / 卓越性能方案发热大，先切回“平衡”
    $origScheme = Get-ActiveSchemeGuid
    if ($origScheme -match '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c|e9a42b02-d5df-448d-aa00-03f14749eb61') {
        powercfg /setactive SCHEME_BALANCED | Out-Null
        Write-Ok '电源计划从“高性能”切回“平衡”'
    }
    $scheme = Get-ActiveSchemeGuid
    if (-not $scheme) { Write-Bad '读取不到电源计划，跳过降温设置'; return }

    $firstTime = -not (Test-Path -LiteralPath $CoolBackupFile)
    if ($firstTime) {
        $scanCpu = $null
        $lowCpu = $null
        try {
            $pref = Get-MpPreference -ErrorAction Stop
            $scanCpu = [int]$pref.ScanAvgCPULoadFactor
            $lowCpu = [bool]$pref.EnableLowCpuPriority
        } catch {}
        $backup = @{
            OrigScheme = $origScheme
            Scheme     = $scheme
            Settings   = @(foreach ($c in $CoolSettings) {
                             $v = Get-PowerValue $scheme $c.Alias
                             if ($v) { @{ Alias = $c.Alias; AC = $v.AC; DC = $v.DC } }
                         })
            ScanCpu    = $scanCpu
            LowCpu     = $lowCpu
        }
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        $backup | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $CoolBackupFile -Encoding UTF8
    }

    if (-not $firstTime) {
        # 旧版本没能备份隐藏设置：在改动之前把缺的补进备份
        try {
            $bk = Get-Content -LiteralPath $CoolBackupFile -Raw -Encoding UTF8 | ConvertFrom-Json
            $have = @($bk.Settings | ForEach-Object { $_.Alias })
            $list = @($bk.Settings)
            $changed = $false
            foreach ($c in $CoolSettings) {
                if ($have -contains $c.Alias) { continue }
                $v = Get-PowerValue $bk.Scheme $c.Alias
                if ($v) { $list += [pscustomobject]@{ Alias = $c.Alias; AC = $v.AC; DC = $v.DC }; $changed = $true }
            }
            if ($changed) {
                $bk.Settings = $list
                $bk | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $CoolBackupFile -Encoding UTF8
            }
        } catch {}
    }

    foreach ($c in $CoolSettings) {
        if (-not (Get-PowerValue $scheme $c.Alias)) { Write-Bad "这台电脑不支持：$($c.Desc)"; continue }
        powercfg /setacvalueindex $scheme SUB_PROCESSOR $c.Alias $c.Value | Out-Null
        powercfg /setdcvalueindex $scheme SUB_PROCESSOR $c.Alias $c.Value | Out-Null
        Write-Ok $c.Desc
    }
    powercfg /setactive $scheme | Out-Null

    $boost = Get-PowerValue $scheme 'PERFBOOSTMODE'
    if ($boost -and $boost.AC -eq 0 -and $boost.DC -eq 0) {
        Write-Ok '验证：睿频已关闭（插电和电池都生效）'
        Write-Info '   自己确认：任务管理器 -> 性能 -> CPU，“速度”以后最高只会到 1.8 GHz 左右（以前会冲到 3~4 GHz）'
    }

    try {
        Set-MpPreference -ScanAvgCPULoadFactor 20 -EnableLowCpuPriority $true -ErrorAction Stop
        Write-Ok '杀毒扫描最多占 20% CPU，减少突然发热'
    } catch {}

    if ($firstTime) {
        Write-Info ''
        Write-Info '软件能做的是“少发热”；如果这样还是很烫，就是散热硬件的问题了：'
        Write-Info '   - 2018 年的笔记本，风扇积灰、硅脂干了最常见：找电脑店清灰 + 换硅脂，通常再降 15~25 度'
        Write-Info '   - 别放在床上/被子上用，底部进风口堵住会很烫；垫个散热支架效果明显'
    }
}

# 实时专注：持续给前台程序提速、给后台占 CPU 的程序降速；按 Q 退出时全部恢复
function Start-LiveFocusLoop {
    Write-Title '实时专注（窗口开着时一直生效）'
    Write-Info '你正在用的程序：优先级调高；后台偷偷占 CPU 的程序：优先级调低（不会被关闭）'
    Write-Host '  不用时点开这个窗口按 Q 键退出，所有程序会自动恢复原样。' -ForegroundColor Yellow
    Write-Info ''

    $interval = 2
    $orig = @{}       # pid -> 原优先级
    $state = @{}      # pid -> 'fg' / 'bg'
    $prevCpu = @{}    # pid -> 上次累计 CPU 毫秒
    $protCache = @{}  # pid -> 是否受保护
    $lastFg = ''
    try {
        while ($true) {
            $fgProc = Get-Process -Id ([FocusNative]::GetForegroundPid()) -ErrorAction SilentlyContinue
            $fgName = ''
            if ($fgProc) { $fgName = $fgProc.ProcessName }

            $lowered = @()
            foreach ($p in Get-Process) {
                $cpu = $null
                try { $cpu = $p.TotalProcessorTime.TotalMilliseconds } catch {}
                if ($null -eq $cpu) { continue }   # 读不到的都是系统进程
                $pct = 0
                if ($prevCpu.ContainsKey($p.Id)) { $pct = ($cpu - $prevCpu[$p.Id]) / ($interval * 10 * $Cores) }
                $prevCpu[$p.Id] = $cpu

                if (-not $protCache.ContainsKey($p.Id)) { $protCache[$p.Id] = Test-ProtectedProc $p }
                if ($protCache[$p.Id]) { continue }

                $want = ''
                if ($fgName -and $p.ProcessName -eq $fgName) { $want = 'fg' }
                elseif ($pct -ge 3) { $want = 'bg' }

                try {
                    if ($want -eq 'fg' -and $state[$p.Id] -ne 'fg') {
                        if (-not $orig.ContainsKey($p.Id)) { $orig[$p.Id] = $p.PriorityClass }
                        if ($orig[$p.Id] -eq 'Normal' -or $orig[$p.Id] -eq 'BelowNormal') { $p.PriorityClass = 'AboveNormal' }
                        $state[$p.Id] = 'fg'
                    } elseif ($want -ne 'fg' -and $state[$p.Id] -eq 'fg') {
                        $p.PriorityClass = $orig[$p.Id]   # 不再是前台了：恢复原优先级
                        $state.Remove($p.Id)
                    }
                    if ($want -eq 'bg' -and -not $state.ContainsKey($p.Id)) {
                        if (-not $orig.ContainsKey($p.Id)) { $orig[$p.Id] = $p.PriorityClass }
                        if ($orig[$p.Id] -eq 'Normal') {
                            $p.PriorityClass = 'BelowNormal'
                            $state[$p.Id] = 'bg'
                            $lowered += $p.ProcessName
                        }
                    }
                } catch {}
            }

            if ($fgName -and $fgName -ne $lastFg) {
                Write-Host ("  [{0}] 当前程序：{1}  -> 已优先" -f (Get-Date -Format 'HH:mm:ss'), $fgName) -ForegroundColor Green
                $lastFg = $fgName
            }
            foreach ($n in ($lowered | Sort-Object -Unique)) {
                Write-Host ("  [{0}] 后台程序：{1}  -> 已降速" -f (Get-Date -Format 'HH:mm:ss'), $n) -ForegroundColor DarkYellow
            }

            $quit = $false
            for ($i = 0; $i -lt ($interval * 5); $i++) {
                Start-Sleep -Milliseconds 200
                while ([Console]::KeyAvailable) {
                    if (([Console]::ReadKey($true)).Key -eq 'Q') { $quit = $true }
                }
                if ($quit) { break }
            }
            if ($quit) { break }
        }
    } finally {
        $n = 0
        foreach ($id in @($orig.Keys)) {
            $p = Get-Process -Id $id -ErrorAction SilentlyContinue
            if ($p) { try { $p.PriorityClass = $orig[$id]; $n++ } catch {} }
        }
        Write-Ok "已退出实时专注，$n 个程序的优先级已恢复原样"
    }
}

# 由第 5 步启动的独立小窗口只跑实时专注
if ($env:PCFOCUS_MODE -eq 'live') {
    try { $Host.UI.RawUI.WindowTitle = '实时专注（按 Q 退出）' } catch {}
    Start-LiveFocusLoop
    Write-Info '3 秒后自动关闭...'
    Start-Sleep -Seconds 3
    exit 0
}

$memBefore = Get-MemUsedGB
$diskBefore = Get-CFreeGB

# ---------------------------------------------------------------------------
Write-Title '第 1 步：开启专注模式'
$needApply = $false
foreach ($t in $Tweaks) {
    $cur = Get-RegValue $t.Key $t.Name
    if (-not $cur.Exists -or "$($cur.Value)" -ne "$($t.Value)") { $needApply = $true }
}
if ([FocusNative]::GetAnimation()) { $needApply = $true }
if (-not (Test-Path -LiteralPath $ClassicMenuKey)) { $needApply = $true }

if (-not $needApply) {
    Write-Ok '专注模式之前已经开启，跳过'
} else {
    $firstTime = -not (Test-Path -LiteralPath $BackupFile)
    if ($firstTime) {
        # 只在第一次开启时备份，避免把“原始值”覆盖掉
        $backup = @{
            Tweaks      = @(foreach ($t in $Tweaks) {
                              $cur = Get-RegValue $t.Key $t.Name
                              @{ Key = $t.Key; Name = $t.Name; Type = $t.Type; Exists = $cur.Exists; Value = $cur.Value }
                          })
            Animation   = [FocusNative]::GetAnimation()
            ClassicMenu = (Test-Path -LiteralPath $ClassicMenuKey)
        }
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        $backup | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $BackupFile -Encoding UTF8
        Write-Ok '原设置已备份（用“恢复默认设置.bat”可一键撤销）'
    }
    foreach ($t in $Tweaks) {
        try {
            if (-not (Test-Path -LiteralPath $t.Key)) { New-Item -Path $t.Key -Force | Out-Null }
            Set-ItemProperty -Path $t.Key -Name $t.Name -Value $t.Value -Type $t.Type -ErrorAction Stop
            Write-Ok $t.Desc
        } catch {
            Write-Bad "$($t.Desc) —— 设置失败：$($_.Exception.Message)"
        }
    }
    [FocusNative]::SetAnimation($false)
    Write-Ok '关闭窗口/菜单的淡入淡出动画'
    try {
        New-Item -Path "$ClassicMenuKey\InprocServer32" -Force | Out-Null
        Set-Item -Path "$ClassicMenuKey\InprocServer32" -Value '' -ErrorAction Stop
        Write-Ok '右键菜单换成经典样式（秒开）'
    } catch {
        Write-Bad "右键菜单设置失败：$($_.Exception.Message)"
    }
    Write-Info '正在刷新任务栏和桌面（会闪一下）...'
    Restart-Shell
    if ($firstTime) {
        Write-Info '提示：按 Ctrl+Shift+Esc 打开任务管理器 -> 启动应用，把用不到的开机自启程序禁用，开机会快很多。'
    }
}

# ---------------------------------------------------------------------------
Write-Title '第 2 步：降低 CPU 温度'
Enable-Cooling

# ---------------------------------------------------------------------------
Write-Title '第 3 步：清理磁盘垃圾'
$total = [long]0
$now = Get-Date
$items = @(
    @{ Name = '用户临时文件';       Path = $env:TEMP;                                                          Cut = $now.AddDays(-1) },
    @{ Name = '系统临时文件';       Path = (Join-Path $env:WINDIR 'Temp');                                     Cut = $now.AddDays(-1) },
    @{ Name = '系统错误报告';       Path = (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportArchive'); Cut = $now },
    @{ Name = '系统错误报告(队列)'; Path = (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportQueue');   Cut = $now },
    @{ Name = '旧的系统更新安装包'; Path = (Join-Path $env:WINDIR 'SoftwareDistribution\Download');            Cut = $now.AddDays(-10) },
    @{ Name = '系统网页缓存';       Path = (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\INetCache');        Cut = $now.AddDays(-1) }
)
foreach ($it in $items) {
    $f = Remove-OldFiles $it.Path $it.Cut
    $total += $f
    Write-Info ('{0,-20} {1,8} MB' -f $it.Name, [math]::Round($f / 1MB))
}
# 浏览器缓存：浏览器开着时跳过，避免把它正在用的缓存搞乱
$browsers = @(
    @{ Name = 'Edge';   Proc = 'msedge'; Root = (Join-Path $env:LOCALAPPDATA 'Microsoft\Edge\User Data') },
    @{ Name = 'Chrome'; Proc = 'chrome'; Root = (Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data') }
)
foreach ($b in $browsers) {
    if (-not (Test-Path -LiteralPath $b.Root)) { continue }
    if (Get-Process -Name $b.Proc -ErrorAction SilentlyContinue) {
        Write-Info "$($b.Name) 浏览器开着，跳过它的缓存"
        continue
    }
    $f = [long]0
    $profiles = Get-ChildItem -LiteralPath $b.Root -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq 'Default' -or $_.Name -like 'Profile *' }
    foreach ($p in $profiles) {
        foreach ($sub in 'Cache', 'Code Cache', 'GPUCache') {
            $f += Remove-OldFiles (Join-Path $p.FullName $sub) $now
        }
    }
    $total += $f
    Write-Info ('{0,-20} {1,8} MB' -f "$($b.Name) 浏览器缓存", [math]::Round($f / 1MB))
}
try { Delete-DeliveryOptimizationCache -Force -ErrorAction Stop *> $null; Write-Info ('{0,-20} {1,8}' -f '更新传递优化缓存', '已清空') } catch {}
Write-Ok ('磁盘垃圾共清理约 {0} MB（回收站没有动）' -f [math]::Round($total / 1MB))

# ---------------------------------------------------------------------------
Write-Title '第 4 步：回收闲置内存'
if (Invoke-MemoryReclaim) { Write-Ok '已回收闲置内存' }

$memAfter = Get-MemUsedGB
$diskAfter = Get-CFreeGB
Write-Info ("已用内存：{0} GB -> {1} GB    C 盘剩余：{2} GB -> {3} GB" -f $memBefore, $memAfter, $diskBefore, $diskAfter)
$memTotal = [math]::Round((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize / 1MB, 1)
if ($memAfter / $memTotal -lt 0.5) {
    Write-Info ("内存总共 {0} GB，只用了 {1} GB，非常充裕，本来就没什么可回收的——内存不是这台电脑慢的原因。" -f $memTotal, $memAfter)
}

# ---------------------------------------------------------------------------
Write-Title '第 5 步：启动实时专注'
$running = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*PCFOCUS_MODE='live'*" }
if ($running) {
    Write-Ok '实时专注已经在运行了，跳过'
} else {
    Start-Process powershell.exe -WindowStyle Minimized -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `$env:PCFOCUS_MODE='live'; Invoke-Expression ([IO.File]::ReadAllText(`$env:PCFOCUS_SELF, [Text.Encoding]::UTF8))"
    Write-Ok '实时专注已在后台启动（任务栏上最小化的“实时专注”窗口）'
    Write-Info '   它会一直给你正在用的程序提速、给后台程序降速。'
    Write-Info '   不用时点开那个窗口按 Q 退出，所有程序自动恢复原样。'
}

# ---------------------------------------------------------------------------
Write-Title '第 6 步：关闭占用 CPU 高的程序（需要你确认）'
$null = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$procs = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne '_Total' -and $_.Name -ne 'Idle' -and $_.IDProcess -ne 0 } |
    ForEach-Object {
        [pscustomobject]@{
            Name  = ($_.Name -replace '#\d+$', '')
            Id    = [int]$_.IDProcess
            Cpu   = [math]::Round($_.PercentProcessorTime / $Cores, 1)
            MemMB = [int][math]::Round($_.WorkingSetPrivate / 1MB)
        }
    }
# 同名多进程（比如浏览器）合并计算
$groups = $procs | Group-Object Name | ForEach-Object {
    [pscustomobject]@{
        Name  = $_.Name
        Id    = ($_.Group | Select-Object -First 1).Id
        Cpu   = [math]::Round(($_.Group | Measure-Object Cpu -Sum).Sum, 1)
        MemMB = [int](($_.Group | Measure-Object MemMB -Sum).Sum)
    }
}
$candidates = @($groups | Where-Object {
        $p = Get-Process -Id $_.Id -ErrorAction SilentlyContinue
        $p -and -not (Test-ProtectedProc $p) -and ($_.Cpu -ge 3 -or $_.MemMB -ge 300)
    } | Sort-Object Cpu, MemMB -Descending | Select-Object -First 8)

if ($candidates.Count -eq 0) {
    Write-Ok '没有占用明显偏高的程序，跳过'
} else {
    Write-Host ('  {0,4}  {1,-28} {2,6} {3,8}' -f '编号', '程序', 'CPU%', '内存MB') -ForegroundColor Gray
    $i = 0
    foreach ($c in $candidates) {
        $i++
        Write-Host ('  {0,4}  {1,-28} {2,6} {3,8}' -f $i, $c.Name, $c.Cpu, $c.MemMB)
    }
    Write-Info '（只列出你自己打开的程序，系统程序不会出现在这里）'
    $ans = Read-Host '  要关掉哪些？输入编号（多个用空格隔开），直接回车跳过'
    $sel = @()
    foreach ($tok in ($ans -split '\s+' | Where-Object { $_ -match '^\d+$' })) {
        $n = [int]$tok
        if ($n -ge 1 -and $n -le $candidates.Count) { $sel += $candidates[$n - 1] }
    }
    if ($sel.Count -gt 0) {
        $names = ($sel | ForEach-Object { $_.Name }) -join '、'
        $ok = Read-Host "  将关闭：$names（没保存的内容会丢失）。确定吗？输入 y 回车"
        if ($ok -match '^[yY]') {
            foreach ($s in $sel) {
                Get-Process -Name $s.Name -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
                Write-Ok "已关闭 $($s.Name)"
            }
        }
    }
}

Write-Host ''
Write-Ok '全部完成！实时专注会在后台小窗口里继续工作。'
Write-Info '5 秒后关闭本窗口...'
Start-Sleep -Seconds 5
exit 0
