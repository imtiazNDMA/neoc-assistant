# Code Quality Guidelines

This document outlines the code quality standards and practices for NEOC AI Assistant.

## Code Style

### Python Standards

We follow PEP 8 with some modifications for readability and consistency.

#### Formatting
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings, single quotes for characters
- **Trailing Commas**: Always use in multi-line structures

#### Imports
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import fastapi
import uvicorn
from pydantic import BaseModel

# Local imports
from .config import config
from .llm_service import LLMService
```

#### Naming Conventions
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_CASE`
- **Private Members**: `_leading_underscore`
- **Protected Members**: `_leading_underscore`

### Code Formatting Tools

#### Black
```bash
# Format code
uv run black src/ tests/ scripts/

# Check formatting
uv run black --check src/ tests/ scripts/
```

#### isort
```bash
# Sort imports
uv run isort src/ tests/ scripts/

# Check import sorting
uv run isort --check-only src/ tests/ scripts/
```

## Linting

### flake8

Configuration in `pyproject.toml`:
```toml
[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
    ".venv",
    "node_modules"
]
```

```bash
# Run linting
uv run flake8 src/ tests/ scripts/
```

### Common Issues

#### E203: Whitespace before ':'
```python
# Bad
dict_items = {
    "key" : "value"
}

# Good
dict_items = {
    "key": "value"
}
```

#### W503: Line break before binary operator
```python
# Bad
result = (condition1
          and condition2)

# Good
result = (condition1
          and condition2)
```

## Type Checking

### mypy

Configuration in `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "chromadb.*",
    "sentence_transformers.*",
    "langchain.*",
    "langchain_core.*"
]
ignore_missing_imports = true
```

```bash
# Run type checking
uv run mypy src/neoc_assistant/
```

### Type Hints

#### Basic Types
```python
from typing import List, Dict, Optional, Union, Any

def process_data(data: List[Dict[str, Any]]) -> Optional[str]:
    """Process data and return result"""
    pass
```

#### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Response(Generic[T]):
    def __init__(self, data: T) -> None:
        self.data = data
```

#### Callbacks
```python
from typing import Callable, Awaitable

async def process_with_callback(
    data: str,
    callback: Callable[[str], Awaitable[None]]
) -> None:
    await callback(data)
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def calculate_risk_score(
    hazard_type: str,
    severity: int,
    population_density: float
) -> float:
    """Calculate risk score for a disaster scenario.

    Args:
        hazard_type: Type of natural hazard (e.g., 'earthquake', 'flood')
        severity: Severity level on scale of 1-10
        population_density: People per square kilometer

    Returns:
        Risk score between 0.0 and 1.0

    Raises:
        ValueError: If severity is outside valid range

    Example:
        >>> calculate_risk_score('earthquake', 7, 1000.0)
        0.85
    """
    if not 1 <= severity <= 10:
        raise ValueError("Severity must be between 1 and 10")

    # Implementation...
    pass
```

### Module Documentation

Each module should start with a module-level docstring:

```python
"""LLM service for NEOC AI Assistant.

This module provides the core LLM functionality including:
- Chat response generation
- RAG pipeline integration
- Response caching and optimization
"""

# Module code...
```

### API Documentation

API endpoints are documented using FastAPI's automatic documentation generation.

## Error Handling

### Exception Hierarchy

```python
class NEOCException(Exception):
    """Base exception for NEOC AI Assistant"""
    pass

class ValidationError(NEOCException):
    """Validation error"""
    pass

class LLMError(NEOCException):
    """LLM service error"""
    pass

class DocumentProcessingError(NEOCException):
    """Document processing error"""
    pass
