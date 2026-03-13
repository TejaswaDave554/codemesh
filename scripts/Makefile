.PHONY: help install install-dev test lint format clean run

help:
	@echo "CodeMesh - Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make run          - Run the application"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest --cov=codemesh --cov-report=html tests/

lint:
	flake8 . --exclude=venv,build,dist
	pylint codemesh --disable=C0111

format:
	black .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info htmlcov/ .pytest_cache/ .coverage

run:
	streamlit run app.py
