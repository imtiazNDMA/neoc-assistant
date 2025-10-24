@echo off
REM NEOC AI Assistant - Development Tools
REM Provides access to various development utilities

cd /d "%~dp0"

echo.
echo ============================================
echo   NEOC AI Assistant - Development Tools
echo ============================================
echo.
echo Select an option:
echo 1. Format code (black + isort)
echo 2. Lint code (flake8)
echo 3. Type check (mypy)
echo 4. Run all checks (format + lint + type check)
echo 5. Run tests with coverage
echo 6. Build documentation
echo 7. Performance tuning
echo 8. Citation test
echo 9. Demo
echo 10. Start server (production mode)
echo 11. Start server (development mode with reload)
echo 0. Exit
echo.

set /p choice="Enter your choice (0-11): "

if "%choice%"=="1" goto format
if "%choice%"=="2" goto lint
if "%choice%"=="3" goto typecheck
if "%choice%"=="4" goto all_checks
if "%choice%"=="5" goto test_coverage
if "%choice%"=="6" goto docs
if "%choice%"=="7" goto performance
if "%choice%"=="8" goto citation
if "%choice%"=="9" goto demo
if "%choice%"=="10" goto server_prod
if "%choice%"=="11" goto server_dev
if "%choice%"=="0" goto exit

echo Invalid choice. Please try again.
goto end

:format
echo [INFO] Formatting code...
uv run black src/ tests/ scripts/
uv run isort src/ tests/ scripts/
echo [SUCCESS] Code formatted!
goto end

:lint
echo [INFO] Running linter...
uv run flake8 src/ tests/ scripts/
echo [SUCCESS] Linting complete!
goto end

:typecheck
echo [INFO] Running type checker...
uv run mypy src/neoc_assistant/
echo [SUCCESS] Type checking complete!
goto end

:all_checks
echo [INFO] Running all code quality checks...
uv run black --check src/ tests/ scripts/
uv run isort --check-only src/ tests/ scripts/
uv run flake8 src/ tests/ scripts/
uv run mypy src/neoc_assistant/
echo [SUCCESS] All checks passed!
goto end

:test_coverage
echo [INFO] Running tests with coverage...
uv run python -m pytest tests/ -v --cov=src/neoc_assistant --cov-report=html --cov-report=term-missing
echo [INFO] Coverage report saved to htmlcov/index.html
goto end

:docs
echo [INFO] Building documentation...
uv run mkdocs build
echo [SUCCESS] Documentation built!
goto end

:performance
echo [INFO] Running performance tuning...
uv run python scripts/performance_tune.py
goto end

:citation
echo [INFO] Testing citation functionality...
uv run python scripts/test_citations.py
goto end

:demo
echo [INFO] Running demo...
uv run python scripts/demo.py
goto end

:server_prod
echo [INFO] Starting server in production mode...
uv run python main.py
goto end

:server_dev
echo [INFO] Starting server in development mode with hot reload...
uv run python main.py --reload
goto end

:exit
echo Goodbye!
goto end

:end
echo.
pause