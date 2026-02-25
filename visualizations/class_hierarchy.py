"""Class inheritance hierarchy visualization module.

This module creates tree visualizations showing class inheritance relationships
and their methods using Plotly.
"""

import plotly.graph_objects as go
import networkx as nx
from typing import Dict, Tuple, List
from utils.helpers import get_node_color


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
    
    def create_hierarchy_figure(self) -> go.Figure:
        """Create interactive class hierarchy visualization.
        
        Returns:
            Plotly Figure object
        """
        if self.graph.number_of_nodes() == 0:
            return self._create_empty_figure()
        
        roots = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        if not roots:
            roots = list(self.graph.nodes())[:1]
        
        pos = self._hierarchical_layout(roots)
        
        edge_trace = self._create_edge_trace(pos)
        node_trace = self._create_node_trace(pos)
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=0, l=0, r=0, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           title="Class Hierarchy"
                       ))
        
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
    
    def _assign_levels(self, node: str, levels: Dict[str, int], level: int):
        """Recursively assign depth levels to nodes.
        
        Args:
            node: Current node ID
            levels: Dictionary to populate with levels
            level: Current depth level
        """
        if node not in levels or levels[node] > level:
            levels[node] = level
            for successor in self.graph.successors(node):
                self._assign_levels(successor, levels, level + 1)
    
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
            line=dict(width=2, color='#e74c3c'),
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
        
        for node in pos:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = self.graph.nodes[node]
            node_text.append(data['name'])
            
            methods = self._get_class_methods(node)
            hover_text = f"<b>{data['name']}</b><br>File: {data['file']}<br>Line: {data['line']}"
            if methods:
                hover_text += f"<br><br>Methods:<br>{'<br>'.join(methods)}"
            node_hover.append(hover_text)
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=20,
                color=get_node_color('class'),
                line=dict(width=2, color='white')
            )
        )
    
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
            text="No class hierarchy to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
