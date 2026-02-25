"""Main Streamlit application for Python code analysis and visualization.

This is the entry point for the code analysis tool. It provides a web interface
for uploading Python files, analyzing their structure, and visualizing relationships
through interactive graphs.
"""

import streamlit as st
import networkx as nx
from typing import Optional

from utils.file_handler import FileHandler
from core.parser import PythonParser
from core.analyzer import CodeAnalyzer
from core.metrics import MetricsCalculator
from visualizations.call_tree import CallTreeVisualizer
from visualizations.dependency_graph import DependencyGraphVisualizer
from visualizations.class_hierarchy import ClassHierarchyVisualizer
from visualizations.mind_map import MindMapVisualizer


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'files' not in st.session_state:
        st.session_state.files = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'parse_result' not in st.session_state:
        st.session_state.parse_result = None
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None


def process_uploaded_file(uploaded_file):
    """Process uploaded file and build analysis graph.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    """
    try:
        files = FileHandler.extract_files(uploaded_file)
        st.session_state.files = files
        
        parser = PythonParser()
        parse_result = parser.parse_files(files)
        st.session_state.parse_result = parse_result
        
        analyzer = CodeAnalyzer(parse_result)
        st.session_state.analyzer = analyzer
        
        st.success(f"Successfully parsed {len(files)} file(s)")
        
        if parse_result.errors:
            st.warning(f"Failed to parse {len(parse_result.errors)} file(s)")
            with st.expander("View parsing errors"):
                for filepath, error in parse_result.errors.items():
                    st.error(f"{filepath}: {error}")
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")


def render_sidebar():
    """Render sidebar with file upload and filters."""
    st.sidebar.title("Code Analysis Tool")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Python file or ZIP",
        type=['py', 'zip'],
        help="Upload a single .py file or a .zip containing multiple Python files"
    )
    
    if uploaded_file is not None:
        if st.sidebar.button("Analyze Code"):
            process_uploaded_file(uploaded_file)
    
    if st.session_state.files:
        st.sidebar.subheader("Files")
        file_tree = FileHandler.get_file_tree(st.session_state.files)
        for filepath in file_tree:
            st.sidebar.text(f"📄 {filepath}")
        
        st.sidebar.subheader("Filters")
        
        selected_file = st.sidebar.selectbox(
            "Filter by file",
            ["All files"] + file_tree
        )
        
        max_depth = st.sidebar.slider(
            "Max call depth",
            min_value=1,
            max_value=20,
            value=10
        )
        
        return selected_file, max_depth
    
    return None, 10


def render_metrics_panel(analyzer: CodeAnalyzer):
    """Render top metrics summary panel.
    
    Args:
        analyzer: CodeAnalyzer instance
    """
    metrics_calc = MetricsCalculator(analyzer.graph)
    summary = metrics_calc.get_summary_metrics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Functions", summary['total_functions'])
    with col2:
        st.metric("Classes", summary['total_classes'])
    with col3:
        st.metric("Methods", summary['total_methods'])
    with col4:
        st.metric("Total Nodes", summary['total_nodes'])
    with col5:
        max_depth = metrics_calc.get_max_call_depth()
        st.metric("Max Call Depth", max_depth)


def render_node_details(analyzer: CodeAnalyzer, node_id: str):
    """Render detailed information about a selected node.
    
    Args:
        analyzer: CodeAnalyzer instance
        node_id: Node ID to display details for
    """
    if node_id not in analyzer.graph:
        st.warning("Node not found")
        return
    
    node_data = analyzer.graph.nodes[node_id]
    
    st.subheader(f"📍 {node_data['name']}")
    st.write(f"**Type:** {node_data['type']}")
    st.write(f"**File:** {node_data['file']}")
    st.write(f"**Line:** {node_data['line']}")
    
    if node_data['params']:
        st.write(f"**Parameters:** {', '.join(node_data['params'])}")
    
    if node_data.get('parent_class'):
        st.write(f"**Parent Class:** {node_data['parent_class']}")
    
    if node_data.get('base_classes'):
        st.write(f"**Base Classes:** {', '.join(node_data['base_classes'])}")
    
    st.write(f"**Complexity:** {node_data.get('complexity', 1)}")
    
    callers = analyzer.get_callers(node_id)
    callees = analyzer.get_callees(node_id)
    
    if callers:
        st.write(f"**Called by ({len(callers)}):**")
        for caller in callers[:10]:
            st.text(f"  • {analyzer.graph.nodes[caller]['name']}")
    
    if callees:
        st.write(f"**Calls ({len(callees)}):**")
        for callee in callees[:10]:
            st.text(f"  • {analyzer.graph.nodes[callee]['name']}")
    
    if node_data['source']:
        with st.expander("View source code"):
            st.code(node_data['source'], language='python')


def render_call_tree_tab(analyzer: CodeAnalyzer):
    """Render call tree visualization tab.
    
    Args:
        analyzer: CodeAnalyzer instance
    """
    st.subheader("Call Tree Visualization")
    
    nodes = list(analyzer.graph.nodes())
    node_names = [analyzer.graph.nodes[n]['name'] for n in nodes]
    
    selected_name = st.selectbox(
        "Select root function",
        node_names,
        index=0 if node_names else None
    )
    
    if selected_name:
        selected_node = nodes[node_names.index(selected_name)]
        call_tree = analyzer.get_call_tree(selected_node)
        
        visualizer = CallTreeVisualizer(call_tree)
        fig = visualizer.create_tree_figure(selected_node)
        st.plotly_chart(fig, use_container_width=True)


