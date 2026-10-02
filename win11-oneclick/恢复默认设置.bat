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
# 恢复默认设置：撤销“老电脑一键加速”第 1 步（专注模式）的全部改动
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
try { $Host.UI.RawUI.WindowTitle = "恢复默认设置" } catch {}
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

Write-Title '恢复默认设置'
if (-not (Test-Path -LiteralPath $BackupFile)) {
    Write-Info '没有找到备份，说明专注模式没有开启过，不需要恢复。'
} else {
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
Write-Host ''
Read-Host '按回车关闭' | Out-Null
exit 0
