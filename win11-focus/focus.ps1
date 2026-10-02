# 专注加速：让 CPU 优先照顾你正在用的程序，减少后台干扰（Win10 / Win11）
# 用法: 双击同目录下的 focus.bat（会自动请求管理员权限）
# 原则: 所有改动都有备份，菜单 4 一键恢复；不关闭任何系统服务，不碰系统进程。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '专注加速' } catch {}

function Write-Title($m) { Write-Host "`n==== $m ====" -ForegroundColor Cyan }
function Write-Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)   { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m)  { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限：请双击 focus.bat 运行。'
    Read-Host '按回车退出' | Out-Null
    exit 1
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

# 专注模式要改的设置（每一项都会先备份原值）
$Tweaks = @(
    @{ Key = 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl'; Name = 'Win32PrioritySeparation'; Type = 'DWord'; Value = 38;
       Desc = '前台程序获得更多 CPU 时间（系统“调整以优化程序性能”的加强版）' },
    @{ Key = 'HKCU:\Control Panel\Desktop'; Name = 'MenuShowDelay'; Type = 'String'; Value = '100';
       Desc = '菜单弹出等待时间 400 毫秒 -> 100 毫秒' },
    @{ Key = 'HKCU:\Control Panel\Desktop\WindowMetrics'; Name = 'MinAnimate'; Type = 'String'; Value = '0';
       Desc = '关闭窗口最小化/最大化动画' },
    @{ Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'; Name = 'TaskbarAnimations'; Type = 'DWord'; Value = 0;
       Desc = '关闭任务栏动画' },
    @{ Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'; Name = 'EnableTransparency'; Type = 'DWord'; Value = 0;
       Desc = '关闭毛玻璃透明效果（老显卡很吃资源）' },
    @{ Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications'; Name = 'GlobalUserDisabled'; Type = 'DWord'; Value = 1;
       Desc = '禁止应用商店类应用在后台偷偷运行' }
)

function Get-RegValue($key, $name) {
    try {
        $item = Get-ItemProperty -Path $key -Name $name -ErrorAction Stop
        return @{ Exists = $true; Value = $item.$name }
    } catch {
        return @{ Exists = $false; Value = $null }
    }
}

function Restart-Shell {
    Get-Process -Name explorer -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe }
}

function Get-FocusStatus {
    if (Test-Path -LiteralPath $BackupFile) { return '已开启' }
    return '未开启'
}

