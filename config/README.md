# Configuration Directory

This directory contains all configuration files for the CodeMesh application.

## Files

### Application Configuration
- **config.py**: Application settings (UI, analysis, logging, export)
- **constants.py**: Application constants (file sizes, thresholds, colors)
- **exceptions.py**: Custom exception classes

### Build & Test Configuration
- **pyproject.toml**: Modern Python packaging configuration
- **setup.py**: Legacy setup configuration
- **pytest.ini**: Pytest test configuration

### Environment
- **.env.example**: Environment variables template (copy to `.env` and customize)

## Usage

### Environment Variables

Copy `.env.example` to `.env` in the project root:

```bash
cp config/.env.example .env
```

Then customize the values as needed.

### Importing Configuration

```python
from config import APP_CONFIG, UI_CONFIG, ANALYSIS_CONFIG
from config.constants import MAX_FILE_SIZE_MB
from config.exceptions import FileSizeError
```
