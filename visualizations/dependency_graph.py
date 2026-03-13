"""Network dependency graph visualization module."""

from pyvis.network import Network
import networkx as nx
from typing import Optional, Dict, Tuple, List
import tempfile
import streamlit.components.v1 as components
import plotly.graph_objects as go
from utils.helpers import get_node_color
from utils.theme_helper import get_theme_colors, get_node_colors, get_theme_layout
from managers.edge_styler import EdgeStyler


class DependencyGraphVisualizer:
    """Creates force-directed network graph visualizations."""
    
    def __init__(self, graph: nx.DiGraph, show_glow: bool = True, 
                 edge_styling: bool = True, show_external: bool = True,
                 node_spacing: float = 2.5, layout_algorithm: str = "spring",
                 show_labels: bool = True, height: int = 800):
        """Initialize visualizer with a graph."""
        self.graph = graph
        self.show_glow = show_glow
        self.edge_styling = edge_styling
        self.show_external = show_external
        self.node_spacing = node_spacing
        self.layout_algorithm = layout_algorithm
        self.show_labels = show_labels
        self.height = height
    
    def create_interactive_plot(self) -> Optional[go.Figure]:
        """Create interactive network visualization using Plotly."""
        if self.graph.number_of_nodes() == 0:
            return self._create_empty_figure()
        
        pos = self._calculate_layout()
        
        traces = []
        
        if self.show_glow:
            glow_trace = self._create_glow_trace(pos)
            if glow_trace:
                traces.append(glow_trace)
        
        edge_trace = self._create_edge_trace(pos)
        node_trace = self._create_node_trace(pos)
        
        traces.extend([edge_trace, node_trace])
        
        fig = go.Figure(
            data=traces,
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=30, l=30, r=30, t=70),  # Better margins
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                title=dict(
                    text="🕸️ Dependency Graph",
                    x=0,  # Left align title
                    font=dict(size=18)
                ),
                height=self.height,
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
            )
        )
        
        fig.update_xaxes(fixedrange=False)
        fig.update_yaxes(fixedrange=False)
        
        return fig
    
    def _create_glow_trace(self, pos: Dict[str, Tuple[float, float]]) -> Optional[go.Scatter]:
        """Create glow effect for nodes with external dependencies."""
        glow_x = []
        glow_y = []
        glow_sizes = []
        
        glow_style = EdgeStyler.get_glow_style()
        
        for node in pos:
            data = self.graph.nodes[node]
            if self._has_external_calls(node):
                x, y = pos[node]
                glow_x.append(x)
                glow_y.append(y)
                base_size = 15 + data.get('complexity', 1) * 2
                glow_sizes.append(base_size * glow_style['size_multiplier'])
        
        if not glow_x:
            return None
        
        return go.Scatter(
            x=glow_x, y=glow_y,
            mode='markers',
            marker=dict(
                size=glow_sizes,
                color=glow_style['color'],
                line=dict(
                    width=glow_style['line_width'],
                    color=glow_style['line_color']
                )
            ),
            hoverinfo='skip',
            showlegend=False
        )
    
    def _calculate_layout(self) -> Dict[str, Tuple[float, float]]:
        """Calculate node positions based on selected layout algorithm."""
        num_nodes = self.graph.number_of_nodes()
        
        try:
            if self.layout_algorithm == "Spring (Force-Directed)":
                pos = nx.spring_layout(
                    self.graph, 
                    k=self.node_spacing/num_nodes**0.5, 
                    iterations=100,
                    scale=2.0
                )
            elif self.layout_algorithm == "Circular":
                pos = nx.circular_layout(self.graph, scale=2.0)
            elif self.layout_algorithm == "Hierarchical":
                pos = nx.spring_layout(
                    self.graph,
                    k=self.node_spacing,
                    iterations=50
                )
                pos = self._apply_hierarchical_layout(pos)
            elif self.layout_algorithm == "Kamada-Kawai":
                pos = nx.kamada_kawai_layout(self.graph, scale=2.0)
            else:
                pos = nx.spring_layout(
                    self.graph,
                    k=self.node_spacing/num_nodes**0.5,
                    iterations=100,
                    scale=2.0
                )
        except Exception:
            pos = nx.spring_layout(self.graph, scale=2.0)
        
        return pos
    
    def _apply_hierarchical_layout(self, pos: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Apply hierarchical adjustments to layout."""
        levels = {}
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            levels[node] = in_degree
        
        max_level = max(levels.values()) if levels else 1
        
        for node in pos:
            x, y = pos[node]
            level = levels.get(node, 0)
            y_adjusted = (level / max_level) * 4 - 2
            pos[node] = (x, y_adjusted)
        
        return pos
    
    def _has_external_calls(self, node_id: str) -> bool:
        """Check if node has external dependencies."""
        for successor in self.graph.successors(node_id):
            if self.graph.nodes[successor].get('is_external', False):
                return True
        return False
    
    def _create_edge_trace(self, pos: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """Create edge trace with styling."""
        if self.edge_styling:
            return self._create_styled_edges(pos)
        else:
            return self._create_simple_edges(pos)
    
    def _create_styled_edges(self, pos: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """Create edges with different styles based on relationship type."""
        edge_x = []
        edge_y = []
        
        for edge in self.graph.edges(data=True):
            source, target, edge_data = edge
            if source in pos and target in pos:
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='rgba(100,100,100,0.8)'),  # More visible edges
            hoverinfo='none',
            mode='lines'
        )
    
    def _create_simple_edges(self, pos: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """Create simple edges without styling."""
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
            line=dict(width=2, color='rgba(100,100,100,0.8)'),  # More visible edges
            hoverinfo='none',
            mode='lines'
        )
    
    def _create_node_trace(self, pos: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """Create node trace with enhanced styling."""
        node_x = []
        node_y = []
        node_text = []
        node_hover = []
        node_colors = []
        node_sizes = []
        
        for node in pos:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = self.graph.nodes[node]
            filename = data['file'].split('/')[-1].split('\\')[-1] if data['file'] else 'external'
            
            if data.get('is_external', False):
                display_text = f"{data['name']}" if self.show_labels else ""
                node_text.append(display_text)
                node_hover.append(
                    f"<b>{data['name']}</b><br>"
                    f"Type: {data['type']}<br>"
                    f"Package: {data.get('package_type', 'external')}"
                )
                node_colors.append(self._get_external_color(data.get('package_type', 'third_party')))
                node_sizes.append(25)
            else:
                display_text = data['name'] if self.show_labels else ""
                node_text.append(display_text)
                node_hover.append(
                    f"<b>{data['name']}</b><br>"
                    f"Type: {data['type']}<br>"
                    f"File: {filename}<br>"
                    f"Line: {data['line']}<br>"
                    f"Complexity: {data.get('complexity', 1)}<br>"
                    f"Calls: {self.graph.out_degree(node)}<br>"
                    f"Called by: {self.graph.in_degree(node)}"
                )
                node_colors.append(get_node_color(data['type']))
                base_size = 20 + data.get('complexity', 1) * 3
                node_sizes.append(base_size)
        
        mode = 'markers+text' if self.show_labels else 'markers'
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode=mode,
            text=node_text,
            textposition="top center",
            textfont=dict(size=10),  # Remove hardcoded black color
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white'),
                opacity=0.9
            )
        )
    
    def _get_external_color(self, package_type: str) -> str:
        """Get color for external package types."""
        colors = {
            'stdlib': '#f39c12',
            'third_party': '#e74c3c',
            'builtin': '#9b59b6'
        }
        return colors.get(package_type, '#95a5a6')
    
    def _create_empty_figure(self) -> go.Figure:
        """Create empty figure with message."""
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
            filename = data['file'].split('/')[-1].split('\\')[-1]
            
            # Enhanced title with file name
            title = (
                f"<b>{data['name']}</b><br>"
                f"Type: {data['type']}<br>"
                f"File: {filename}<br>"
                f"Full Path: {data['file']}<br>"
                f"Line: {data['line']}<br>"
                f"Complexity: {data.get('complexity', 1)}"
            )
            
            # Show filename in label for better context
            label = f"{data['name']}\n({filename})"
            
            net.add_node(
                node,
                label=label,
                title=title,
                color=color,
                size=20 + data.get('complexity', 1) * 2
            )
        
        for source, target, data in self.graph.edges(data=True):
            relation = data.get('relation', 'calls')
            if relation == 'inherits':
                color = '#e74c3c'
            elif relation == 'uses':
                color = '#f39c12'
            else:
                color = '#95a5a6'
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
