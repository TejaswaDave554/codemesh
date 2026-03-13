"""Sidebar UI component for file upload and filters."""

import streamlit as st
from typing import Tuple, Optional, List

from config.config import APP_CONFIG, UI_CONFIG, ANALYSIS_CONFIG
from utils.file_handler import FileHandler


def render_sidebar(process_callback, clear_callback) -> Tuple[Optional[str], int, int]:
    """Render sidebar with file upload and filters."""
    st.sidebar.title("🔍 CodeMesh")
    st.sidebar.markdown("### Python Code Analyzer")
    
    uploaded_files = st.sidebar.file_uploader(
        "Upload Python files or ZIP",
        type=ANALYSIS_CONFIG['supported_extensions'],
        accept_multiple_files=True,
        help=f"Upload multiple .py files or .zip archives (max {APP_CONFIG['max_file_size_mb']}MB total)"
    )
    
    if uploaded_files:
        if st.sidebar.button("🚀 Analyze Code", type="primary"):
            process_callback(uploaded_files)
    
    if st.session_state.get('files'):
        st.sidebar.markdown("---")
        st.sidebar.subheader("📁 Files")
        
        files_hash = str(hash(str(sorted(st.session_state.files.keys()))))
        file_tree = _get_cached_file_tree(files_hash, st.session_state.files)
        
        with st.sidebar.expander(f"View {len(file_tree)} files", expanded=UI_CONFIG['file_tree_expanded']):
            for filepath in file_tree:
                st.text(f"📄 {filepath}")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Filters")
        
        selected_file = st.sidebar.selectbox(
            "Filter by file",
            ["All files"] + file_tree,
            key="file_filter"
        )
        
        sort_by = st.sidebar.radio(
            "Sort functions by",
            ["Most Called", "Highest Complexity", "Alphabetical"],
            key="sort_option"
        )
        
        st.session_state.sort_by = {
            "Most Called": "calls",
            "Highest Complexity": "complexity",
            "Alphabetical": "name"
        }[sort_by]
        
        max_depth = st.sidebar.slider(
            "Max call depth",
            min_value=UI_CONFIG['max_depth_range'][0],
            max_value=UI_CONFIG['max_depth_range'][1],
            value=UI_CONFIG['max_depth_default'],
            key="max_depth"
        )
        
        display_limit = st.sidebar.slider(
            "Display limit",
            min_value=UI_CONFIG['display_limit_range'][0],
            max_value=UI_CONFIG['display_limit_range'][1],
            value=UI_CONFIG['display_limit_default'],
            key="display_limit"
        )
        
        if st.sidebar.button("🗑️ Clear Analysis", help="Clear current analysis and start fresh"):
            clear_callback()
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Function Filtering")
        
        # Toggle for unused functions with more prominent button style
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📊 Core Only", 
                        type="primary" if not st.session_state.get('show_unused', False) else "secondary",
                        help="Show only functions that are called by other functions",
                        key="core_only_btn"):
                st.session_state.show_unused = False
        
        with col2:
            if st.button("📋 Show All", 
                        type="primary" if st.session_state.get('show_unused', False) else "secondary",
                        help="Include unused and isolated functions",
                        key="show_all_btn"):
                st.session_state.show_unused = True
        
        # Display current mode
        current_mode = "All Functions" if st.session_state.get('show_unused', False) else "Core Functions Only"
        st.sidebar.caption(f"Current: {current_mode}")
        
        minimal_view = st.sidebar.checkbox(
            "Minimal View", 
            value=True, 
            key="minimal_view",
            help="Remove redundant methods (__init__, __str__, getters/setters) that clutter visualizations. Focuses on core business logic."
        )
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📐 Visualization Settings")
        
        viz_height = st.sidebar.slider(
            "Graph Height (px)",
            min_value=400,
            max_value=1200,
            value=800,
            step=50,
            key="viz_height",
            help="Adjust visualization canvas height"
        )
        
        node_spacing = st.sidebar.slider(
            "Node Spacing",
            min_value=1.0,
            max_value=5.0,
            value=2.5,
            step=0.5,
            key="node_spacing",
            help="Increase for less crowded graphs"
        )
        
        layout_algorithm = st.sidebar.selectbox(
            "Layout Algorithm",
            ["Spring (Force-Directed)", "Circular", "Hierarchical", "Kamada-Kawai"],
            key="layout_algorithm",
            help="Different layouts for different graph structures"
        )
        
        show_labels = st.sidebar.checkbox("Show Node Labels", value=True, key="show_labels")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔌 External Dependencies")
        
        show_external = st.sidebar.checkbox("Show External Packages", value=True, key="show_external")
        
        if show_external:
            group_mode = st.sidebar.radio(
                "Display Mode",
                ["Collapsed Groups", "Individual Functions"],
                key="group_mode"
            )
            
            st.sidebar.markdown("**Package Types:**")
            show_stdlib = st.sidebar.checkbox("Standard Library", value=True, key="show_stdlib")
            show_third_party = st.sidebar.checkbox("Third Party", value=True, key="show_third_party")
            show_builtin = st.sidebar.checkbox("Built-ins", value=False, key="show_builtin")
            
            st.sidebar.markdown("**Visual Effects:**")
            show_glow = st.sidebar.checkbox("Glow Effect", value=True, key="show_glow")
            edge_styling = st.sidebar.checkbox("Styled Edges", value=True, key="edge_styling")
        
        return selected_file, max_depth, display_limit
    
    return None, UI_CONFIG['max_depth_default'], UI_CONFIG['display_limit_default']


@st.cache_data(ttl=APP_CONFIG['cache_ttl_seconds'])
def _get_cached_file_tree(files_hash: str, files: dict) -> List[str]:
    """Cache file tree computation."""
    return FileHandler.get_file_tree(files)
