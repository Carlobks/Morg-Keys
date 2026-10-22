@echo off
title Desinstalar - Morg Keys
echo Isto desliga o GlazeWM, a barra e o arranque automatico para esta conta.
choice /m "Continuar"
if errorlevel 2 exit /b
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\desinstalar.ps1"
echo.
pause