```

### Error Handling Patterns

```python
def safe_llm_call(prompt: str) -> str:
    """Safely call LLM with proper error handling"""
    try:
        response = llm.generate(prompt)
        return response
    except TimeoutError:
        logger.error("LLM request timed out")
        raise LLMError("Request timed out")
    except Exception as e:
        logger.error(f"Unexpected LLM error: {e}")
        raise LLMError(f"LLM service error: {e}")
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_request(request_data: dict) -> dict:
    """Process a request with proper logging"""
    logger.info(f"Processing request: {request_data.get('id', 'unknown')}")

    try:
        result = perform_processing(request_data)
        logger.info("Request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        raise
```

## Security

### Input Validation

```python
from pydantic import BaseModel, validator
import re

class ChatRequest(BaseModel):
    message: str

    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')

        if len(v) > 10000:
            raise ValueError('Message too long')

        # Check for potentially harmful patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Invalid message content')

        return v.strip()
```

### Secure Defaults

```python
# Security configuration
DEFAULT_CONFIG = {
    "max_request_size": 1000,  # characters
    "rate_limit": 60,  # requests per minute
    "timeout": 30,  # seconds
    "allowed_origins": ["*"],  # Restrict in production
}
```

### Secrets Management

```python
import os
from pathlib import Path

def get_secret(key: str, default: str = None) -> str:
    """Get secret from environment or secure storage"""
    value = os.getenv(key)
    if value:
        return value

    # In production, use secure secret storage
    # For development, use .env file
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)

    if default is None:
        raise ValueError(f"Secret {key} not found")

    return default
```

## Performance

### Optimization Principles

1. **Memory Efficiency**: Use generators for large datasets
2. **Caching**: Cache expensive operations
3. **Async I/O**: Use async/await for I/O operations
4. **Lazy Loading**: Load resources on demand

### Performance Patterns

```python
from functools import lru_cache
import asyncio

@lru_cache(maxsize=100)
def cached_expensive_operation(param: str) -> dict:
    """Cache expensive operations"""
    # Expensive computation...
    return result

async def process_concurrent_requests(requests: List[dict]) -> List[dict]:
    """Process multiple requests concurrently"""
    tasks = [process_single_request(req) for req in requests]
    return await asyncio.gather(*tasks)
```

### Profiling

```python
import cProfile
import pstats
from functools import wraps

def profile_function(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        stats = pstats.Stats(profiler)
        stats.sort_stats('cumtime')
        stats.print_stats(10)

        return result
    return wrapper
```

## Testing

### Test Quality

- **Coverage**: >80% for unit tests
- **Isolation**: Tests should not depend on each other
- **Readability**: Clear test names and structure
- **Maintainability**: Easy to update when code changes

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestLLMService:
    """Test cases for LLMService"""

    @pytest.fixture
    def llm_service(self):
        """LLM service fixture"""
        from src.neoc_assistant.llm_service import LLMService
        return LLMService()

    def test_initialization(self, llm_service):
        """Test service initialization"""
        assert llm_service is not None

    def test_response_generation(self, llm_service):
        """Test response generation"""
        with patch.object(llm_service.llm, 'invoke') as mock_invoke:
            mock_invoke.return_value = Mock(content="Test response")

            result = llm_service.generate_response("Hello")
            assert result == "Test response"
```

## Code Review

### Review Checklist

- [ ] **Functionality**: Code works as intended
- [ ] **Style**: Follows code style guidelines
- [ ] **Documentation**: Adequate docstrings and comments
- [ ] **Tests**: Appropriate test coverage
- [ ] **Security**: No security vulnerabilities
- [ ] **Performance**: No obvious performance issues
- [ ] **Error Handling**: Proper exception handling
- [ ] **Type Hints**: Complete type annotations

### Review Comments

- **Be Constructive**: Focus on improvement
- **Explain Reasoning**: Why a change is needed
- **Provide Examples**: Show better alternatives
- **Ask Questions**: Seek clarification when needed

## Continuous Integration

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run tests
        run: uv run python -m pytest tests/ --cov=src/neoc_assistant
      - name: Run linting
        run: |
          uv run black --check src/ tests/
          uv run isort --check-only src/ tests/
          uv run flake8 src/ tests/
          uv run mypy src/neoc_assistant/
```

## Tools and Configuration

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "neoc-ai-assistant"
version = "2.0.0"
description = "Complete LLM application for disaster management"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    # ... other dependencies
]

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
# ... mypy configuration
```

This comprehensive code quality guide ensures that NEOC AI Assistant maintains high standards of code quality, security, and maintainability.