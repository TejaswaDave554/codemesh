"""Hierarchical call tree visualization module.

This module creates interactive hierarchical tree visualizations of function call chains
using Plotly for rendering.
"""

import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Tuple, Optional
from utils.helpers import get_node_color


class CallTreeVisualizer:
    """Creates hierarchical call tree visualizations.
    
    This class generates interactive tree-layout visualizations showing function
    call hierarchies starting from a root node.
    """
    
    def __init__(self, graph: nx.DiGraph):
        """Initialize visualizer with a graph.
        
        Args:
            graph: NetworkX directed graph to visualize
        """
        self.graph = graph
    
    def create_interactive_plot(self, max_depth: int = 10) -> Optional[go.Figure]:
        """Create interactive call tree visualization.
        
        Args:
            max_depth: Maximum depth to display
            
        Returns:
            Plotly Figure object or None
        """
        return self.create_tree_figure()
    
    def create_tree_figure(self, root_node: Optional[str] = None) -> go.Figure:
        """Create interactive call tree visualization.
        
        Args:
            root_node: Node ID to use as root (if None, finds suitable root)
            
        Returns:
            Plotly Figure object
        """
        if self.graph.number_of_nodes() == 0:
            return self._create_empty_figure()
        
        if root_node is None:
            root_node = self._find_root_node()
        
        if root_node not in self.graph:
            return self._create_empty_figure()
        
        pos = self._hierarchical_layout(root_node)
        
        edge_trace = self._create_edge_trace(pos)
        node_trace = self._create_node_trace(pos)
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=30, l=30, r=30, t=70),  # Better margins
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           title=dict(
                               text="📊 Call Tree Visualization",
                               x=0,  # Left align title
                               font=dict(size=18)
                           ),
                           dragmode='pan',  # Pan by default
                           plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
                           # Add border
                           shapes=[
                               dict(
                                   type="rect",
                                   xref="paper", yref="paper",
                                   x0=0, y0=0, x1=1, y1=1,
                                   line=dict(color="rgba(128,128,128,0.3)", width=1)
                               )
                           ]
                       ))
        
        return fig
    
    def _find_root_node(self) -> str:
        """Find suitable root node for tree visualization.
        
        Returns:
            Node ID of root node
        """
        for node, data in self.graph.nodes(data=True):
            if data['name'] == 'main':
                return node
        
        root_candidates = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        if root_candidates:
            return root_candidates[0]
        
        return list(self.graph.nodes())[0]
    
    def _hierarchical_layout(self, root: str) -> Dict[str, Tuple[float, float]]:
        """Calculate hierarchical layout positions.
        
        Args:
            root: Root node ID
            
        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        levels = self._assign_levels(root)
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
    
    def _assign_levels(self, root: str) -> Dict[str, int]:
        """Assign depth levels to nodes via BFS.
        
        Args:
            root: Root node ID
            
        Returns:
            Dictionary mapping node IDs to depth levels
        """
        levels = {root: 0}
        queue = [(root, 0)]
        visited = {root}
        max_nodes = 1000  # Prevent excessive memory usage
        
        while queue and len(visited) < max_nodes:
            node, level = queue.pop(0)
            
            # Limit depth to prevent infinite loops
            if level >= 50:
                continue
            
            for successor in self.graph.successors(node):
                if successor not in visited:
                    visited.add(successor)
                    levels[successor] = level + 1
                    queue.append((successor, level + 1))
        
        return levels
    
    def _create_edge_trace(self, pos: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """Create edge trace for visualization.
        
        Args:
            pos: Node positions
            
        Returns:
            Plotly Scatter trace for edges
        """
        edge_x = []
        edge_y = []
        
        for edge in self.graph.edges():
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
    
    def _create_node_trace(self, pos: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """Create node trace for visualization.
        
        Args:
            pos: Node positions
            
        Returns:
            Plotly Scatter trace for nodes
        """
        node_x = []
        node_y = []
        node_text = []
        node_hover = []
        node_colors = []
        
        for node in pos:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = self.graph.nodes[node]
            filename = data['file'].split('/')[-1].split('\\')[-1]
            node_text.append(f"{data['name']}")
            node_hover.append(
                f"<b>{data['name']}</b><br>"
                f"File: {filename}<br>"
                f"Line: {data['line']}<br>"
                f"Type: {data['type']}<br>"
                f"Complexity: {data.get('complexity', 1)}"
            )
            node_colors.append(get_node_color(data['type']))
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=15,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )
    
    def _create_empty_figure(self) -> go.Figure:
        """Create empty figure with message.
        
        Returns:
            Empty Plotly Figure
        """
        fig = go.Figure()
        fig.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
