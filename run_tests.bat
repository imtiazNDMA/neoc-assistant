@echo off
REM NEOC AI Assistant - Test Runner
REM Runs the complete test suite

cd /d "%~dp0"

echo.
echo ============================================
echo   NEOC AI Assistant - Test Suite
echo ============================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_neoc_assistant.bat first.
    pause
    exit /b 1
)

echo [INFO] Running test suite...
echo.

uv run python -m pytest tests/ -v --tb=short --cov=src/neoc_assistant --cov-report=term-missing

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] All tests passed!
) else (
    echo.
    echo [WARNING] Some tests failed. Check the output above.
)

echo.
pause