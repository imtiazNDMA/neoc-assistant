@echo off
REM NEOC AI Assistant - Quick Start
REM Minimal startup script for regular use

cd /d "%~dp0"

echo Starting NEOC AI Assistant...
echo Web UI will be available at: http://localhost:8000
echo Press Ctrl+C to stop
echo.

uv run python main.py