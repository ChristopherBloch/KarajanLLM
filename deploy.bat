@echo off
REM Aria Brain - Quick Deploy to Mac
REM Usage: deploy.bat [commit message]

set MSG=%*
if "%MSG%"=="" set MSG=Auto-deploy: %date% %time%

powershell -ExecutionPolicy Bypass -File "%~dp0deploy-to-mac.ps1" -Message "%MSG%"
