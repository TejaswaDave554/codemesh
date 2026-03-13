"""Graph building and code analysis module.

This module constructs NetworkX graphs from parsed code structures and provides
analysis capabilities for understanding code relationships and dependencies.
"""

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
import logging
from .parser import ParseResult, CodeNode

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes parsed code and builds relationship graphs.
    
    This class takes parsed code structures and builds a NetworkX directed graph
    representing all functions, classes, methods, and their relationships.
    """
    
    def __init__(self, parse_result: ParseResult):
        """Initialize analyzer with parse results."""
        self.parse_result = parse_result
        self.graph = nx.DiGraph()
        self.collapse_manager = None
        self.external_grouper = None
        
        try:
            from managers.collapse_manager import CollapseManager
            from managers.external_grouper import ExternalGrouper
            self.collapse_manager = CollapseManager()
            self.external_grouper = ExternalGrouper()
        except ImportError:
            pass
        
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
                complexity=node.complexity,
                decorators=getattr(node, 'decorators', []),
                external_refs=getattr(node, 'external_refs', set()),
                is_external=getattr(node, 'is_external', False),
                package_name=getattr(node, 'package_name', None),
                package_type=getattr(node, 'package_type', None),
                external_calls=getattr(node, 'external_calls', set())
            )
        
        for node_id, node in self.parse_result.nodes.items():
            for call in node.calls:
                target_id = self._resolve_call(node, call)
                if target_id and target_id in self.graph:
                    self.graph.add_edge(node_id, target_id, relation='calls')
            
            for ext_ref in getattr(node, 'external_refs', set()):
                ext_id = f"{node.file_path}::external::{ext_ref}"
                if ext_id in self.graph:
                    self.graph.add_edge(node_id, ext_id, relation='uses')
        
        for node_id, node in self.parse_result.nodes.items():
            if node.node_type == 'class':
                for base_class in node.base_classes:
                    base_id = self._find_class(base_class, node.file_path)
                    if base_id:
                        self.graph.add_edge(node_id, base_id, relation='inherits')
        
        self._create_external_groups()
    
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
            logger.warning(f"Root node {root_node} not found in graph")
            return nx.DiGraph()
        
        # Limit max_depth to prevent excessive memory usage
        max_depth = min(max_depth, 50)
        
        nodes = {root_node}
        current_level = {root_node}
        visited = {root_node}
        
        for depth in range(max_depth):
            next_level = set()
            for node in current_level:
                successors = set(self.graph.successors(node))
                # Avoid cycles
                successors = successors - visited
                next_level.update(successors)
            
            if not next_level:
                break
            
            # Limit nodes per level to prevent explosion
            if len(next_level) > 1000:
                logger.warning(f"Too many nodes at depth {depth}, limiting to 1000")
                next_level = set(list(next_level)[:1000])
            
            nodes.update(next_level)
            visited.update(next_level)
            current_level = next_level
            
            # Safety check for total nodes
            if len(nodes) > 5000:
                logger.warning(f"Node limit reached at depth {depth}")
                break
        
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
            logger.warning(f"Node {node_id} not found in graph")
            return nx.DiGraph()
        
        # Limit radius to prevent excessive computation
        radius = min(radius, 10)
        
        nodes = {node_id}
        for _ in range(radius):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self.graph.predecessors(node))
                new_nodes.update(self.graph.successors(node))
            
            # Prevent explosion
            if len(new_nodes) > 1000:
                logger.warning(f"Neighborhood too large, limiting to 1000 nodes")
                new_nodes = set(list(new_nodes)[:1000])
                break
            
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
        """Get list of nodes called by the specified node."""
        return list(self.graph.successors(node_id))
    
    def _create_external_groups(self):
        """Create grouped nodes for external dependencies."""
        if not self.external_grouper:
            return
        
        groups = self.external_grouper.create_groups(self.parse_result.nodes)
        group_nodes = self.external_grouper.create_group_nodes(groups)
        
        for group_id, group_node in group_nodes.items():
            self.graph.add_node(
                group_id,
                name=group_node.name,
                type=group_node.node_type,
                file=group_node.file_path,
                line=group_node.line_number,
                is_external=True,
                is_collapsed=True,
                children=getattr(group_node, 'children', []),
                package_type=getattr(group_node, 'package_type', None)
            )
            
            if self.collapse_manager:
                self.collapse_manager.collapse_node(group_id, getattr(group_node, 'children', []))
    
    def get_filtered_graph(self, show_external: bool = True, 
                          show_collapsed: bool = True,
                          show_unused: bool = False,
                          minimal_view: bool = True) -> nx.DiGraph:
        """Get filtered graph based on visibility settings."""
        filtered_graph = self.graph.copy()
        
        # Remove external nodes if not requested
        if not show_external:
            external_nodes = [
                node for node, data in filtered_graph.nodes(data=True)
                if data.get('is_external', False)
            ]
            filtered_graph.remove_nodes_from(external_nodes)
        
        # Apply aggressive filtering for minimal view
        if minimal_view:
            filtered_graph = self._apply_minimal_filtering(filtered_graph)
        
        # Remove unused/unnecessary functions
        if not show_unused:
            unnecessary_nodes = []
            for node, data in filtered_graph.nodes(data=True):
                # Skip if it's external (already handled above)
                if data.get('is_external', False):
                    continue
                
                # Remove if it has zero incoming calls (unused)
                in_degree = filtered_graph.in_degree(node)
                out_degree = filtered_graph.out_degree(node)
                
                # Keep main functions and entry points
                if data.get('name') in ['main', '__init__', '__main__']:
                    continue
                
                # Remove if:
                # 1. No incoming calls AND no outgoing calls (isolated)
                # 2. Only calls external functions (no internal dependencies)
                if in_degree == 0 and out_degree == 0:
                    unnecessary_nodes.append(node)
                elif in_degree == 0 and out_degree > 0:
                    # Check if it only calls external functions
                    all_external = True
                    for successor in filtered_graph.successors(node):
                        successor_data = filtered_graph.nodes.get(successor, {})
                        if not successor_data.get('is_external', False):
                            all_external = False
                            break
                    if all_external:
                        unnecessary_nodes.append(node)
            
            filtered_graph.remove_nodes_from(unnecessary_nodes)
        
        # Handle collapsed nodes
        if show_collapsed and self.collapse_manager:
            visible_nodes = self.collapse_manager.get_visible_nodes(list(filtered_graph.nodes()))
            filtered_graph = filtered_graph.subgraph(visible_nodes).copy()
        
        return filtered_graph

    def _apply_minimal_filtering(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Apply focused filtering to remove redundant methods like __init__."""
        nodes_to_remove = set()

        # Define redundant method patterns (the main culprits taking up space)
        redundant_methods = {
            '__init__', '__new__', '__del__', '__enter__', '__exit__',
            '__str__', '__repr__', '__len__', '__bool__', '__hash__', 
            '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__',
            '__getitem__', '__setitem__', '__delitem__', '__contains__',
            '__iter__', '__next__', '__call__', '__getattr__', '__setattr__',
            '__delattr__', '__dir__', '__format__', '__sizeof__'
        }

        # Simple getter/setter patterns
        simple_patterns = ['get_', 'set_', '_get', '_set']

        for node, data in graph.nodes(data=True):
            if data.get('is_external', False):
                continue

            name = str(data.get('name', '')).lower()
            complexity = data.get('complexity', 1)

            # Remove redundant magic methods (these are the main space wasters)
            if name in redundant_methods:
                nodes_to_remove.add(node)
                continue

            # Remove simple getters/setters with low complexity
            if any(pattern in name for pattern in simple_patterns) and complexity <= 2:
                nodes_to_remove.add(node)
                continue

            # Remove very simple functions that are likely just property accessors
            if complexity == 1 and len(name) <= 4 and not name in ['main', 'run', 'test']:
                nodes_to_remove.add(node)
                continue

            # Remove functions that only have trivial connections
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)

            # Keep meaningful entry points
            if name in ['main', '__main__', 'run', 'execute', 'start', 'test']:
                continue

            # Remove isolated nodes or nodes with only trivial connections
            if in_degree == 0 and out_degree <= 1 and complexity <= 2:
                # Check if it only calls other redundant methods
                only_redundant_calls = True
                try:
                    for successor in graph.successors(node):
                        succ_data = graph.nodes.get(successor, {})
                        succ_name = str(succ_data.get('name', '')).lower()

                        if (not succ_data.get('is_external', False) and 
                            succ_name not in redundant_methods and
                            not any(pattern in succ_name for pattern in simple_patterns)):
                            only_redundant_calls = False
                            break
                except Exception:
                    pass

                if only_redundant_calls:
                    nodes_to_remove.add(node)
                    continue

        # Remove the identified nodes
        filtered_graph = graph.copy()
        filtered_graph.remove_nodes_from(nodes_to_remove)

        # Clean up any nodes that became isolated after filtering
        isolated_nodes = []
        for node, data in filtered_graph.nodes(data=True):
            if data.get('is_external', False):
                continue

            name = str(data.get('name', '')).lower()
            if name in ['main', '__main__', 'run', 'execute', 'start', 'test']:
                continue

            in_degree = filtered_graph.in_degree(node)
            out_degree = filtered_graph.out_degree(node)

            if in_degree == 0 and out_degree == 0:
                isolated_nodes.append(node)

        filtered_graph.remove_nodes_from(isolated_nodes)

        return filtered_graph
