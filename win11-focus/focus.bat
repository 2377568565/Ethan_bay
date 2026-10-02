@echo off
setlocal
rem Focus booster launcher. Requests admin rights, then runs focus.ps1.

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0focus.ps1"
if errorlevel 1 pause
