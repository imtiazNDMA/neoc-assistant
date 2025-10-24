#!/bin/bash
# NEOC AI Assistant Setup Script

set -e

echo "🚀 Setting up NEOC AI Assistant..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data static

# Check Ollama
echo "🔍 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    ollama list
else
    echo "⚠️  Ollama not found. Please install Ollama and run:"
    echo "   ollama pull phi3:latest"
fi

# Run tests
echo "🧪 Running tests..."
uv run pytest tests/ -v

echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  uv run python main.py"
echo ""
echo "To run tests:"
echo "  uv run pytest tests/"
echo ""
echo "To check coverage:"
echo "  uv run pytest tests/ --cov=src/neoc_assistant"