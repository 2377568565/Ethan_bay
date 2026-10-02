@echo off
setlocal
rem Win11 audio "muted / cannot unmute" one-click fix launcher.
rem Requests admin rights, then runs fix-audio.ps1 from the same folder.

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix-audio.ps1"
echo.
pause
