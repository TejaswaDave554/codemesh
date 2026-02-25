# Python Code Analysis & Visualization Tool

A Streamlit web application that parses Python project files, analyzes their structure, and visualizes function call trees, class hierarchies, and method relationships as interactive graphs.

## Features

- **File Input**: Upload single `.py` files or `.zip` archives containing multiple Python files
- **AST Parsing**: Extract functions, classes, methods, calls, and imports using Python's `ast` module
- **Interactive Visualizations**:
  - Hierarchical call tree
  - Force-directed dependency graph
  - Class inheritance hierarchy
  - Radial mind map view
- **Code Metrics**: Complexity analysis, call frequency, unused functions detection
- **Search & Filter**: Find specific functions/classes, filter by file, control visualization depth

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to the URL shown (typically `http://localhost:8501`)

3. Upload a Python file or ZIP archive using the sidebar

4. Click "Analyze Code" to parse and visualize

5. Explore different visualization tabs and use filters/search in the sidebar

## Project Structure

```
project/
├── app.py                  # Main Streamlit entry point
├── core/
│   ├── parser.py           # AST parsing logic
│   ├── analyzer.py         # Graph building and analysis
│   └── metrics.py          # Code quality metrics
├── visualizations/
│   ├── call_tree.py        # Hierarchical tree view
│   ├── dependency_graph.py # Network graph view
│   ├── class_hierarchy.py  # Inheritance view
│   └── mind_map.py         # Radial/mind map view
├── utils/
│   ├── file_handler.py     # File upload and zip extraction
│   └── helpers.py          # Shared utility functions
└── requirements.txt
```

## Technical Details

- **Parser**: Uses Python's built-in `ast` module with context stack for accurate call tracking
- **Graph**: NetworkX directed graph stores all relationships
- **Cross-file resolution**: Imports are tracked and resolved across uploaded files
- **Edge cases handled**: Recursive functions, nested functions, lambda functions, decorators
- **Session state**: Graph is cached and only rebuilt when files change

## Visualization Types

1. **Call Tree**: Top-down hierarchical view starting from a root function (e.g., main)
2. **Dependency Graph**: Force-directed network showing all functions, classes, and relationships
3. **Class Hierarchy**: Tree showing inheritance relationships with methods on hover
4. **Mind Map**: Radial layout centered on selected node showing immediate connections

## Color Coding

- Blue: Functions
- Green: Classes
- Orange: Methods
- Red: Center node (mind map) / Inheritance edges

## Metrics Provided

- Total functions, classes, methods count
- Most called functions (top 10)
- Functions with no callers (potentially unused)
- Maximum call depth
- Functions with most dependencies
- Cyclomatic complexity statistics
