@echo off
title Instalar - Morg Keys
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\instalar.ps1" %*
echo.
pause
