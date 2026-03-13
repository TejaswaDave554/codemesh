# CodeMesh - Quick Reference

## 📂 Project Structure (Clean & Organized!)

```
codemesh/
├── 📄 app.py                   # START HERE - Main application
├── 📄 README.md                # Project overview
├── 📄 LICENSE                  # MIT License
├── 📄 requirements.txt         # Dependencies
├── 📄 requirements-dev.txt     # Dev dependencies
│
├── ⚙️  config/                 # All configuration
├── 🧠 core/                    # Core logic
├── 🔧 utils/                   # Utilities
├── 📊 visualizations/          # Visualizations
├── 📚 docs/                    # Documentation
├── 💡 examples/                # Sample files
├── 🧪 tests/                   # Tests
├── 🛠️  scripts/                # Build tools
└── 📦 lib/                     # External libs
```

## 🚀 Quick Commands

```bash
# Install and run
pip install -r requirements.txt
streamlit run app.py

# Development
pip install -r requirements-dev.txt
pytest tests/
black .
flake8 .
```

## 📝 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `config/config.py` | App settings |
| `config/constants.py` | Constants |
| `config/exceptions.py` | Custom exceptions |
| `core/parser.py` | AST parsing |
| `core/analyzer.py` | Graph analysis |
| `core/metrics.py` | Code metrics |

## 📖 Documentation

- [Quick Start](docs/QUICKSTART.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Complete Summary](docs/COMPLETE_SUMMARY.md)
- [Final Organization](docs/FINAL_ORGANIZATION.md)

## 🎯 What's Different?

**Before:** 20+ files cluttering root directory
**After:** 7 essential files, everything organized!

All configuration → `config/`
All documentation → `docs/`
All examples → `examples/`
All tests → `tests/`
All scripts → `scripts/`

Clean, professional, easy to navigate! ✨
