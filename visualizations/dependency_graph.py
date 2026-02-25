"""Network dependency graph visualization module.

This module creates force-directed network visualizations showing all code relationships
using PyVis for interactive rendering.
"""

from pyvis.network import Network
import networkx as nx
from typing import Optional
import tempfile
import streamlit.components.v1 as components
from utils.helpers import get_node_color


class DependencyGraphVisualizer:
    """Creates force-directed network graph visualizations.
    
    This class generates interactive network visualizations showing all functions,
    classes, and their relationships using a force-directed layout.
    """
    
    def __init__(self, graph: nx.DiGraph):
        """Initialize visualizer with a graph.
        
        Args:
            graph: NetworkX directed graph to visualize
        """
        self.graph = graph
    
    def create_network(self, height: str = "600px", width: str = "100%") -> str:
        """Create interactive network visualization.
        
        Args:
            height: Height of the visualization
            width: Width of the visualization
            
        Returns:
            HTML string of the network visualization
        """
        if self.graph.number_of_nodes() == 0:
            return "<div>No data to display</div>"
        
        net = Network(height=height, width=width, directed=True, notebook=False)
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=100)
        
        for node, data in self.graph.nodes(data=True):
            color = get_node_color(data['type'])
            title = f"{data['name']}\nType: {data['type']}\nFile: {data['file']}\nLine: {data['line']}"
            
            net.add_node(
                node,
                label=data['name'],
                title=title,
                color=color,
                size=20
            )
        
        for source, target, data in self.graph.edges(data=True):
            relation = data.get('relation', 'calls')
            color = '#e74c3c' if relation == 'inherits' else '#95a5a6'
            net.add_edge(source, target, color=color, arrows='to')
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
            net.save_graph(f.name)
            with open(f.name, 'r', encoding='utf-8') as file:
                html = file.read()
        
        return html
    
    def render_in_streamlit(self, height: int = 600):
        """Render network visualization in Streamlit.
        
        Args:
            height: Height of the visualization in pixels
        """
        html = self.create_network(height=f"{height}px")
        components.html(html, height=height, scrolling=True)
