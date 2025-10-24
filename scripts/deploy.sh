#!/bin/bash
# NEOC AI Assistant Production Deployment Script

set -e

echo "🚀 Starting NEOC AI Assistant production deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p chroma_db
mkdir -p .cache

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your production configuration!"
fi

# Pull latest Ollama image
echo "🐳 Pulling latest Ollama image..."
docker pull ollama/ollama:latest

# Start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check if Ollama is running
echo "🔍 Checking Ollama service..."
if curl -f http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama is running"

    # Pull the required model
    echo "🤖 Pulling phi3 model..."
    docker-compose exec -T ollama ollama pull phi3
else
    echo "❌ Ollama is not responding. Check logs with: docker-compose logs ollama"
    exit 1
fi

# Check if NEOC AI Assistant is running
echo "🔍 Checking NEOC AI Assistant service..."
  if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ NEOC AI Assistant is running"
    echo ""
    echo "🎉 Deployment successful!"
    echo "🌐 Web UI: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "📊 Metrics: http://localhost:8000/metrics"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
else
    echo "❌ NEOC AI Assistant is not responding. Check logs with: docker-compose logs neoc-ai-assistant"
    exit 1
fi