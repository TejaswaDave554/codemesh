# CodeMesh - Python Code Analysis & Visualization Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Streamlit web application that parses Python projects, analyzes their structure, and visualizes function call trees, class hierarchies, and method relationships as interactive graphs.

## ✨ Features

- **File Input**: Upload single `.py` files or `.zip` archives
- **AST Parsing**: Extract functions, classes, methods, calls, and imports
- **Interactive Visualizations**: Call trees, dependency graphs, class hierarchies, mind maps
- **Code Metrics**: Complexity analysis, call frequency, unused functions detection
- **Search & Filter**: Find specific functions/classes, filter by file
- **Export**: Download analysis as JSON or CSV

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

Open your browser to `http://localhost:8501` and upload Python files to analyze.

## 📁 Project Structure

```
codemesh/
├── app.py              # Main application (120 lines)
├── config/             # Configuration and constants
├── core/               # Core parsing and analysis
├── ui/                 # UI components (modular)
├── utils/              # Utility functions
├── visualizations/     # Visualization modules
├── docs/               # Documentation
├── examples/           # Sample files
├── tests/              # Test suite
└── scripts/            # Build and dev scripts
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Quick Reference](docs/QUICK_REFERENCE.md)
- [Ultimate Summary](docs/ULTIMATE_SUMMARY.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .

# Run linters
flake8 .
```

See [scripts/Makefile](scripts/Makefile) for more commands.

## 📋 Requirements

- Python 3.8+
- streamlit >= 1.28.0
- networkx >= 3.0
- plotly >= 5.17.0
- pyvis >= 0.3.2
- pandas >= 2.0.0

## 🔒 Security

- Path traversal protection
- Zip bomb detection
- File size validation
- Input sanitization
- Comprehensive validation layer

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## 🎯 Status

**Production Ready** ✅ | **Security Hardened** 🔒 | **Fully Modular** 📦
