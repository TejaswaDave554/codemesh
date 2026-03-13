# Interactive Collapsible Tree Implementation

## 🎯 Features Implemented

### 1. **Fully Interactive Collapse/Expand**
- **Click Detection:** Nodes respond to clicks in real-time
- **Session State:** Collapse state persists across interactions
- **Visual Feedback:** Immediate update when toggling nodes
- **Smart Rerun:** Only reruns when state changes

### 2. **Built-in Function Filtering**
- **Automatic Filtering:** Removes all external/built-in Python functions
- **Clean Tree:** Shows only your project's internal code
- **No Clutter:** Standard library calls (print, len, etc.) excluded
- **Focus on Your Code:** Only functions/classes you wrote

### 3. **Enhanced Controls**

#### Action Buttons
- **🔄 Expand All** - Opens all collapsed nodes
- **📦 Collapse All** - Collapses all parent nodes
- **Root Node Selector** - Choose starting point for tree

#### Visual Indicators
- **▶ Orange Square** - Collapsed node (click to expand)
- **▼ Blue Diamond** - Expanded node (click to collapse)
- **● Colored Circle** - Leaf node (no children)

### 4. **Smart Root Detection**
Automatically finds the best root node:
1. Looks for `main()` function (if exists)
2. Finds entry points (nodes with no incoming calls)
3. Selects first internal function
4. Filters out all external nodes

## 🎨 How It Works

### Filtering External Nodes
```python
# Removes from tree:
- Python built-ins: print(), len(), range(), etc.
- Standard library: os.path.join(), sys.argv, etc.
- Third-party packages: pandas.read_csv(), numpy.array(), etc.

# Keeps in tree:
- Your functions
- Your classes
- Your methods
```

### Interactive Collapse
```
1. User clicks node with ▶ or ▼
2. System detects click via Plotly selection
3. Updates session state (add/remove from collapsed set)
4. Reruns visualization with new state
5. Tree updates instantly
```

### Session State Management
```python
st.session_state.tree_collapsed_nodes = {node_id1, node_id2, ...}
st.session_state.tree_root_node = selected_root_id
```

## 📊 Visual States

### Collapsed Node (▶)
```
▶ function_name
  (children hidden)
```
- Orange square marker
- Shows ▶ symbol
- Click to expand and show children

### Expanded Node (▼)
```
▼ function_name
  ├─ child1
  ├─ child2
  └─ child3
```
- Blue diamond marker
- Shows ▼ symbol
- Click to collapse and hide children

### Leaf Node (●)
```
● function_name
  (no children)
```
- Colored circle (by type)
- No expand/collapse symbol
- Not clickable (no children to show)

## 🎛️ User Interface

### Top Controls
```
[Info Banner: Click nodes to expand/collapse]
[🔄 Expand All] [📦 Collapse All]
[Root Node Selector: dropdown]
```

### Interaction Flow
1. **Select Root:** Choose starting function from dropdown
2. **View Tree:** See hierarchical structure
3. **Click Nodes:** Toggle expand/collapse
4. **Navigate:** Zoom and pan as needed
5. **Reset:** Use Expand/Collapse All buttons

## 💡 Usage Examples

### Example 1: Exploring Large Codebase
```
1. Start with root collapsed
2. Click 📦 Collapse All
3. Expand only functions of interest
4. Focus on specific code paths
```

### Example 2: Understanding Call Flow
```
1. Select main() as root
2. Click 🔄 Expand All
3. See complete call hierarchy
4. Trace execution path top-down
```

### Example 3: Finding Specific Function
```
1. Choose different root nodes
2. Expand branches selectively
3. Locate target function
4. See its children/dependencies
```

## 🔧 Technical Implementation

### External Node Filtering
```python
def _filter_internal_only(graph):
    """Remove all external nodes from graph."""
    filtered = nx.DiGraph()
    
    for node, data in graph.nodes(data=True):
        if not data.get('is_external', False):
            filtered.add_node(node, **data)
    
    # Only keep edges between internal nodes
    for source, target in graph.edges():
        if source in filtered and target in filtered:
            filtered.add_edge(source, target)
    
    return filtered
```

### Click Detection
```python
# Plotly on_select event
selected_points = st.plotly_chart(
    fig,
    on_select="rerun",
    selection_mode="points"
)

# Process clicks
if selected_points.selection['points']:
    clicked_node = get_node_from_index(point_index)
    toggle_collapse(clicked_node)
    st.rerun()
```

### State Persistence
```python
# Initialize state
if 'tree_collapsed_nodes' not in st.session_state:
    st.session_state.tree_collapsed_nodes = set()

# Toggle node
if node in st.session_state.tree_collapsed_nodes:
    st.session_state.tree_collapsed_nodes.discard(node)  # Expand
else:
    st.session_state.tree_collapsed_nodes.add(node)  # Collapse
```

## 📈 Benefits

### Before
```
❌ Static tree (no interaction)
❌ Shows all Python built-ins
❌ Cluttered with external calls
❌ No way to focus on specific areas
❌ Overwhelming for large codebases
```

### After
```
✅ Fully interactive (click to toggle)
✅ Only shows your code
✅ Clean, focused view
✅ Explore at your own pace
✅ Manageable for any codebase size
```

## 🎯 Best Practices

### For Large Codebases
1. Start with everything collapsed
2. Expand only relevant branches
3. Use root selector to change perspective
4. Focus on one module at a time

### For Understanding Flow
1. Select entry point (main, __init__, etc.)
2. Expand all to see full hierarchy
3. Trace execution path
4. Identify bottlenecks or complexity

### For Code Review
1. Select function being reviewed
2. Expand to see dependencies
3. Check what it calls
4. Verify no unexpected dependencies

## 🚀 Performance

### Optimizations
- **Lazy Loading:** Only calculates visible nodes
- **Efficient Layout:** Caches subtree widths
- **Smart Filtering:** Removes external nodes early
- **Session State:** Avoids recalculation

### Scalability
- Handles 100+ internal nodes smoothly
- Collapse reduces visible nodes
- Zoom/pan for navigation
- No performance degradation

## 🔍 Troubleshooting

### "No internal nodes found"
- Your code only calls external functions
- No functions/classes defined in uploaded files
- Check that files were parsed correctly

### "Tree looks empty"
- All nodes might be collapsed
- Click 🔄 Expand All
- Try different root node

### "Can't click nodes"
- Only nodes with children are clickable
- Leaf nodes (●) have no children
- Look for ▶ or ▼ symbols

## 📚 Related Features

- **Dependency Graph:** See all relationships at once
- **Call Tree:** Traditional hierarchical view
- **Class Hierarchy:** Focus on class relationships
- **External Dependencies:** Toggle to show/hide external calls

The collapsible tree now provides a clean, interactive way to explore your code structure without the noise of built-in functions!
