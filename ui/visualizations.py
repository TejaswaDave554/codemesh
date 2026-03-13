"""Visualizations UI component."""

import streamlit as st
from typing import Optional
from core.analyzer import CodeAnalyzer
from config.config import ERROR_MESSAGES
from utils.validation import sanitize_depth
from visualizations.call_tree import CallTreeVisualizer
from visualizations.dependency_graph import DependencyGraphVisualizer
from visualizations.class_hierarchy import ClassHierarchyVisualizer
from visualizations.mind_map import MindMapVisualizer


def render_visualizations(analyzer: CodeAnalyzer, selected_file: Optional[str], max_depth: int) -> None:
    """Render visualization tabs."""
    if not analyzer or not analyzer.graph or analyzer.graph.number_of_nodes() == 0:
        st.info(ERROR_MESSAGES['no_files'])
        return
    
    max_depth = sanitize_depth(max_depth)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Call Tree",
        "🕸️ Dependency Graph",
        "🏛️ Class Hierarchy",
        "🧠 Mind Map"
    ])
    
    with tab1:
        _render_call_tree(analyzer, max_depth)
    
    with tab2:
        _render_dependency_graph(analyzer)
    
    with tab3:
        _render_class_hierarchy(analyzer)
    
    with tab4:
        _render_mind_map(analyzer)


def _render_call_tree(analyzer: CodeAnalyzer, max_depth: int) -> None:
    """Render call tree visualization."""
    try:
        viz_height = st.session_state.get('viz_height', 800)
        
        # Use filtered graph for cleaner visualization
        filtered_graph = analyzer.get_filtered_graph(
            show_external=st.session_state.get('show_external', True),
            show_unused=st.session_state.get('show_unused', False),
            minimal_view=st.session_state.get('minimal_view', True)
        )
        
        visualizer = CallTreeVisualizer(filtered_graph)
        fig = visualizer.create_interactive_plot(max_depth=max_depth)
        if fig:
            fig.update_layout(height=viz_height)
            st.plotly_chart(fig, use_container_width=True, config={
                'scrollZoom': True,
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['pan2d', 'select2d', 'lasso2d'],
                'modeBarButtonsToRemove': ['autoScale2d'],
                'doubleClick': 'reset+autosize'
            })
        else:
            st.warning("Unable to generate call tree")
    except Exception as e:
        st.error(f"Error rendering call tree: {str(e)}")


def _render_dependency_graph(analyzer: CodeAnalyzer) -> None:
    """Render dependency graph visualization."""
    try:
        show_glow = st.session_state.get('show_glow', True)
        edge_styling = st.session_state.get('edge_styling', True)
        show_external = st.session_state.get('show_external', True)
        node_spacing = st.session_state.get('node_spacing', 2.5)
        layout_algorithm = st.session_state.get('layout_algorithm', 'Spring (Force-Directed)')
        show_labels = st.session_state.get('show_labels', True)
        viz_height = st.session_state.get('viz_height', 800)
        
        graph = analyzer.get_filtered_graph(
            show_external=show_external,
            show_unused=st.session_state.get('show_unused', False),
            minimal_view=st.session_state.get('minimal_view', True)
        )
        
        num_nodes = graph.number_of_nodes()
        original_nodes = analyzer.graph.number_of_nodes()
        
        if st.session_state.get('minimal_view', True) and num_nodes < original_nodes:
            reduction = ((original_nodes - num_nodes) / original_nodes) * 100
            st.info(f"📊 Displaying {num_nodes} nodes (filtered from {original_nodes}, {reduction:.0f}% noise reduction) | Use sidebar buttons to toggle unused functions | Mouse wheel to zoom | Drag to pan")
        else:
            st.info(f"📊 Displaying {num_nodes} nodes | Use sidebar buttons to toggle unused functions | Mouse wheel to zoom | Drag to pan")
        
        visualizer = DependencyGraphVisualizer(
            graph, 
            show_glow=show_glow,
            edge_styling=edge_styling,
            show_external=show_external,
            node_spacing=node_spacing,
            layout_algorithm=layout_algorithm,
            show_labels=show_labels,
            height=viz_height
        )
        fig = visualizer.create_interactive_plot()
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={
                'scrollZoom': True,
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d', 'select2d'],
                'modeBarButtonsToRemove': ['autoScale2d'],
                'doubleClick': 'reset+autosize'
            })
        else:
            st.warning("Unable to generate dependency graph")
    except Exception as e:
        st.error(f"Error rendering dependency graph: {str(e)}")