# ---------------------------------------------------------------------------
# 1. 开启专注模式
# ---------------------------------------------------------------------------
function Enable-FocusMode {
    Write-Title '开启专注模式'
    if (-not (Test-Path -LiteralPath $BackupFile)) {
        # 只在第一次开启时备份，避免重复开启时把“原始值”覆盖掉
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
        Write-Ok "原设置已备份到 $BackupFile"
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
    Write-Ok '关闭窗口/菜单的淡入淡出动画（点开东西立刻出现）'

    # Win11 新版右键菜单要先加载很多扩展，换回经典菜单后右键立刻弹出
    try {
        New-Item -Path "$ClassicMenuKey\InprocServer32" -Force | Out-Null
        Set-Item -Path "$ClassicMenuKey\InprocServer32" -Value '' -ErrorAction Stop
        Write-Ok '右键菜单换成经典样式，弹出更快（不用再点“显示更多选项”）'
    } catch {
        Write-Bad "右键菜单设置失败：$($_.Exception.Message)"
    }

    Write-Info ''
    Write-Info '正在刷新任务栏和桌面（会闪一下）...'
    Restart-Shell
    Write-Ok '专注模式已开启。部分动画设置要注销或重启一次后完全生效。'

    Write-Title '建议顺手做：关掉没用的开机自启动'
    Write-Info '马上为你打开任务管理器的“启动应用”页面：'
    Write-Info '把不认识/用不到的（如各种更新助手、网盘、播放器、电脑管家等）右键 -> 禁用。'
    Write-Info '禁用只是不让它开机自动运行，软件本身还在，随时可以再启用。'
    try { Start-Process taskmgr.exe -ArgumentList '/0 /startup' } catch { Start-Process taskmgr.exe }

    Show-DiskHint
}

function Show-DiskHint {
    try {
        $dn = (Get-Partition -DriveLetter C -ErrorAction Stop).DiskNumber
        $pd = Get-PhysicalDisk -ErrorAction Stop | Where-Object { $_.DeviceId -eq "$dn" }
        if ($pd -and "$($pd.MediaType)" -eq 'HDD') {
            Write-Title '重要发现'
            Write-Bad '系统装在机械硬盘上！这是“打开软件/网页慢”的头号原因。'
            Write-Info '   换一块固态硬盘（几百块钱）重装系统，打开速度通常能快好几倍，比任何优化都管用。'
        }
    } catch {}
}

# ---------------------------------------------------------------------------
# 2. 实时专注：窗口开着时，持续给前台程序提速、给后台占 CPU 的程序降速
# ---------------------------------------------------------------------------
$ProtectedNames = @(
    'system', 'idle', 'registry', 'memory compression', 'memcompression', 'smss', 'csrss', 'wininit',
    'winlogon', 'services', 'lsass', 'lsaiso', 'svchost', 'dwm', 'explorer', 'fontdrvhost', 'sihost',
    'ctfmon', 'audiodg', 'spoolsv', 'msmpeng', 'mpdefendercoreservice', 'nissrv',
    'securityhealthservice', 'searchindexer', 'tiworker', 'trustedinstaller', 'mousocoreworker',
    'powershell', 'conhost', 'cmd', 'wmiprvse', 'runtimebroker', 'taskhostw',
    'startmenuexperiencehost', 'shellexperiencehost', 'searchhost', 'textinputhost', 'wudfhost',
    'dllhost', 'applicationframehost', 'taskmgr'
)

function Test-ProtectedProc($p) {
    if ($ProtectedNames -contains $p.ProcessName.ToLower()) { return $true }
    $path = $null
    try { $path = $p.Path } catch {}
    if (-not $path) { return $true }
    if ($path -like "$env:WINDIR\*") { return $true }
    if ($path -match '\\Windows Defender\\') { return $true }
    return $false
}

function Start-LiveFocus {
    Write-Title '实时专注已启动'
    Write-Info '你正在用的程序：优先级调高（高于正常）'
    Write-Info '后台偷偷占 CPU 的程序：优先级调低（低于正常），不会被关闭'
    Write-Host '  按 Q 键退出，退出时自动把所有程序恢复原样。（请不要直接点 X 关窗口）' -ForegroundColor Yellow
    Write-Info ''

    $Cores = [Environment]::ProcessorCount
    $interval = 2
    $orig = @{}       # pid -> 原优先级
    $state = @{}      # pid -> 'fg' / 'bg'
    $prevCpu = @{}    # pid -> 上次累计 CPU 毫秒
    $protCache = @{}  # pid -> 是否受保护
    $lastFg = ''

    try {
        while ($true) {
            $fgPid = [FocusNative]::GetForegroundPid()
            $fgProc = Get-Process -Id $fgPid -ErrorAction SilentlyContinue
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
                        if ($orig[$p.Id] -eq 'Normal' -or $orig[$p.Id] -eq 'BelowNormal') {
                            $p.PriorityClass = 'AboveNormal'
                        }
                        $state[$p.Id] = 'fg'
                    } elseif ($want -ne 'fg' -and $state[$p.Id] -eq 'fg') {
                        # 不再是前台了：恢复原优先级
                        $p.PriorityClass = $orig[$p.Id]
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

            # 等待下一轮，期间检查是否按了 Q
            $quit = $false
            for ($i = 0; $i -lt ($interval * 5); $i++) {
                Start-Sleep -Milliseconds 200
                while ([Console]::KeyAvailable) {
                    $k = [Console]::ReadKey($true)
                    if ($k.Key -eq 'Q') { $quit = $true }
                }
                if ($quit) { break }
            }
            if ($quit) { break }
        }
    } finally {
        $n = 0
        foreach ($id in @($orig.Keys)) {
            $p = Get-Process -Id $id -ErrorAction SilentlyContinue
            if ($p) {
                try { $p.PriorityClass = $orig[$id]; $n++ } catch {}
            }
        }
        Write-Ok "已退出实时专注，$n 个程序的优先级已恢复原样"
    }
}

# ---------------------------------------------------------------------------
# 4. 恢复默认
# ---------------------------------------------------------------------------
function Disable-FocusMode {
    Write-Title '恢复默认设置'
    if (-not (Test-Path -LiteralPath $BackupFile)) {
        Write-Info '没有找到备份，说明专注模式没有开启过，不需要恢复。'
        return
    }
    $b = Get-Content -LiteralPath $BackupFile -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($t in $b.Tweaks) {
        try {
            if ($t.Exists) {
                Set-ItemProperty -Path $t.Key -Name $t.Name -Value $t.Value -Type $t.Type -ErrorAction Stop
            } else {
                Remove-ItemProperty -Path $t.Key -Name $t.Name -ErrorAction SilentlyContinue
            }
        } catch {
            Write-Bad "恢复 $($t.Name) 失败：$($_.Exception.Message)"
        }
    }
    [FocusNative]::SetAnimation([bool]$b.Animation)
    if (-not $b.ClassicMenu) {
        Remove-Item -LiteralPath $ClassicMenuKey -Recurse -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath $BackupFile -Force -ErrorAction SilentlyContinue
    Write-Info '正在刷新任务栏和桌面（会闪一下）...'
    Restart-Shell
    Write-Ok '已全部恢复成开启专注模式之前的样子。注销或重启一次后完全生效。'
}

# ---------------------------------------------------------------------------
# 菜单
# ---------------------------------------------------------------------------
while ($true) {
    Write-Host ''
    Write-Host '==================== 专注加速 ====================' -ForegroundColor Cyan
    Write-Host ("  专注模式：{0}" -f (Get-FocusStatus))
    Write-Host '  1. 开启专注模式   前台程序优先、关动画和透明、右键菜单秒开、禁后台应用'
    Write-Host '  2. 实时专注       窗口开着时，持续给当前程序提速、给后台程序降速'
    Write-Host '  3. 管理开机自启   打开任务管理器的“启动应用”页面'
    Write-Host '  4. 恢复默认       撤销第 1 项的全部改动'
    Write-Host '  0. 退出'
    $choice = Read-Host '请输入数字后回车'
    switch ($choice.Trim()) {
        '1' { Enable-FocusMode }
        '2' { Start-LiveFocus }
        '3' { try { Start-Process taskmgr.exe -ArgumentList '/0 /startup' } catch { Start-Process taskmgr.exe } }
        '4' { Disable-FocusMode }
        '0' { exit 0 }
        default { Write-Bad '请输入 0~4 之间的数字' }
    }
}
