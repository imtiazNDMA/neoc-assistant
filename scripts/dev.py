#!/usr/bin/env python3
"""
NEOC AI Assistant Development Utilities
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command with proper error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def install_deps():
    """Install dependencies"""
    run_command("uv sync", "Installing dependencies")

def run_tests():
    """Run test suite"""
    run_command("uv run pytest tests/ -v", "Running tests")

def run_tests_coverage():
    """Run tests with coverage"""
    run_command("uv run pytest tests/ --cov=src/neoc_assistant --cov-report=html", "Running tests with coverage")

def lint_code():
    """Lint code"""
    run_command("uv run flake8 src/ tests/", "Linting code")

def format_code():
    """Format code"""
    run_command("uv run black src/ tests/", "Formatting code")
    run_command("uv run isort src/ tests/", "Sorting imports")

def type_check():
    """Type check code"""
    run_command("uv run mypy src/", "Type checking")

def start_server():
    """Start development server"""
    print("🚀 Starting NEOC AI Assistant server...")
    print("Server will be available at http://localhost:8000")
    print("Press Ctrl+C to stop")
    try:
        subprocess.run("uv run python main.py", shell=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

def clean_cache():
    """Clean caches and temporary files"""
    run_command("find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true", "Cleaning Python cache")
    run_command("find . -name '*.pyc' -delete", "Removing compiled Python files")
    run_command("rm -rf .pytest_cache htmlcov .coverage", "Cleaning test artifacts")

def show_help():
    """Show help message"""
    print("NEOC AI Assistant Development Utilities")
    print("===================================")
    print()
    print("Available commands:")
    print("  install    - Install dependencies")
    print("  test       - Run test suite")
    print("  coverage   - Run tests with coverage")
    print("  lint       - Lint code")
    print("  format     - Format code")
    print("  typecheck  - Type check code")
    print("  server     - Start development server")
    print("  clean      - Clean caches and temporary files")
    print("  all        - Run all checks (format, lint, typecheck, test)")
    print("  help       - Show this help message")
    print()
    print("Usage: python scripts/dev.py <command>")

def run_all_checks():
    """Run all code quality checks"""
    print("🔍 Running all code quality checks...")
    format_code()
    lint_code()
    type_check()
    run_tests_coverage()

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    commands = {
        'install': install_deps,
        'test': run_tests,
        'coverage': run_tests_coverage,
        'lint': lint_code,
        'format': format_code,
        'typecheck': type_check,
        'server': start_server,
        'clean': clean_cache,
        'all': run_all_checks,
        'help': show_help
    }

    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()