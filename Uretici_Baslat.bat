@echo off
cd /d "%~dp0csv_senaryo_uretici"
title IHA Telemetri CSV Senaryo Uretici v1.6.0
start "" pythonw "%~dp0csv_senaryo_uretici\app.py"
exit
