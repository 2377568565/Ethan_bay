@echo off
setlocal
rem Touchpad fix launcher. Requests admin rights, then runs fix-touchpad.ps1.

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix-touchpad.ps1"
echo.
pause
