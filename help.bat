@echo off
REM NEOC AI Assistant - Help
REM Shows available commands and usage

cd /d "%~dp0"

echo.
echo ============================================
echo   NEOC AI Assistant - Help & Commands
echo ============================================
echo.
echo AVAILABLE BATCH FILES:
echo.
echo setup_neoc_assistant.bat
echo   - Initial setup and dependency installation
echo   - Run this first time only
echo.
echo check_status.bat
echo   - Quick system status check
echo   - Verify your setup before running
echo.
echo run_neoc_assistant.bat
echo   - Full startup with checks
echo   - Recommended for regular use
echo.
echo quick_start.bat
echo   - Minimal startup (fastest)
echo   - Use when you know everything is set up
echo.
echo run_tests.bat
echo   - Run complete test suite
echo   - Includes coverage reporting
echo.
echo dev_tools.bat
echo   - Interactive development menu
echo   - Code formatting, linting, testing, etc.
echo.
echo MANUAL COMMANDS:
echo.
echo uv sync              - Install/update dependencies
echo uv run python main.py - Start application manually
echo ollama serve         - Start Ollama service
echo ollama pull phi3      - Download AI model
echo.
echo WEB ACCESS:
echo   http://localhost:8000     - Main application
echo   http://localhost:8000/docs - API documentation
echo.
echo TROUBLESHOOTING:
echo.
echo 1. If you get timeout errors, use quick_start.bat
echo 2. Run check_status.bat to verify your setup
echo 3. Ensure Ollama is running: ollama serve
echo 4. Check Python version: python --version (should be 3.13+)
echo.
echo For more information, see README.md
echo.
pause