# Installation

This guide covers installing NEOC AI Assistant, a complete LLM application for disaster management, for development and production use.

## Prerequisites

- Python 3.13+
- uv package manager
- Ollama (for local LLM inference)
- 4GB+ RAM recommended
- 10GB+ disk space for models and data

## Quick Install

=== "Using uv (Recommended)"

    ```bash
    # Clone the repository
    git clone https://github.com/your-org/neoc-assistant.git
    cd neoc-assistant

    # Install with uv
    uv sync

    # Install Ollama and pull model
    curl -fsSL https://ollama.ai/install.sh | sh
    ollama pull phi3
    ```

=== "Using pip"

    ```bash
    # Clone the repository
    git clone https://github.com/your-org/neoc-assistant.git
    cd neoc-assistant

    # Install dependencies
    pip install -r requirements-dev.txt
    pip install -e .

    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    ollama pull phi3
    ```

=== "Using Docker"

    ```bash
    # Clone the repository
    git clone https://github.com/your-org/neoc-assistant.git
    cd neoc-assistant

    # Start with Docker Compose
    docker-compose up -d --build
    ```

## Development Setup

1. **Clone and install**:
   ```bash
   git clone https://github.com/your-org/neoc-assistant.git
   cd neoc-assistant
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize data**:
   ```bash
   # Start Ollama in background
   ollama serve &

   # Pull required model
   ollama pull phi3

   # Ingest documents (optional)
   python scripts/dev.py ingest
   ```

4. **Run development server**:
   ```bash
   python scripts/dev.py server
   ```

## Production Setup

### Docker Deployment

1. **Configure production environment**:
   ```bash
   cp .env.production .env
   # Edit with production values
   ```

2. **Deploy**:
   ```bash
   ./scripts/deploy.sh
   ```

3. **Verify deployment**:
   ```bash
   curl http://localhost:8000/health
   ```

### Manual Production Setup

1. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.13 python3.13-venv

   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Setup application**:
   ```bash
   git clone https://github.com/your-org/neoc-assistant.git
   cd neoc-assistant
   uv sync --no-dev
   cp .env.production .env
   ```

3. **Configure systemd service**:
   ```bash
    sudo cp scripts/neoc-ai-assistant.service /etc/systemd/system/
    sudo systemctl enable neoc-ai-assistant
    sudo systemctl start neoc-ai-assistant
   ```

## Troubleshooting

### Common Issues

**Ollama connection failed**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**Import errors**
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version
python --version  # Should be 3.13+
```

**Memory issues**
```bash
# Reduce cache sizes in .env
RAG_CACHE_SIZE=100
LLM_CACHE_SIZE=25
MAX_MEMORY_MB=256
```

**Port conflicts**
```bash
# Change port in .env
API_PORT=8001

# Or find process using port
lsof -i :8000
```