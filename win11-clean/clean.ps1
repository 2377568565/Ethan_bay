# 一键清理：CPU（关掉占用高的程序）+ 磁盘垃圾 + 运行内存（Win10 / Win11）
# 用法: 双击同目录下的 clean.bat（会自动请求管理员权限）
# 原则: 只删缓存和临时文件，不碰你的文档/照片/下载；系统进程不会被关闭。

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '一键清理' } catch {}

function Write-Title($m) { Write-Host "`n==== $m ====" -ForegroundColor Cyan }
function Write-Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Bad($m)   { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Info($m)  { Write-Host "  $m" }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限：请双击 clean.bat 运行。'
    exit 1
}

# ---------------------------------------------------------------------------
# 内存清理用到的系统接口
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 通用函数
# ---------------------------------------------------------------------------
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
    if (-not $path) { return $true }
    if ($path -like "$env:WINDIR\*") { return $true }
    if ($path -match '\\Windows Defender\\') { return $true }
    return $false
}

function Get-MemUsedGB {
    $os = Get-CimInstance Win32_OperatingSystem
    $mem = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
    $totalMB = $os.TotalVisibleMemorySize / 1KB
    return [math]::Round(($totalMB - $mem.AvailableMBytes) / 1KB, 2)
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

$memBefore = Get-MemUsedGB
$diskBefore = Get-CFreeGB
$Cores = [Environment]::ProcessorCount

# ---------------------------------------------------------------------------
Write-Title '第 1 步：CPU —— 找出正在拖慢电脑的程序'
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
        Count = $_.Count
    }
}
$candidates = @($groups | Where-Object { -not (Test-Protected $_.Name $_.Id) -and ($_.Cpu -ge 3 -or $_.MemMB -ge 300) } |
    Sort-Object Cpu, MemMB -Descending | Select-Object -First 8)

if ($candidates.Count -eq 0) {
    Write-Ok '没有占用明显偏高的程序，CPU 这块不用处理'
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

# ---------------------------------------------------------------------------
Write-Title '第 2 步：磁盘 —— 清理垃圾文件'
$total = [long]0
$now = Get-Date

$items = @(
    @{ Name = '用户临时文件';         Path = $env:TEMP;                                                 Cut = $now.AddDays(-1) },
    @{ Name = '系统临时文件';         Path = (Join-Path $env:WINDIR 'Temp');                            Cut = $now.AddDays(-1) },
    @{ Name = '系统错误报告';         Path = (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportArchive'); Cut = $now },
    @{ Name = '系统错误报告(队列)';   Path = (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportQueue');   Cut = $now },
    @{ Name = '旧的系统更新安装包';   Path = (Join-Path $env:WINDIR 'SoftwareDistribution\Download');   Cut = $now.AddDays(-10) },
    @{ Name = '系统网页缓存';         Path = (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\INetCache'); Cut = $now.AddDays(-1) }
)
foreach ($it in $items) {
    $f = Remove-OldFiles $it.Path $it.Cut
    $total += $f
    Write-Info ('{0,-22} {1,8} MB' -f $it.Name, [math]::Round($f / 1MB))
}

# 浏览器缓存：浏览器开着时跳过，避免把它正在用的缓存搞乱
$browsers = @(
    @{ Name = 'Edge';   Proc = 'msedge'; Root = (Join-Path $env:LOCALAPPDATA 'Microsoft\Edge\User Data') },
    @{ Name = 'Chrome'; Proc = 'chrome'; Root = (Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data') }
)
foreach ($b in $browsers) {
    if (-not (Test-Path -LiteralPath $b.Root)) { continue }
    if (Get-Process -Name $b.Proc -ErrorAction SilentlyContinue) {
        Write-Bad "$($b.Name) 浏览器开着，跳过它的缓存（关掉浏览器再运行可以多清一些）"
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
    Write-Info ('{0,-22} {1,8} MB' -f "$($b.Name) 浏览器缓存", [math]::Round($f / 1MB))
}

# 传递优化缓存（Windows 更新的 P2P 缓存）
try {
    Delete-DeliveryOptimizationCache -Force -ErrorAction Stop | Out-Null
    Write-Info ('{0,-22} {1,8}' -f '更新传递优化缓存', '已清空')
} catch {}

# 回收站：里面是你删掉的文件，先问一下
try {
    $bin = (New-Object -ComObject Shell.Application).Namespace(10)
    $binCount = @($bin.Items()).Count
    if ($binCount -gt 0) {
        $ok = Read-Host "  回收站里有 $binCount 个文件/文件夹，要清空吗？（清空后找不回来）输入 y 回车，直接回车跳过"
        if ($ok -match '^[yY]') {
            Clear-RecycleBin -Force -ErrorAction SilentlyContinue
            Write-Ok '回收站已清空'
        }
    }
} catch {}

Write-Ok ('磁盘垃圾共清理约 {0} MB' -f [math]::Round($total / 1MB))

if (Test-Path -LiteralPath "$env:SystemDrive\Windows.old") {
    Write-Bad '发现 C:\Windows.old（重装前的旧系统，通常有十几到几十 GB）'
    Write-Info '   确认不需要旧系统里的文件后，可以在：设置 -> 系统 -> 存储 -> 临时文件 -> 勾选「以前的 Windows 安装」 -> 删除'
}

# ---------------------------------------------------------------------------
Write-Title '第 3 步：运行内存 —— 回收闲置内存'
$r1 = [PcClean.Mem]::Run(2)   # 回收各程序暂时不用的内存
$r2 = [PcClean.Mem]::Run(4)   # 清空备用缓存
if ($r1 -ne 0 -and $r2 -ne 0) {
    Write-Bad ('内存清理没有成功（错误码 0x{0:X8}）' -f $r1)
} else {
    Start-Sleep -Seconds 1
    Write-Ok '已回收闲置内存'
}

# ---------------------------------------------------------------------------
$memAfter = Get-MemUsedGB
$diskAfter = Get-CFreeGB
Write-Title '清理结果'
Write-Info ("已用内存：{0} GB  ->  {1} GB" -f $memBefore, $memAfter)
Write-Info ("C 盘剩余：{0} GB  ->  {1} GB" -f $diskBefore, $diskAfter)
Write-Host ''
Write-Info '小提示：内存清理的效果是暂时的，程序用到时会重新占用，这是正常的。'
Write-Info '        真正长期变快靠的是：少开程序 / 少开浏览器标签页、只装一个杀毒、开启降温模式。'
