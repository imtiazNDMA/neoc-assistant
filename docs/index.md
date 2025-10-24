# NEOC AI Assistant Documentation

Welcome to the NEOC AI Assistant documentation. This is a complete LLM application specifically adapted for disaster management, featuring comprehensive knowledge of all natural hazards, their prediction, mitigation, and prevention strategies.

## Overview

NEOC AI Assistant combines cutting-edge AI technologies with robust software engineering practices to deliver a comprehensive disaster management platform with expert knowledge of natural hazards, prediction methodologies, mitigation strategies, and prevention protocols.

### Key Features

- **Big-O Optimized**: All algorithms optimized for O(1) or O(log n) performance
- **Security First**: Comprehensive input validation and rate limiting
- **Production Ready**: Full monitoring, logging, and error handling
- **Scalable Architecture**: Modular design with dependency injection

## Quick Start

1. **Installation**
   ```bash
   uv sync
   ```

2. **Setup**
   ```bash
   python scripts/dev.py install
   ```

3. **Run**
   ```bash
   python scripts/dev.py server
   ```

## Architecture

```
neoc-ai-assistant/
├── src/neoc_assistant/     # Core application code
├── tests/                  # Comprehensive test suite
├── static/                 # Frontend assets
├── data/                   # Document storage
├── docs/                   # Documentation
└── scripts/               # Development utilities
```

## API Reference

### Chat Endpoint

```http
POST /api/chat/
Content-Type: application/json

{
  "message": "What is disaster prediction?",
  "conversation_id": "optional"
}
```

### Health Check

```http
GET /health
```

## Development

### Code Quality

```bash
# Run all checks
python scripts/dev.py all

# Format code
python scripts/dev.py format

# Run tests
python scripts/dev.py test
```

### Testing

```bash
# Unit tests
uv run pytest tests/test_*.py

# Integration tests
uv run pytest tests/test_integration.py

# With coverage
uv run pytest tests/ --cov=src/neoc_assistant
```

## Configuration

See `.env.example` for all available configuration options.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run `python scripts/dev.py all`
5. Submit a pull request