# Contributing to CodeMesh

Thank you for your interest in contributing to CodeMesh!

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Running Tests

```bash
pytest tests/
```

For coverage report:
```bash
pytest --cov=codemesh tests/
```

## Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run before committing:
```bash
black .
flake8 .
mypy .
```

## Project Structure

- `core/` - Core parsing and analysis logic
- `visualizations/` - Visualization modules
- `utils/` - Utility functions
- `tests/` - Unit tests
- `examples/` - Sample files
- `docs/` - Documentation

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## Reporting Issues

Please use GitHub Issues to report bugs or request features. Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
