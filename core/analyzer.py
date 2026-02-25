"""Graph building and code analysis module.

This module constructs NetworkX graphs from parsed code structures and provides
analysis capabilities for understanding code relationships and dependencies.
"""

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
from core.parser import ParseResult, CodeNode


class CodeAnalyzer:
    """Analyzes parsed code and builds relationship graphs.
    
    This class takes parsed code structures and builds a NetworkX directed graph
    representing all functions, classes, methods, and their relationships.
    """
    
    def __init__(self, parse_result: ParseResult):
        """Initialize analyzer with parse results.
        
        Args:
            parse_result: ParseResult containing nodes and imports
        """
        self.parse_result = parse_result
        self.graph = nx.DiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Build NetworkX graph from parsed nodes and relationships."""
        for node_id, node in self.parse_result.nodes.items():
            self.graph.add_node(
                node_id,
                name=node.name,
                type=node.node_type,
                file=node.file_path,
                line=node.line_number,
                params=node.parameters,
                parent_class=node.parent_class,
                base_classes=node.base_classes,
                source=node.source_code,
                complexity=node.complexity
            )
        
        for node_id, node in self.parse_result.nodes.items():
            for call in node.calls:
                target_id = self._resolve_call(node, call)
                if target_id and target_id in self.graph:
                    self.graph.add_edge(node_id, target_id, relation='calls')
        
        for node_id, node in self.parse_result.nodes.items():
            if node.node_type == 'class':
                for base_class in node.base_classes:
                    base_id = self._find_class(base_class, node.file_path)
                    if base_id:
                        self.graph.add_edge(node_id, base_id, relation='inherits')
    
    def _resolve_call(self, caller: CodeNode, call_name: str) -> Optional[str]:
        """Resolve a function call to its node ID.
        
        Args:
            caller: CodeNode making the call
            call_name: Name of the called function
            
        Returns:
            Node ID of the called function or None
        """
        same_file_id = f"{caller.file_path}::{call_name}"
        if same_file_id in self.parse_result.nodes:
            return same_file_id
        
        if caller.parent_class:
            method_id = f"{caller.file_path}::{caller.parent_class}.{call_name}"
            if method_id in self.parse_result.nodes:
                return method_id
            
            for base_class in self._get_base_classes(caller.parent_class, caller.file_path):
                base_method_id = f"{caller.file_path}::{base_class}.{call_name}"
                if base_method_id in self.parse_result.nodes:
                    return base_method_id
        
        for node_id, node in self.parse_result.nodes.items():
            if node.name == call_name:
                return node_id
        
        return None
    
    def _get_base_classes(self, class_name: str, file_path: str) -> List[str]:
        """Get base classes for a given class.
        
        Args:
            class_name: Name of the class
            file_path: File path of the class
            
        Returns:
            List of base class names
        """
        class_id = f"{file_path}::{class_name}"
        if class_id in self.parse_result.nodes:
            return self.parse_result.nodes[class_id].base_classes
        return []
    
    def _find_class(self, class_name: str, file_path: str) -> Optional[str]:
        """Find a class node by name.
        
        Args:
            class_name: Name of the class to find
            file_path: File path context for search
            
        Returns:
            Node ID of the class or None
        """
        same_file_id = f"{file_path}::{class_name}"
        if same_file_id in self.parse_result.nodes:
            return same_file_id
        
        for node_id, node in self.parse_result.nodes.items():
            if node.name == class_name and node.node_type == 'class':
                return node_id
        
        return None
    
    def get_call_tree(self, root_node: str, max_depth: int = 10) -> nx.DiGraph:
        """Generate call tree starting from a root node.
        
        Args:
            root_node: Node ID to use as root
            max_depth: Maximum depth to traverse
            
        Returns:
            Subgraph containing the call tree
        """
        if root_node not in self.graph:
            return nx.DiGraph()
        
        nodes = {root_node}
        current_level = {root_node}
        
        for _ in range(max_depth):
            next_level = set()
            for node in current_level:
                successors = set(self.graph.successors(node))
                next_level.update(successors)
            if not next_level:
                break
            nodes.update(next_level)
            current_level = next_level
        
        return self.graph.subgraph(nodes).copy()
    
    def get_class_hierarchy(self) -> nx.DiGraph:
        """Extract class inheritance hierarchy.
        
        Returns:
            Subgraph containing only classes and inheritance relationships
        """
        class_nodes = [n for n, d in self.graph.nodes(data=True) if d['type'] == 'class']
        subgraph = self.graph.subgraph(class_nodes).copy()
        
        edges_to_remove = [(u, v) for u, v, d in subgraph.edges(data=True) 
                          if d.get('relation') != 'inherits']
        subgraph.remove_edges_from(edges_to_remove)
        
        return subgraph
    
    def get_node_neighborhood(self, node_id: str, radius: int = 1) -> nx.DiGraph:
        """Get neighborhood around a node (callers and callees).
        
        Args:
            node_id: Center node ID
            radius: Number of hops to include
            
        Returns:
            Subgraph containing the neighborhood
        """
        if node_id not in self.graph:
            return nx.DiGraph()
        
        nodes = {node_id}
        for _ in range(radius):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self.graph.predecessors(node))
                new_nodes.update(self.graph.successors(node))
            nodes.update(new_nodes)
        
        return self.graph.subgraph(nodes).copy()
    
    def filter_by_file(self, file_path: str) -> nx.DiGraph:
        """Filter graph to show only nodes from a specific file.
        
        Args:
            file_path: Path to filter by
            
        Returns:
            Filtered subgraph
        """
        nodes = [n for n, d in self.graph.nodes(data=True) if d['file'] == file_path]
        return self.graph.subgraph(nodes).copy()
    
    def get_callers(self, node_id: str) -> List[str]:
        """Get list of nodes that call the specified node.
        
        Args:
            node_id: Node to find callers for
            
        Returns:
            List of caller node IDs
        """
        return list(self.graph.predecessors(node_id))
    
    def get_callees(self, node_id: str) -> List[str]:
        """Get list of nodes called by the specified node.
        
        Args:
            node_id: Node to find callees for
            
        Returns:
            List of callee node IDs
        """
        return list(self.graph.successors(node_id))
