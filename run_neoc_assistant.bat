@echo off
REM NEOC AI Assistant - Automated Startup Script
REM This script automates the setup and execution of NEOC AI Assistant

echo.
echo ============================================
echo   NEOC AI Assistant - Disaster Management LLM
echo ============================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] uv package manager is not installed!
    echo.
    echo Please install uv first:
    echo 1. Visit: https://astral.sh/uv
    echo 2. Run: curl -LsSf https://astral.sh/uv/install.sh ^| sh
    echo 3. Or use: pip install uv
    echo.
    pause
    exit /b 1
)

REM Check if Ollama is running
echo [INFO] Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not running!
    echo.
    echo Please start Ollama first:
    echo 1. Download from: https://ollama.ai/download
    echo 2. Run: ollama serve
    echo 3. Pull the model: ollama pull phi3
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit...
    pause >nul
)

REM Navigate to the project directory
cd /d "%~dp0"

REM Check if virtual environment exists, create if needed
if not exist ".venv" (
    echo [INFO] Setting up virtual environment...
    uv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install/update dependencies
echo [INFO] Installing/updating dependencies...
uv sync
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

REM Skip model check and health check to avoid timeouts
echo [INFO] Skipping model availability check (run manually if needed)
echo [INFO] Skipping health checks (run manually if needed)

REM Start the application
echo.
echo ============================================
echo   Starting NEOC AI Assistant...
echo ============================================
echo.
echo [INFO] The application will display accessible URLs on startup.
echo [INFO] Press Ctrl+C to stop the application
echo.

uv run python main.py

REM If we get here, the application stopped
echo.
echo [INFO] NEOC AI Assistant has stopped.
echo Press any key to exit...
pause >nul