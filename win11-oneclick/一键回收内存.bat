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
# 一键回收内存：回收各程序闲置的内存 + 清空备用缓存，然后自动关闭窗口
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
try { $Host.UI.RawUI.WindowTitle = "一键回收内存" } catch {}
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

Write-Title '一键回收内存'
$before = Get-MemUsedGB
if (Invoke-MemoryReclaim) {
    $after = Get-MemUsedGB
    $freed = [math]::Round($before - $after, 2)
    if ($freed -lt 0) { $freed = 0 }
    Write-Ok ("已用内存：{0} GB  ->  {1} GB（释放约 {2} GB）" -f $before, $after, $freed)
}
Write-Info '5 秒后自动关闭...'
Start-Sleep -Seconds 5
exit 0