def _render_class_hierarchy(analyzer: CodeAnalyzer) -> None:
    """Render class hierarchy visualization."""
    try:
        viz_height = st.session_state.get('viz_height', 800)
        
        # Use filtered graph for cleaner visualization
        filtered_graph = analyzer.get_filtered_graph(
            show_external=st.session_state.get('show_external', True),
            show_unused=st.session_state.get('show_unused', False),
            minimal_view=st.session_state.get('minimal_view', True)
        )
        
        visualizer = ClassHierarchyVisualizer(filtered_graph)
        fig = visualizer.create_interactive_plot()
        if fig:
            fig.update_layout(height=viz_height)
            st.plotly_chart(fig, use_container_width=True, config={
                'scrollZoom': True,
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['pan2d', 'select2d', 'lasso2d'],
                'modeBarButtonsToRemove': ['autoScale2d'],
                'doubleClick': 'reset+autosize'
            })
            
            # Add info about the tree layout
            st.info("🌳 **Tree Layout:** Green = Root classes • Blue = Middle classes • Purple = Leaf classes • Gold = Isolated classes")
        else:
            st.warning("Unable to generate class hierarchy")
    except Exception as e:
        st.error(f"Error rendering class hierarchy: {str(e)}")


def _render_mind_map(analyzer: CodeAnalyzer) -> None:
    """Render 3D mind map visualization."""
    try:
        viz_height = st.session_state.get('viz_height', 800)
        
        # Get filtered graph for cleaner visualization
        filtered_graph = analyzer.get_filtered_graph(
            show_external=False,  # Hide external nodes for cleaner view
            show_unused=False,    # Hide unused functions
            minimal_view=st.session_state.get('minimal_view', True)
        )
        
        # Get internal nodes from filtered graph
        internal_nodes = []
        try:
            for node, data in filtered_graph.nodes(data=True):
                if not data.get('is_external', False):
                    node_name = str(data.get('name', 'Unknown')).strip()
                    if node_name and node_name != 'Unknown':
                        internal_nodes.append((node, node_name))
        except Exception as e:
            st.error(f"Error accessing graph nodes: {str(e)}")
            return
        
        if not internal_nodes:
            st.warning("No meaningful functions found after filtering. Try uploading more complex Python files with substantial function definitions.")
            st.info("💡 The minimal view removes redundant methods (__init__, __str__, getters/setters) to show only core business logic.")
            return
        
        # Show filtering stats
        original_count = analyzer.graph.number_of_nodes()
        filtered_count = len(internal_nodes)
        st.info(f"📊 Showing {filtered_count} core functions (filtered from {original_count} total nodes)")
        
        # Root node selector
        try:
            node_options = [name for _, name in internal_nodes]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_options = []
            unique_nodes = []
            for (node, name) in internal_nodes:
                if name not in seen:
                    seen.add(name)
                    unique_options.append(name)
                    unique_nodes.append((node, name))
            
            if not unique_options:
                st.warning("No valid function names found after filtering.")
                return
            
            selected_name = st.selectbox(
                "Select root function:",
                options=unique_options,
                index=0,
                key="tree_root_select",
                help="Choose the function to start the 3D mind map from"
            )
            
            # Find the selected node
            selected_node = None
            for node, name in unique_nodes:
                if name == selected_name:
                    selected_node = node
                    break
            
            if not selected_node:
                st.error("Selected function not found.")
                return
                
        except Exception as e:
            st.error(f"Error setting up root selector: {str(e)}")
            return
        
        # Create and display 3D visualization
        try:
            with st.spinner("Generating 3D mind map..."):
                visualizer = MindMapVisualizer(filtered_graph)  # Use filtered graph
                fig = visualizer.create_interactive_plot(root_node=selected_node)
            
            if fig:
                fig.update_layout(height=viz_height)
                st.plotly_chart(fig, use_container_width=True, config={
                    'scrollZoom': True,
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['pan3d', 'zoom3d', 'resetCameraDefault3d', 'resetCameraLastSave3d', 'orbitRotation', 'tableRotation'],
                    'modeBarButtonsToRemove': ['autoScale2d'],
                    'doubleClick': 'reset'
                })
                
                # Add helpful info
                st.info("🌐 **3D Mind Map:** Drag to rotate • Mouse wheel to zoom • Double-click to reset view")
                st.info("💡 **Tip:** This shows only the core functions and their relationships. "
                       "Redundant methods (__init__, __str__, getters/setters) are filtered out for clarity.")
            else:
                st.warning("No 3D visualization generated. This might happen if the selected function has no meaningful internal calls.")
                
        except Exception as e:
            st.error(f"Error creating 3D mind map: {str(e)}")
            
    except Exception as e:
        st.error(f"Error in mind map rendering: {str(e)}")
        st.info("Try uploading different Python files or check that your code contains substantial function definitions.")
