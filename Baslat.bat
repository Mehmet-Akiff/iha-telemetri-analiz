@echo off
cd /d "%~dp0"
title IHA Telemetri Analiz Istasyonu v1.6.0
start "" pythonw "%~dp0gui_app.py"
exit
