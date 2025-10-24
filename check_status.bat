@echo off
REM NEOC AI Assistant - Status Check
REM Quick check of system status without starting the application

cd /d "%~dp0"

echo.
echo ============================================
echo   NEOC AI Assistant - Status Check
echo ============================================
echo.

REM Check if uv is available
echo [CHECK] uv package manager...
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] uv is installed
) else (
    echo [FAIL] uv is not installed
)

REM Check if virtual environment exists
echo [CHECK] Virtual environment...
if exist ".venv" (
    echo [OK] Virtual environment exists
) else (
    echo [FAIL] Virtual environment not found (run setup_neoc_assistant.bat)
)

REM Check if Ollama is running
echo [CHECK] Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama is running
) else (
    echo [FAIL] Ollama is not running (start with: ollama serve)
)

REM Check if phi3 model is available (only if Ollama is running)
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo [CHECK] phi3 model...
    curl -s http://localhost:11434/api/tags | findstr "phi3" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] phi3 model is available
    ) else (
        echo [FAIL] phi3 model not found (run: ollama pull phi3)
    )
)

REM Check if application can import
echo [CHECK] Application imports...
if exist ".venv" (
    uv run python -c "from neoc_assistant.app import app; print('[OK] Application imports successfully')" 2>nul
    if %errorlevel% neq 0 (
        echo [FAIL] Application import failed
    )
) else (
    echo [SKIP] Cannot check imports without virtual environment
)

echo.
echo ============================================
echo   Status Check Complete
echo ============================================
echo.
echo If all checks show [OK], you can run: quick_start.bat
echo.
pause