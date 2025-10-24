@echo off
REM NEOC AI Assistant - Initial Setup Script
REM This script performs the initial setup and configuration

echo.
echo ============================================
echo   NEOC AI Assistant - Initial Setup
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

REM Navigate to the project directory
cd /d "%~dp0"

REM Create virtual environment
echo [INFO] Creating virtual environment...
uv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)

REM Install dependencies
echo [INFO] Installing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

REM Install development dependencies
echo [INFO] Installing development dependencies...
uv sync --dev
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install some dev dependencies, but continuing...
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "chroma_db" mkdir chroma_db
if not exist ".cache" mkdir .cache
if not exist "data" mkdir data

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating default .env file...
    copy .env.example .env >nul 2>&1
    echo [INFO] Please edit .env file with your configuration settings
)

REM Check Ollama installation (but don't pull model to avoid timeout)
echo [INFO] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not installed!
    echo.
    echo Please install Ollama manually:
    echo 1. Download from: https://ollama.ai/download
    echo 2. Install and run: ollama serve
    echo 3. Pull the model: ollama pull phi3
    echo.
) else (
    echo [INFO] Ollama is installed.
    echo [INFO] To pull the phi3 model, run manually: ollama pull phi3
)

REM Skip initial tests to avoid timeouts
echo [INFO] Setup complete! Run tests manually with: run_tests.bat

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo [SUCCESS] NEOC AI Assistant has been set up successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Ensure Ollama is running: ollama serve
echo 3. Run the application: run_neoc_assistant.bat
echo.
echo For more information, see README.md
echo.
pause