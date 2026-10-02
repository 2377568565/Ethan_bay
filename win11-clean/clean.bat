@echo off
setlocal
rem One-click cleanup launcher (CPU hogs, junk files, memory).
rem Requests admin rights, then runs clean.ps1 from the same folder.

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0clean.ps1"
echo.
pause
