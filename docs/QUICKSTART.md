# Quick Start Guide

## Installation & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Test with sample file:**
   - The browser will open automatically (or go to http://localhost:8501)
   - Click "Browse files" in the sidebar
   - Upload `sample_code.py` (included in this project)
   - Click "Analyze Code"
   - Explore the different visualization tabs!

## What to Try

### Call Tree Tab
- Select "main" as the root function
- See how main() calls other functions in a hierarchical tree

### Dependency Graph Tab
- View the full network of all functions and classes
- Blue nodes = functions, Green = classes, Orange = methods
- Zoom and pan to explore

### Class Hierarchy Tab
- See the Animal → Dog/Cat inheritance
- Hover over classes to see their methods

### Mind Map Tab
- Select different functions as the center
- See immediate callers and callees in a radial layout

### Metrics Tab
- View most called functions
- Find unused functions (unused_function will appear here!)
- See complexity statistics

## Sidebar Features

- **File list**: See all uploaded files
- **Filter by file**: Focus on specific files
- **Max call depth**: Control how deep to traverse
- **Node Search**: Search for any function/class by name
- **Node Details**: Click a node to see detailed information

## Tips

- The graph is cached - it only rebuilds when you upload new files
- Use the search feature to quickly find specific functions
- Filter by file when working with large projects
- Check the Metrics tab to identify code quality issues
