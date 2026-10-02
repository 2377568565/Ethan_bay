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
# 安装进度查看：每 3 秒刷新一次，看“显卡驱动一键更新”是不是还在干活（只看不改）。按 Q 退出。

$ErrorActionPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
try { $Host.UI.RawUI.WindowTitle = '安装进度查看（按 Q 退出）' } catch {}
$Cores = [Environment]::ProcessorCount
$startVer = "$((Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' } | Select-Object -First 1).DriverVersion)"
$lastSize = $null

function Get-FolderMB($p) {
    if (-not (Test-Path -LiteralPath $p)) { return $null }
    $sum = (Get-ChildItem -LiteralPath $p -Recurse -Force -File | Measure-Object Length -Sum).Sum
    return [math]::Round($sum / 1MB)
}

while ($true) {
    $procs = Get-CimInstance Win32_Process
    $perf = @{}
    foreach ($r in (Get-CimInstance Win32_PerfFormattedData_PerfProc_Process)) { $perf[[int]$r.IDProcess] = $r }

    $rows = @()
    foreach ($p in $procs) {
        $role = ''
        if ($p.CommandLine -match 'PCFOCUS_SELF' -and $p.Name -eq 'powershell.exe' -and $p.ProcessId -ne $PID) { $role = '更新脚本（下载/校验签名/等待安装）' }
        elseif ($p.Name -match '^\d{3}\.\d{2}-.*\.exe$' -or $p.ExecutablePath -match 'DriverUpdate') { $role = 'NVIDIA 驱动安装包（正在解压/启动安装）' }
        elseif ($p.ExecutablePath -match '\\NVIDIA' -and $p.Name -match 'setup|nvi2|install') { $role = 'NVIDIA 安装程序（正在安装）' }
        elseif ($p.Name -match '^(drvinst|dpinst|pnputil|msiexec)\.exe$') { $role = 'Windows 驱动安装组件（正在写入驱动）' }
        if (-not $role) { continue }
        $pf = $perf[[int]$p.ProcessId]
        $cpu = 0; $io = 0
        if ($pf) { $cpu = [math]::Round($pf.PercentProcessorTime / $Cores, 1); $io = [math]::Round(($pf.IOReadBytesPersec + $pf.IOWriteBytesPersec) / 1MB, 1) }
        $rows += [pscustomobject]@{ Name = $p.Name; Pid = $p.ProcessId; Cpu = $cpu; Io = $io; Role = $role }
    }

    $nvVer = "$((Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' } | Select-Object -First 1).DriverVersion)"
    $extract = Get-FolderMB 'C:\NVIDIA\DisplayDriver'

    Clear-Host
    Write-Host "安装进度查看    $(Get-Date -Format 'HH:mm:ss')    每 3 秒刷新，按 Q 退出" -ForegroundColor Cyan
    Write-Host ''
    if ($rows.Count -eq 0) {
        Write-Host '  没有找到安装相关的进程' -ForegroundColor Yellow
    } else {
        Write-Host ('  {0,-48} {1,7} {2,10}  {3}' -f '进程', 'CPU%', '读写MB/s', '在做什么') -ForegroundColor Gray
        foreach ($r in $rows) { Write-Host ('  {0,-48} {1,7} {2,10}  {3}' -f $r.Name, $r.Cpu, $r.Io, $r.Role) }
    }
    Write-Host ''
    if ($null -ne $extract) {
        $trend = ''
        if ($null -ne $lastSize -and $extract -gt $lastSize) { $trend = '（还在增长 = 正在解压）' }
        Write-Host "  NVIDIA 解压目录 C:\NVIDIA\DisplayDriver：$extract MB $trend"
        $lastSize = $extract
    }
    Write-Host "  当前 NVIDIA 驱动版本：$nvVer"
    Write-Host ''

    $installing = $rows | Where-Object { $_.Role -match '正在安装|正在写入|正在解压' }
    $script = $rows | Where-Object { $_.Role -match '更新脚本' }
    $busy = $rows | Where-Object { $_.Cpu -ge 1 -or $_.Io -ge 0.5 }
    if ($nvVer -and $startVer -and $nvVer -ne $startVer) {
        Write-Host '  结论：NVIDIA 驱动已经换成新版本了，安装基本完成，等更新窗口出结果/倒计时重启即可。' -ForegroundColor Green
    } elseif ($installing) {
        Write-Host '  结论：正在安装中，请耐心等待，不要关机。' -ForegroundColor Green
    } elseif ($script -and $busy) {
        Write-Host '  结论：更新脚本正在工作（多半是在校验 870MB 安装包的数字签名），请等待。' -ForegroundColor Green
    } elseif ($script) {
        Write-Host '  结论：更新脚本还开着，但现在没有在用 CPU/硬盘。再观察 2~3 分钟；一直这样就截图发给我。' -ForegroundColor Yellow
    } else {
        Write-Host '  结论：没有检测到进行中的安装。看一下更新窗口显示了什么结果，截图发给我。' -ForegroundColor Yellow
    }

    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Milliseconds 200
        while ([Console]::KeyAvailable) { if (([Console]::ReadKey($true)).Key -eq 'Q') { exit 0 } }
    }
}
