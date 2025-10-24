# Testing Guide

This guide covers the testing strategy and practices for NEOC AI Assistant.

## Testing Strategy

### Test Types

#### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Focus on business logic
- Located in `tests/unit/`

#### Integration Tests
- Test component interactions
- Use real dependencies where possible
- Test API endpoints
- Located in `tests/integration/`

#### End-to-End Tests
- Test complete user workflows
- Use the running application
- Validate user experience
- Located in `tests/e2e/`

#### Performance Tests
- Validate performance requirements
- Test under load
- Monitor resource usage
- Located in `scripts/performance_tune.py`

## Running Tests

### All Tests
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ -v --cov=src/neoc_assistant --cov-report=html
```

### Specific Test Types
```bash
# Unit tests only
uv run python -m pytest tests/unit/ -v

# Integration tests only
uv run python -m pytest tests/integration/ -v

# End-to-end tests
uv run python -m pytest tests/e2e/ -v
```

### Test a Specific File
```bash
uv run python -m pytest tests/unit/test_llm_service.py -v
```

### Run Tests in Parallel
```bash
uv run python -m pytest tests/ -n auto
```

## Writing Tests

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestLLMService:
    """Test cases for LLMService"""

    def test_initialization(self):
        """Test service initialization"""
        from src.neoc_assistant.llm_service import LLMService

        service = LLMService()
        assert service is not None
        assert service.llm is not None

    def test_chat_response(self):
        """Test chat response generation"""
        from src.neoc_assistant.llm_service import LLMService

        service = LLMService()

        # Mock the LLM chain
        with patch.object(service.chat_chain, 'invoke') as mock_invoke:
            mock_invoke.return_value = "Test response"

            result = service.generate_response("Hello")
            assert result == "Test response"
            mock_invoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operations"""
        # Async test example
        pass
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names that explain what is being tested

### Fixtures

```python
import pytest

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "model_name": "test-model",
        "temperature": 0.5
    }

@pytest.fixture
def llm_service(sample_config):
    """LLM service fixture"""
    from src.neoc_assistant.llm_service import LLMService
    return LLMService(config=sample_config)
```

### Mocking

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mocking():
    """Example of mocking external dependencies"""
    with patch('src.neoc_assistant.llm_service.Ollama') as mock_ollama:
        mock_instance = Mock()
        mock_ollama.return_value = mock_instance

        from src.neoc_assistant.llm_service import LLMService
        service = LLMService()

        # Test with mocked dependency
        assert service.llm == mock_instance
```

## Test Coverage

### Coverage Goals

- **Unit Tests**: >80% coverage
- **Integration Tests**: Key integration points
- **E2E Tests**: Critical user journeys

### Coverage Report

```bash
# Generate HTML coverage report
uv run python -m pytest tests/ --cov=src/neoc_assistant --cov-report=html

# View report in browser
# Open htmlcov/index.html
```

### Coverage Configuration

Coverage configuration is in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src/neoc_assistant"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

## Performance Testing

### Load Testing

```bash
# Run performance validation
uv run python scripts/uat_validation.py
```

### Profiling

```python
import cProfile
import pstats

def profile_function():
    """Profile a function"""
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = expensive_function()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(10)  # Top 10 functions

    return result
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Function to profile memory usage"""
    # Code that uses significant memory
    pass
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Push to main branch
- Pull requests
- Scheduled runs

### CI Pipeline

1. **Linting**: `black`, `isort`, `flake8`, `mypy`
2. **Security**: `bandit`, `safety`
3. **Tests**: `pytest` with coverage
4. **Build**: Package build verification
5. **Integration**: Docker image build

### Local CI

```bash
# Run all CI checks locally
uv run python -m pytest tests/ --cov=src/neoc_assistant
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run flake8 src/ tests/
uv run mypy src/neoc_assistant/
```

## Test Data

### Test Data Management

- Use fixtures for test data
- Avoid hardcoding test data
- Use factories for complex objects
- Clean up after tests

### Sample Data

```python
@pytest.fixture
def sample_disaster_query():
    """Sample disaster management query"""
    return {
        "message": "What are the main types of natural disasters?",
        "expected_keywords": ["earthquake", "flood", "hurricane"]
    }

@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "title": "Earthquake Preparedness",
            "content": "Earthquake preparedness involves...",
            "metadata": {"type": "guide", "category": "earthquake"}
        }
    ]
```

## Debugging Tests

### Common Issues

1. **Import Errors**: Check Python path
2. **Mock Issues**: Verify mock targets
3. **Async Tests**: Use `@pytest.mark.asyncio`
4. **Fixture Errors**: Check fixture dependencies

### Debugging Tools

```python
# Add debug prints
def test_debug():
    result = some_function()
    print(f"Debug: result = {result}")  # Temporary debug
    assert result is not None

# Use pytest breakpoints
def test_with_breakpoint():
    result = some_function()
    breakpoint()  # Will drop into debugger
    assert result is not None
```

### Test Isolation

- Each test should be independent
- Use unique test data
- Clean up resources
- Avoid test interdependencies

## Best Practices

### Test Quality

- **Readable**: Clear test names and structure
- **Maintainable**: Easy to update when code changes
- **Fast**: Tests should run quickly
- **Reliable**: Tests should not be flaky

### Test Organization

```
tests/
├── unit/
│   ├── test_llm_service.py
│   ├── test_rag_pipeline.py
│   └── test_security.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_document_processing.py
├── e2e/
│   ├── test_chat_workflow.py
│   └── test_document_upload.py
├── conftest.py
└── fixtures.py
```

### Test Documentation

- Document complex test scenarios
- Explain test data requirements
- Note any special setup needed
- Include links to related issues

## Troubleshooting

### Test Failures

1. **Check Dependencies**: Ensure all dependencies are installed
2. **Environment**: Verify test environment matches production
3. **Data**: Check test data is valid
4. **Mocks**: Verify mocks are set up correctly

### Performance Issues

1. **Slow Tests**: Profile and optimize
2. **Memory Leaks**: Check for proper cleanup
3. **Resource Contention**: Run tests in isolation
4. **External Dependencies**: Mock slow external calls

### CI Issues

1. **Environment Differences**: Test locally first
2. **Dependency Conflicts**: Check dependency versions
3. **Timeout Issues**: Increase timeouts or optimize tests
4. **Resource Limits**: Check CI resource allocation