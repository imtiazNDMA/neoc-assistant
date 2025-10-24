# Contributing to NEOC AI Assistant

Thank you for your interest in contributing to NEOC AI Assistant! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.9+
- [uv](https://astral.sh/uv) package manager
- [Ollama](https://ollama.ai/) for local LLM inference
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/neoc-ai-assistant.git
   cd neoc-ai-assistant
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

4. **Run the application**
   ```bash
   # For development with hot reload
   uv run python main.py --reload

   # Or use the batch file
   ./dev_tools.bat
   ```

## Development Workflow

### 1. Choose an Issue

- Check the [GitHub Issues](https://github.com/your-org/neoc-ai-assistant/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes

- Follow the [code quality guidelines](code-quality.md)
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Test Your Changes

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ -v --cov=src/neoc_assistant --cov-report=html

# Run linting and type checking
uv run black src/ tests/ scripts/
uv run isort src/ tests/ scripts/
uv run flake8 src/ tests/ scripts/
uv run mypy src/neoc_assistant/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Follow conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring

### 6. Create a Pull Request

- Push your branch to GitHub
- Create a pull request with a clear description
- Reference any related issues
- Ensure CI checks pass

## Code Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings in Google style
- Maximum line length: 88 characters (Black default)

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_CASE`
- Private methods: `_leading_underscore`

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Don't expose sensitive information

### Testing

- Write unit tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Test both success and failure cases

## Architecture Guidelines

### Component Structure

- Keep components loosely coupled
- Use dependency injection
- Follow single responsibility principle
- Document component interfaces

### Performance

- Optimize for memory usage
- Use caching where appropriate
- Profile performance-critical code
- Consider async/await for I/O operations

### Security

- Validate all inputs
- Use secure defaults
- Follow OWASP guidelines
- Log security events

## Documentation

### Code Documentation

- All public functions/methods must have docstrings
- Include parameter types and descriptions
- Document return values and exceptions
- Provide usage examples where helpful

### User Documentation

- Update relevant docs for user-facing changes
- Include screenshots for UI changes
- Test documentation examples
- Keep API documentation current

## Review Process

### Pull Request Reviews

- At least one maintainer must approve
- All CI checks must pass
- Review focuses on code quality, tests, and documentation
- Constructive feedback is encouraged

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backwards compatibility maintained

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/your-org/neoc-ai-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/neoc-ai-assistant/discussions)
- **Documentation**: Check the docs/ directory
- **Community**: Join our Discord/Slack channel

## Recognition

Contributors are recognized in:
- GitHub repository contributors
- CHANGELOG.md for significant contributions
- Release notes
- Project documentation

Thank you for contributing to NEOC AI Assistant! 🌟