def render_dependency_graph_tab(analyzer: CodeAnalyzer):
    """Render dependency graph visualization tab.
    
    Args:
        analyzer: CodeAnalyzer instance
    """
    st.subheader("Full Dependency Graph")
    
    visualizer = DependencyGraphVisualizer(analyzer.graph)
    visualizer.render_in_streamlit(height=600)


def render_class_hierarchy_tab(analyzer: CodeAnalyzer):
    """Render class hierarchy visualization tab.
    
    Args:
        analyzer: CodeAnalyzer instance
    """
    st.subheader("Class Hierarchy")
    
    class_hierarchy = analyzer.get_class_hierarchy()
    
    if class_hierarchy.number_of_nodes() == 0:
        st.info("No class inheritance relationships found")
        return
    
    visualizer = ClassHierarchyVisualizer(class_hierarchy)
    fig = visualizer.create_hierarchy_figure()
    st.plotly_chart(fig, use_container_width=True)


def render_mind_map_tab(analyzer: CodeAnalyzer):
    """Render mind map visualization tab.
    
    Args:
        analyzer: CodeAnalyzer instance
    """
    st.subheader("Mind Map View")
    
    nodes = list(analyzer.graph.nodes())
    node_names = [analyzer.graph.nodes[n]['name'] for n in nodes]
    
    selected_name = st.selectbox(
        "Select center node",
        node_names,
        index=0 if node_names else None,
        key="mindmap_select"
    )
    
    if selected_name:
        selected_node = nodes[node_names.index(selected_name)]
        
        visualizer = MindMapVisualizer(analyzer.graph)
        fig = visualizer.create_mind_map(selected_node)
        st.plotly_chart(fig, use_container_width=True)


def render_metrics_tab(analyzer: CodeAnalyzer):
    """Render detailed metrics tab.
    
    Args:
        analyzer: CodeAnalyzer instance
    """
    st.subheader("Code Metrics")
    
    metrics_calc = MetricsCalculator(analyzer.graph)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Most Called Functions**")
        most_called = metrics_calc.get_most_called(10)
        if most_called:
            for node_id, name, count in most_called:
                st.text(f"{name}: {count} calls")
        else:
            st.text("No data")
    
    with col2:
        st.write("**Most Dependencies**")
        most_deps = metrics_calc.get_most_dependencies(10)
        if most_deps:
            for node_id, name, count in most_deps:
                st.text(f"{name}: {count} dependencies")
        else:
            st.text("No data")
    
    st.write("**Unused Functions (No Callers)**")
    unused = metrics_calc.get_unused_functions()
    if unused:
        for node_id, name in unused[:20]:
            st.text(f"• {name}")
    else:
        st.text("All functions are called")
    
    complexity_stats = metrics_calc.get_complexity_stats()
    st.write("**Complexity Statistics**")
    st.text(f"Average: {complexity_stats['avg']:.2f}")
    st.text(f"Maximum: {complexity_stats['max']}")
    st.text(f"Minimum: {complexity_stats['min']}")
    
    high_complexity = metrics_calc.get_high_complexity_nodes(threshold=10)
    if high_complexity:
        st.write("**High Complexity Functions (≥10)**")
        for node_id, name, complexity in high_complexity:
            st.text(f"{name}: {complexity}")


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Python Code Analyzer",
        page_icon="🔍",
        layout="wide"
    )
    
    initialize_session_state()
    
    selected_file, max_depth = render_sidebar()
    
    st.title("🔍 Python Code Analysis & Visualization")
    
    if st.session_state.analyzer is None:
        st.info("👈 Upload a Python file or ZIP archive to begin analysis")
        st.markdown("""
        ### Features
        - 📊 Interactive call tree visualization
        - 🕸️ Full dependency network graph
        - 🏗️ Class inheritance hierarchy
        - 🎯 Mind map view centered on any function
        - 📈 Code quality metrics and complexity analysis
        - 🔍 Search and filter capabilities
        """)
        return
    
    analyzer = st.session_state.analyzer
    
    if selected_file and selected_file != "All files":
        filtered_graph = analyzer.filter_by_file(selected_file)
        analyzer = CodeAnalyzer(st.session_state.parse_result)
        analyzer.graph = filtered_graph
    
    render_metrics_panel(analyzer)
    
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Call Tree",
        "🕸️ Dependency Graph",
        "🏗️ Class Hierarchy",
        "🎯 Mind Map",
        "📈 Metrics"
    ])
    
    with tab1:
        render_call_tree_tab(analyzer)
    
    with tab2:
        render_dependency_graph_tab(analyzer)
    
    with tab3:
        render_class_hierarchy_tab(analyzer)
    
    with tab4:
        render_mind_map_tab(analyzer)
    
    with tab5:
        render_metrics_tab(analyzer)
    
    with st.sidebar:
        if st.session_state.analyzer:
            st.divider()
            st.subheader("Node Search")
            nodes = list(analyzer.graph.nodes())
            node_names = [analyzer.graph.nodes[n]['name'] for n in nodes]
            
            search_term = st.text_input("Search for function/class")
            if search_term:
                matches = [n for n in node_names if search_term.lower() in n.lower()]
                if matches:
                    selected = st.selectbox("Select node", matches)
                    if selected:
                        node_id = nodes[node_names.index(selected)]
                        st.session_state.selected_node = node_id
                else:
                    st.warning("No matches found")
            
            if st.session_state.selected_node:
                st.divider()
                with st.expander("Node Details", expanded=True):
                    render_node_details(analyzer, st.session_state.selected_node)


if __name__ == "__main__":
    main()
