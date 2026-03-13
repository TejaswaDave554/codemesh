"""Class inheritance hierarchy visualization module.

This module creates tree visualizations showing class inheritance relationships
and their methods using Plotly with theme-adaptive styling.
"""

import plotly.graph_objects as go
import networkx as nx
from typing import Dict, Tuple, List
from utils.helpers import get_node_color
from utils.theme_helper import get_theme_colors, get_node_colors, get_theme_layout


class ClassHierarchyVisualizer:
    """Creates class inheritance hierarchy visualizations.
    
    This class generates interactive tree visualizations showing class inheritance
    relationships with methods displayed on hover.
    """
    
    def __init__(self, graph: nx.DiGraph, full_graph: nx.DiGraph = None):
        """Initialize visualizer with a graph.
        
        Args:
            graph: NetworkX directed graph containing class nodes
            full_graph: Full graph with all nodes (for method lookup)
        """
        self.graph = graph
        self.full_graph = full_graph if full_graph else graph
    
    def create_interactive_plot(self) -> go.Figure:
        """Create interactive class hierarchy visualization.
        
        Returns:
            Plotly Figure object
        """
        return self.create_hierarchy_figure()
    
    def create_hierarchy_figure(self) -> go.Figure:
        """Create interactive class hierarchy visualization with tree layout.
        
        Returns:
            Plotly Figure object
        """
        if self.graph.number_of_nodes() == 0:
            return self._create_empty_figure()
        
        # Filter to only show classes
        class_nodes = [n for n, data in self.graph.nodes(data=True) 
                      if data.get('type') == 'class']
        
        if not class_nodes:
            return self._create_no_classes_figure()
        
        # Create a subgraph with only classes
        class_graph = self.graph.subgraph(class_nodes).copy()
        
        # Use hierarchical tree layout with proper spacing
        pos = self._tree_layout(class_graph)
        
        # Create traces with theme-aware styling
        edge_trace = self._create_tree_edge_trace(pos, class_graph)
        node_trace = self._create_tree_node_trace(pos, class_graph)
        
        fig = go.Figure(data=[edge_trace, node_trace])
        
        # Theme-aware layout with borders and better alignment
        theme_layout = get_theme_layout()
        fig.update_layout(
            title=dict(
                text="🏛️ Class Hierarchy Tree",
                x=0,  # Left align title
                font=dict(size=18)  # Use default font color instead of theme color
            ),
            showlegend=False,
            hovermode='closest',
            **theme_layout,
            # Add border and improve layout
            shapes=[
                dict(
                    type="rect",
                    xref="paper", yref="paper",
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color="rgba(128,128,128,0.3)", width=1)
                )
            ]
        )
        
        return fig
    
    def _hierarchical_layout(self, roots: List[str]) -> Dict[str, Tuple[float, float]]:
        """Calculate hierarchical layout for class tree.
        
        Args:
            roots: List of root node IDs
            
        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        levels = {}
        for root in roots:
            self._assign_levels(root, levels, 0)
        
        pos = {}
        level_nodes = {}
        for node, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)
        
        for level, nodes in level_nodes.items():
            y = -level
            for i, node in enumerate(nodes):
                x = i - len(nodes) / 2
                pos[node] = (x, y)
        
        return pos

    def _tree_layout(self, class_graph: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical tree layout with proper spacing.

        Args:
            class_graph: Graph containing only class nodes

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if class_graph.number_of_nodes() == 0:
            return {}

        # Find root classes (no inheritance)
        roots = [n for n in class_graph.nodes() if class_graph.in_degree(n) == 0]
        if not roots:
            # If no clear roots, pick nodes with highest out-degree
            roots = sorted(class_graph.nodes(), 
                          key=lambda x: class_graph.out_degree(x), 
                          reverse=True)[:1]

        # Calculate levels for each node
        levels = {}
        self._assign_tree_levels(class_graph, roots, levels)

        # Group nodes by level
        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)

        # Calculate positions with proper spacing
        pos = {}
        max_level = max(level_groups.keys()) if level_groups else 0

        for level, nodes in level_groups.items():
            y = max_level - level  # Top-down layout
            num_nodes = len(nodes)

            # Calculate spacing based on number of nodes
            if num_nodes == 1:
                x_positions = [0]
            else:
                # Spread nodes evenly with good spacing
                total_width = max(6, num_nodes * 2)  # Minimum width of 6
                x_positions = []
                for i in range(num_nodes):
                    x = -total_width/2 + (i * total_width / (num_nodes - 1))
                    x_positions.append(x)

            for i, node in enumerate(nodes):
                pos[node] = (x_positions[i], y * 2)  # Multiply by 2 for vertical spacing

        return pos

    def _assign_tree_levels(self, graph: nx.DiGraph, roots: List[str], levels: Dict[str, int]):
        """Assign levels to nodes in tree hierarchy.

        Args:
            graph: Class graph
            roots: Root node IDs
            levels: Dictionary to populate with levels
        """
        # BFS to assign levels
        from collections import deque

        queue = deque()
        for root in roots:
            levels[root] = 0
            queue.append(root)

        visited = set(roots)

        while queue:
            current = queue.popleft()
            current_level = levels[current]

            for child in graph.successors(current):
                if child not in visited:
                    levels[child] = current_level + 1
                    queue.append(child)
                    visited.add(child)

    def _create_tree_edge_trace(self, pos: Dict[str, Tuple[float, float]], 
                               class_graph: nx.DiGraph) -> go.Scatter:
        """Create theme-aware edge trace for tree layout.

        Args:
            pos: Node positions
            class_graph: Graph containing only classes

        Returns:
            Plotly Scatter trace for edges
        """
        edge_x = []
        edge_y = []

        for edge in class_graph.edges():
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        theme_colors = get_theme_colors()

        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(
                width=2, 
                color=theme_colors['edge_color']
            ),
            hoverinfo='none',
            mode='lines',
            name='Inheritance',
            showlegend=False
        )

    def _create_tree_node_trace(self, pos: Dict[str, Tuple[float, float]], 
                               class_graph: nx.DiGraph) -> go.Scatter:
        """Create theme-aware node trace for tree layout.

        Args:
            pos: Node positions
            class_graph: Graph containing only classes

        Returns:
            Plotly Scatter trace for nodes
        """
        node_x = []
        node_y = []
        node_text = []
        node_hover = []
        node_colors = []
        node_sizes = []

        theme_colors = get_theme_colors()
        node_colors_palette = get_node_colors()

        for node in pos:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            data = class_graph.nodes[node]
            class_name = data['name']
            node_text.append(class_name)

            # Get class info
            filename = data['file'].split('/')[-1].split('\\')[-1]
            methods = self._get_class_methods(node)

            # Count inheritance relationships
            parents = list(class_graph.predecessors(node))
            children = list(class_graph.successors(node))

            # Enhanced hover info
            hover_text = (
                f"<b>🏛️ {class_name}</b><br>"
                f"📁 File: {filename}<br>"
                f"📍 Line: {data['line']}<br>"
                f"👥 Methods: {len(methods)}<br>"
            )

            if parents:
                parent_names = [class_graph.nodes[p]['name'] for p in parents]
                hover_text += f"⬆️ Inherits from: {', '.join(parent_names)}<br>"
            if children:
                child_names = [class_graph.nodes[c]['name'] for c in children]
                hover_text += f"⬇️ Inherited by: {', '.join(child_names)}<br>"

            if methods:
                hover_text += f"<br><b>Methods:</b><br>"
                displayed_methods = methods[:6]  # Show fewer for cleaner display
                for method in displayed_methods:
                    hover_text += f"• {method}<br>"
                if len(methods) > 6:
                    hover_text += f"• ... and {len(methods) - 6} more"

            node_hover.append(hover_text)

            # Theme-aware colors based on class role
            if not parents and children:
                # Root class
                node_colors.append(node_colors_palette['root'])
                node_sizes.append(30)
            elif parents and children:
                # Middle class
                node_colors.append(node_colors_palette['middle'])
                node_sizes.append(25)
            elif parents and not children:
                # Leaf class
                node_colors.append(node_colors_palette['leaf'])
                node_sizes.append(22)
            else:
                # Isolated class
                node_colors.append(node_colors_palette['isolated'])
                node_sizes.append(20)

        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            textfont=dict(
                size=10,
                color='white',  # White text for contrast against colored nodes
                family='Arial, sans-serif'
            ),
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color=theme_colors['node_border']),
                opacity=0.9
            ),
            name='Classes',
            showlegend=False
        )

    def _create_no_classes_figure(self) -> go.Figure:
        """Create figure when no classes are found.

        Returns:
            Plotly Figure with message
        """
        fig = go.Figure()
        fig.add_annotation(
            text="No classes found in the code<br><span style='font-size:14px'>Upload files with class definitions to see hierarchy</span>",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def _assign_levels(self, node: str, levels: Dict[str, int], level: int, max_depth: int = 50):
        """Recursively assign depth levels to nodes.
        
        Args:
            node: Current node ID
            levels: Dictionary to populate with levels
            level: Current depth level
            max_depth: Maximum recursion depth
        """
        # Prevent infinite recursion
        if level >= max_depth:
            return
        
        if node not in levels or levels[node] > level:
            levels[node] = level
            for successor in self.graph.successors(node):
                self._assign_levels(successor, levels, level + 1, max_depth)
    


    
    
    def _get_class_methods(self, class_node: str) -> List[str]:
        """Get methods belonging to a class.
        
        Args:
            class_node: Class node ID
            
        Returns:
            List of method names
        """
        class_name = self.graph.nodes[class_node]['name']
        file_path = self.graph.nodes[class_node]['file']
        
        methods = []
        for node, data in self.full_graph.nodes(data=True):
            if data['type'] == 'method' and data.get('parent_class') == class_name:
                if data['file'] == file_path:
                    methods.append(data['name'])
        
        return methods
    
    def _create_empty_figure(self) -> go.Figure:
        """Create empty figure with message.
        
        Returns:
            Empty Plotly Figure
        """
        fig = go.Figure()
        fig.add_annotation(
            text="No code structure to display<br><span style='font-size:14px'>Upload Python files to analyze class hierarchy</span>",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
