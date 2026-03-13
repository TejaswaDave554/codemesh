# Scripts Directory

This directory contains build scripts and development tools.

## Files

- **Makefile**: Common development tasks (install, test, lint, format, run)

## Usage

```bash
# From project root
make install      # Install dependencies
make test         # Run tests
make format       # Format code
make lint         # Run linters
make run          # Run application
make clean        # Clean build artifacts
```

For Windows users without `make`, you can run commands directly:

```bash
pip install -r requirements.txt
pytest tests/
black .
flake8 .
streamlit run app.py
```
