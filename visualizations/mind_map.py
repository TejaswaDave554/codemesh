"""3D Mind Map visualization module.

This module creates interactive 3D mind map visualizations using Plotly 3D
to show code relationships in three-dimensional space.
"""

import plotly.graph_objects as go
import networkx as nx
import numpy as np
from typing import Dict, List, Set, Optional, Tuple
from utils.helpers import get_node_color
import math


class MindMapVisualizer:
    """Creates 3D mind map visualizations."""
    
    def __init__(self, graph: nx.DiGraph):
        """Initialize visualizer with a graph."""
        self.graph = graph
    
    def create_interactive_plot(self, root_node: Optional[str] = None) -> go.Figure:
        """Create 3D mind map visualization.

        Returns:
            Plotly 3D Figure object
        """
        try:
            # Get internal nodes only
            internal_nodes = self._get_internal_nodes()

            if not internal_nodes:
                return self._create_empty_figure()

            # Find root node
            if not root_node or root_node not in internal_nodes:
                root_node = self._find_root_node(internal_nodes)

            if not root_node:
                return self._create_empty_figure()

            # Build 3D layout
            pos_3d = self._calculate_3d_layout(root_node, internal_nodes)

            if not pos_3d:
                return self._create_empty_figure()

            # Create 3D traces
            edge_trace = self._create_3d_edge_trace(pos_3d, internal_nodes)
            node_trace = self._create_3d_node_trace(pos_3d, internal_nodes)

            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace])

            # Update layout for 3D with borders and better alignment
            fig.update_layout(
                title=dict(
                    text="🌐 3D Code Mind Map",
                    x=0,  # Left align title
                    font=dict(size=18)
                ),
                scene=dict(
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(200,200,200,0.3)',
                        showticklabels=False,
                        title=""
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(200,200,200,0.3)',
                        showticklabels=False,
                        title=""
                    ),
                    zaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(200,200,200,0.3)',
                        showticklabels=False,
                        title=""
                    ),
                    bgcolor='rgba(240,240,240,0.1)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5),
                        center=dict(x=0, y=0, z=0)
                    ),
                    aspectmode='cube'
                ),
                showlegend=False,
                margin=dict(l=30, r=30, t=70, b=30),  # Better margins
                hovermode='closest',
                dragmode='orbit',  # 3D orbit mode by default
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                # Add border for 3D plot
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

        except Exception as e:
            return self._create_error_figure(str(e))

    
    def _get_internal_nodes(self) -> Set[str]:
        """Get only internal (non-external) nodes."""
        internal = set()
        try:
            for node, data in self.graph.nodes(data=True):
                if not data.get('is_external', False):
                    internal.add(node)
        except Exception:
            pass
        return internal
    
    def _find_root_node(self, internal_nodes: Set[str]) -> Optional[str]:
        """Find best root node from internal nodes."""
        try:
            # Look for main function
            for node in internal_nodes:
                data = self.graph.nodes.get(node, {})
                if data.get('name') == 'main':
                    return node
            
            # Look for entry points (no incoming edges from internal nodes)
            for node in internal_nodes:
                has_internal_callers = False
                try:
                    for predecessor in self.graph.predecessors(node):
                        if predecessor in internal_nodes:
                            has_internal_callers = True
                            break
                except Exception:
                    pass
                
                if not has_internal_callers:
                    return node
            
            # Return first internal node
            return next(iter(internal_nodes)) if internal_nodes else None
            
        except Exception:
            return next(iter(internal_nodes)) if internal_nodes else None
    
    def _calculate_3d_layout(self, root: str, internal_nodes: Set[str]) -> Dict[str, Tuple[float, float, float]]:
        """Calculate 3D positions for nodes using spherical/radial layout."""
        try:
            pos_3d = {}
            
            # Start with root at center
            pos_3d[root] = (0.0, 0.0, 0.0)
            
            # Build levels using BFS
            levels = {root: 0}
            queue = [root]
            visited = {root}
            
            while queue:
                current = queue.pop(0)
                current_level = levels[current]
                
                # Get children
                children = []
                try:
                    for successor in self.graph.successors(current):
                        if (successor in internal_nodes and 
                            successor not in visited and 
                            current_level < 5):  # Limit depth
                            children.append(successor)
                            visited.add(successor)
                            levels[successor] = current_level + 1
                            queue.append(successor)
                except Exception:
                    continue
                
                # Position children in 3D space around parent
                if children:
                    parent_pos = pos_3d[current]
                    self._position_children_3d(children, parent_pos, current_level + 1, pos_3d)
            
            return pos_3d
            
        except Exception:
            return {root: (0.0, 0.0, 0.0)} if root else {}
    
    def _position_children_3d(self, children: List[str], parent_pos: Tuple[float, float, float], 
                             level: int, pos_3d: Dict[str, Tuple[float, float, float]]):
        """Position children in 3D space around their parent."""
        if not children:
            return
        
        px, py, pz = parent_pos
        num_children = len(children)
        
        # Calculate radius based on level (further from center as we go deeper)
        radius = 2.0 + level * 1.5
        
        if num_children == 1:
            # Single child - place directly in front
            pos_3d[children[0]] = (px + radius, py, pz)
        else:
            # Multiple children - distribute in 3D space
            for i, child in enumerate(children):
                # Use spherical coordinates for even distribution
                phi = (i / num_children) * 2 * math.pi  # Azimuthal angle
                theta = math.pi / 3 + (i % 3) * math.pi / 6  # Polar angle (vary by level)
                
                # Convert to Cartesian coordinates
                x = px + radius * math.sin(theta) * math.cos(phi)
                y = py + radius * math.sin(theta) * math.sin(phi)
                z = pz + radius * math.cos(theta)
                
                pos_3d[child] = (x, y, z)
    
    def _create_3d_edge_trace(self, pos_3d: Dict[str, Tuple[float, float, float]], 
                             internal_nodes: Set[str]) -> go.Scatter3d:
        """Create 3D edge trace."""
        edge_x, edge_y, edge_z = [], [], []

        try:
            for node in pos_3d:
                if node not in internal_nodes:
                    continue

                x0, y0, z0 = pos_3d[node]

                try:
                    for successor in self.graph.successors(node):
                        if successor in pos_3d and successor in internal_nodes:
                            x1, y1, z1 = pos_3d[successor]

                            # Add edge line
                            edge_x.extend([x0, x1, None])
                            edge_y.extend([y0, y1, None])
                            edge_z.extend([z0, z1, None])
                except Exception:
                    continue
        except Exception:
            pass

        return go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(
                color='rgba(100,100,100,0.6)',
                width=2
            ),
            hoverinfo='skip',
            showlegend=False
        )

    
    def _create_3d_node_trace(self, pos_3d: Dict[str, Tuple[float, float, float]], 
                             internal_nodes: Set[str]) -> go.Scatter3d:
        """Create 3D node trace."""
        node_x, node_y, node_z = [], [], []
        node_text, node_hover = [], []
        node_colors, node_sizes = [], []
        
        try:
            for node in pos_3d:
                if node not in internal_nodes:
                    continue
                
                x, y, z = pos_3d[node]
                node_x.append(x)
                node_y.append(y)
                node_z.append(z)
                
                # Get node data
                try:
                    data = self.graph.nodes.get(node, {})
                except Exception:
                    data = {}
                
                name = str(data.get('name', 'Unknown'))
                node_type = str(data.get('type', 'function'))
                filename = str(data.get('file', 'unknown'))
                if filename and filename != 'unknown':
                    try:
                        filename = filename.split('/')[-1].split('\\')[-1]
                    except Exception:
                        filename = 'unknown'
                
                line_num = data.get('line', 0)
                complexity = data.get('complexity', 1)
                
                # Try to get call count
                call_count = 0
                try:
                    call_count = len(list(self.graph.successors(node)))
                except Exception:
                    pass
                
                node_text.append(name)
                
                # Enhanced hover info
                hover_info = (
                    f"<b>{name}</b><br>"
                    f"Type: {node_type}<br>"
                    f"File: {filename}<br>"
                    f"Line: {line_num}<br>"
                    f"Complexity: {complexity}<br>"
                    f"Calls: {call_count}<br>"
                    f"Position: ({x:.1f}, {y:.1f}, {z:.1f})"
                )
                node_hover.append(hover_info)
                
                # Color based on type
                color = get_node_color(node_type)
                node_colors.append(color)
                
                # Size based on complexity
                size = max(8, min(20, 8 + complexity * 2))
                node_sizes.append(size)
        
        except Exception:
            # Fallback for errors
            if pos_3d:
                first_node = next(iter(pos_3d))
                x, y, z = pos_3d[first_node]
                node_x, node_y, node_z = [x], [y], [z]
                node_text = ['Error']
                node_hover = ['Error loading node data']
                node_colors = ['red']
                node_sizes = [10]
        
        return go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            textfont=dict(size=10, color='white'),  # White text for contrast against colored nodes
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
    
    def _create_empty_figure(self) -> go.Figure:
        """Create empty 3D figure."""
        fig = go.Figure()
        fig.add_annotation(
            text="No internal code found to visualize",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            )
        )
        return fig
    
    def _create_error_figure(self, error_msg: str) -> go.Figure:
        """Create error figure."""
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating 3D visualization:<br>{error_msg}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='red')
        )
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            )
        )
        return fig