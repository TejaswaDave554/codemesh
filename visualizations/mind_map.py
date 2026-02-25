"""Radial mind map visualization module.

This module creates radial/mind map style visualizations centered on a selected node,
showing immediate callers and callees using Plotly.
"""

import plotly.graph_objects as go
import networkx as nx
import math
from typing import Dict, Tuple, Optional
from utils.helpers import get_node_color


class MindMapVisualizer:
    """Creates radial mind map visualizations.
    
    This class generates interactive radial visualizations centered on a selected node,
    showing its immediate relationships in a circular layout.
    """
    
    def __init__(self, graph: nx.DiGraph):
        """Initialize visualizer with a graph.
        
        Args:
            graph: NetworkX directed graph to visualize
        """
        self.graph = graph
    
    def create_mind_map(self, center_node: Optional[str] = None) -> go.Figure:
        """Create interactive mind map visualization.
        
        Args:
            center_node: Node ID to center the visualization on
            
        Returns:
            Plotly Figure object
        """
        if self.graph.number_of_nodes() == 0:
            return self._create_empty_figure()
        
        if center_node is None or center_node not in self.graph:
            center_node = list(self.graph.nodes())[0]
        
        subgraph = self._get_neighborhood(center_node)
        pos = self._radial_layout(center_node, subgraph)
        
        edge_trace = self._create_edge_trace(pos, subgraph)
        node_trace = self._create_node_trace(pos, subgraph, center_node)
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=0, l=0, r=0, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           title=f"Mind Map - Centered on {self.graph.nodes[center_node]['name']}"
                       ))
        
        return fig
    
    def _get_neighborhood(self, center_node: str, radius: int = 1) -> nx.DiGraph:
        """Extract neighborhood subgraph around center node.
        
        Args:
            center_node: Center node ID
            radius: Number of hops to include
            
        Returns:
            Subgraph containing the neighborhood
        """
        nodes = {center_node}
        for _ in range(radius):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self.graph.predecessors(node))
                new_nodes.update(self.graph.successors(node))
            nodes.update(new_nodes)
        
        return self.graph.subgraph(nodes).copy()
    
    def _radial_layout(self, center: str, subgraph: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Calculate radial layout positions.
        
        Args:
            center: Center node ID
            subgraph: Subgraph to layout
            
        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        pos = {center: (0, 0)}
        
        neighbors = list(subgraph.neighbors(center)) + list(subgraph.predecessors(center))
        neighbors = list(set(neighbors))
        
        if neighbors:
            angle_step = 2 * math.pi / len(neighbors)
            radius = 2.0
            
            for i, node in enumerate(neighbors):
                angle = i * angle_step
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                pos[node] = (x, y)
        
        return pos
    
    def _create_edge_trace(self, pos: Dict[str, Tuple[float, float]], 
                          subgraph: nx.DiGraph) -> go.Scatter:
        """Create edge trace for visualization.
        
        Args:
            pos: Node positions
            subgraph: Subgraph being visualized
            
        Returns:
            Plotly Scatter trace for edges
        """
        edge_x = []
        edge_y = []
        
        for edge in subgraph.edges():
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
    
    def _create_node_trace(self, pos: Dict[str, Tuple[float, float]], 
                          subgraph: nx.DiGraph, center_node: str) -> go.Scatter:
        """Create node trace for visualization.
        
        Args:
            pos: Node positions
            subgraph: Subgraph being visualized
            center_node: Center node ID
            
        Returns:
            Plotly Scatter trace for nodes
        """
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        
        for node in pos:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = subgraph.nodes[node]
            node_text.append(f"{data['name']}<br>Type: {data['type']}<br>File: {data['file']}")
            
            if node == center_node:
                node_colors.append('#e74c3c')
                node_sizes.append(30)
            else:
                node_colors.append(get_node_color(data['type']))
                node_sizes.append(20)
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[subgraph.nodes[n]['name'] for n in pos],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_sizes,
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
