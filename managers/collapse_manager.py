"""Collapse/expand state management for graph nodes."""

from typing import Set, Dict, List


class CollapseManager:
    """Manages collapse/expand state for any node in the graph."""
    
    def __init__(self):
        self.collapsed_nodes: Set[str] = set()
        self.node_groups: Dict[str, List[str]] = {}
        self.parent_map: Dict[str, str] = {}
    
    def collapse_node(self, node_id: str, children: List[str]):
        """Collapse a node and hide its children."""
        self.collapsed_nodes.add(node_id)
        self.node_groups[node_id] = children
        
        for child in children:
            self.parent_map[child] = node_id
    
    def expand_node(self, node_id: str):
        """Expand a node and show its children."""
        self.collapsed_nodes.discard(node_id)
        
        if node_id in self.node_groups:
            for child in self.node_groups[node_id]:
                self.parent_map.pop(child, None)
    
    def toggle_node(self, node_id: str):
        """Toggle collapse state of a node."""
        if self.is_collapsed(node_id):
            self.expand_node(node_id)
        else:
            if node_id in self.node_groups:
                self.collapse_node(node_id, self.node_groups[node_id])
    
    def is_collapsed(self, node_id: str) -> bool:
        """Check if node is collapsed."""
        return node_id in self.collapsed_nodes
    
    def is_hidden(self, node_id: str) -> bool:
        """Check if node is hidden by a collapsed parent."""
        parent = self.parent_map.get(node_id)
        if parent and self.is_collapsed(parent):
            return True
        return False
    
    def get_visible_nodes(self, all_nodes: List[str]) -> List[str]:
        """Get list of nodes that should be visible."""
        visible = []
        for node in all_nodes:
            if not self.is_hidden(node):
                visible.append(node)
        return visible
    
    def collapse_all_external(self):
        """Collapse all external dependency groups."""
        for node_id in list(self.node_groups.keys()):
            if node_id.startswith('__group__'):
                self.collapse_node(node_id, self.node_groups[node_id])
    
    def expand_all(self):
        """Expand all collapsed nodes."""
        self.collapsed_nodes.clear()
        self.parent_map.clear()
