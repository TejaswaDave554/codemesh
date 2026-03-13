# External Dependencies & Collapse System Implementation

## 🎯 Features Implemented

### 1. **External Dependency Detection**
- **File:** `managers/external_detector.py`
- Automatically detects and classifies imports:
  - `stdlib` - Standard library (os, sys, json, etc.)
  - `third_party` - Installed packages (pandas, numpy, etc.)
  - `builtin` - Built-in modules (math, time, etc.)
  - `internal` - Your project code

### 2. **Collapse Management System**
- **File:** `managers/collapse_manager.py`
- Universal collapse/expand for any node type
- Tracks parent-child relationships
- Manages visibility state
- Supports grouping external dependencies

### 3. **External Grouping**
- **File:** `managers/external_grouper.py`
- Groups external dependencies by type
- Creates collapsed group nodes with counts
- Icons for different package types:
  - 📚 Standard Library
  - 📦 Third Party
  - ⚙️ Built-ins

### 4. **Enhanced CodeNode**
- **File:** `core/parser.py`
- Added new fields:
  - `is_external` - Boolean flag
  - `package_name` - Package name (e.g., 'pandas')
  - `package_type` - Classification (stdlib/third_party/builtin)
  - `external_calls` - Set of external function calls
  - `is_collapsed` - Collapse state
  - `children` - Child nodes for grouping
  - `parent_group` - Parent group reference

### 5. **Edge Styling System**
- **File:** `managers/edge_styler.py`
- Different styles for different relationships:
  - **Internal calls:** Solid blue lines
  - **Standard library:** Dashed orange lines
  - **Third party:** Dotted red lines
  - **Built-ins:** Dash-dot purple lines
  - **Inheritance:** Solid red lines
  - **File usage:** Dotted orange lines

### 6. **Glow Effect**
- **File:** `visualizations/dependency_graph.py`
- Orange glow around nodes with external dependencies
- Size based on complexity
- Subtle visual indicator without clutter

### 7. **Enhanced UI Controls**
- **File:** `ui/sidebar.py`
- New sidebar section: "🔌 External Dependencies"
- Controls:
  - ☑ Show External Packages
  - Display Mode (Collapsed/Individual)
  - Package type filters (stdlib/third_party/builtin)
  - Visual effects (glow/edge styling)

## 🎨 Visual Features

### Default View (Collapsed)
```
Your Code:
  function_a() [glow] ──────→ function_b()
                      ┈┈┈┈┈→ 📚 Standard Library (5)
                      ······→ 📦 Third Party (3)
```

### Expanded View
```
Your Code:
  function_a() [glow] ──────→ function_b()
                      ┈┈┈┈┈→ os.path.join()
                      ┈┈┈┈┈→ sys.argv
                      ······→ pandas.read_csv()
                      ······→ numpy.array()
```

### Visual Elements
- **Glow Effect:** Orange halo around nodes with external deps
- **Edge Styles:** Different line patterns for different types
- **Node Colors:** Color-coded by package type
- **Group Icons:** Visual indicators for package categories
- **Hover Info:** Enhanced tooltips with package information

## 🔧 Technical Implementation

### Parser Enhancement
```python
# Automatically detects external imports
def _process_external_import(self, module_name, result, filepath):
    if self.external_detector.is_external(module_name):
        package_type = self.external_detector.classify_import(module_name)
        # Creates external nodes with metadata
```

### Analyzer Enhancement
```python
# Creates grouped external nodes
def _create_external_groups(self):
    groups = self.external_grouper.create_groups(self.parse_result.nodes)
    group_nodes = self.external_grouper.create_group_nodes(groups)
    # Adds to graph with collapse state
```

### Visualization Enhancement
```python
# Glow effect for nodes with external dependencies
def _create_glow_trace(self, pos):
    for node in pos:
        if self._has_external_calls(node):
            # Add glow effect
```

## 🎛️ User Controls

### Sidebar Controls
1. **Show External Packages** - Toggle visibility
2. **Display Mode** - Collapsed groups vs individual functions
3. **Package Filters** - Show/hide specific types
4. **Visual Effects** - Enable/disable glow and edge styling

### Interactive Features
- Click to expand/collapse groups
- Hover for detailed information
- Filter by package type
- Toggle visual effects

## 📊 Benefits

### Clean Default View
- External dependencies grouped and collapsed
- Focus on your code structure
- Minimal visual clutter

### Detailed When Needed
- Expand to see individual external functions
- Glow effect highlights external usage
- Edge styling shows relationship types

### User Control
- Toggle features on/off
- Filter by package type
- Choose display mode

### Universal System
- Collapse works for any node type
- Extensible to classes, modules, etc.
- Consistent across all visualizations

## 🚀 Result

✅ **Clean visualization** with external dependencies properly managed
✅ **Glow effects** highlight nodes with external calls
✅ **Edge styling** differentiates relationship types
✅ **Grouped clusters** organize external packages
✅ **Universal collapse** system for any node
✅ **User controls** for customization
✅ **Enhanced tooltips** with package information

The system now provides a sophisticated way to visualize external dependencies without cluttering the main code structure view!