@echo off
setlocal
rem Lag rescue / cool-down / health check launcher.
rem Requests admin rights, then runs speedup.ps1 from the same folder.

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0speedup.ps1"
if errorlevel 1 pause
