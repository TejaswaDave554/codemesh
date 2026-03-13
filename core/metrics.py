"""Code quality metrics calculation module.

This module provides functions to calculate various code metrics such as
function call counts, complexity, and dependency analysis.
"""

import networkx as nx
from typing import Dict, List, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculates code quality and complexity metrics.
    
    This class analyzes a code graph to compute various metrics about the codebase
    including call frequencies, complexity, and dependency patterns.
    """
    
    def __init__(self, graph: nx.DiGraph):
        """Initialize calculator with a code graph.
        
        Args:
            graph: NetworkX directed graph of code relationships
        """
        self.graph = graph
    
    def get_summary_metrics(self) -> Dict[str, int]:
        """Calculate summary statistics for the codebase.
        
        Returns:
            Dictionary containing counts of functions, classes, and methods
        """
        node_types = [d['type'] for _, d in self.graph.nodes(data=True)]
        type_counts = Counter(node_types)
        
        return {
            'total_functions': type_counts.get('function', 0),
            'total_classes': type_counts.get('class', 0),
            'total_methods': type_counts.get('method', 0),
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges()
        }
    
    def get_most_called(self, top_n: int = 10) -> List[Tuple[str, str, int]]:
        """Find most frequently called functions.
        
        Args:
            top_n: Number of top results to return
            
        Returns:
            List of tuples (node_id, name, call_count) sorted by call count
        """
        call_counts = []
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            if in_degree > 0:
                name = self.graph.nodes[node]['name']
                call_counts.append((node, name, in_degree))
        
        call_counts.sort(key=lambda x: x[2], reverse=True)
        return call_counts[:top_n]
    
    def get_nodes_by_complexity(self, top_n: int = 10) -> List[Tuple[str, str, int]]:
        """Get nodes sorted by complexity.
        
        Args:
            top_n: Number of top results to return
            
        Returns:
            List of tuples (node_id, name, complexity) sorted by complexity
        """
        complexities = []
        for node, data in self.graph.nodes(data=True):
            if data['type'] in ['function', 'method']:
                complexities.append((node, data['name'], data.get('complexity', 1)))
        
        complexities.sort(key=lambda x: x[2], reverse=True)
        return complexities[:top_n]
    
    def get_sorted_nodes(self, sort_by: str = 'calls') -> List[Tuple[str, str, int]]:
        """Get all nodes sorted by specified metric.
        
        Args:
            sort_by: 'calls' or 'complexity'
            
        Returns:
            List of tuples (node_id, name, metric_value)
        """
        if sort_by == 'complexity':
            return self.get_nodes_by_complexity(top_n=self.graph.number_of_nodes())
        else:
            return self.get_most_called(top_n=self.graph.number_of_nodes())
    
    def get_unused_functions(self) -> List[Tuple[str, str]]:
        """Find functions with no callers (potentially unused).
        
        Returns:
            List of tuples (node_id, name) for functions with no callers
        """
        unused = []
        for node, data in self.graph.nodes(data=True):
            if data['type'] in ['function', 'method']:
                if self.graph.in_degree(node) == 0:
                    unused.append((node, data['name']))
        return unused
    
    def get_max_call_depth(self) -> int:
        """Calculate maximum call depth in the graph.
        
        Returns:
            Maximum depth of call chains
        """
        if self.graph.number_of_nodes() == 0:
            return 0
        
        try:
            # Check if graph has cycles
            if not nx.is_directed_acyclic_graph(self.graph):
                # For cyclic graphs, use a different approach
                max_depth = 0
                for node in self.graph.nodes():
                    try:
                        # BFS with depth limit to avoid infinite loops
                        depth = self._calculate_depth_bfs(node, max_limit=100)
                        max_depth = max(max_depth, depth)
                    except Exception:
                        continue
                return max_depth
            else:
                return nx.dag_longest_path_length(self.graph)
        except (nx.NetworkXError, RecursionError) as e:
            logger.warning(f"Error calculating max depth: {e}")
            return 0
    
    def _calculate_depth_bfs(self, start_node: str, max_limit: int = 100) -> int:
        """Calculate depth using BFS with cycle detection.
        
        Args:
            start_node: Starting node
            max_limit: Maximum depth to prevent infinite loops
            
        Returns:
            Maximum depth from start node
        """
        visited = {start_node}
        queue = [(start_node, 0)]
        max_depth = 0
        
        while queue:
            node, depth = queue.pop(0)
            if depth >= max_limit:
                return max_limit
            
            max_depth = max(max_depth, depth)
            for successor in self.graph.successors(node):
                if successor not in visited:
                    visited.add(successor)
                    queue.append((successor, depth + 1))
        
        return max_depth
    
    def get_most_dependencies(self, top_n: int = 10) -> List[Tuple[str, str, int]]:
        """Find functions with most outgoing dependencies.
        
        Args:
            top_n: Number of top results to return
            
        Returns:
            List of tuples (node_id, name, dependency_count)
        """
        dependencies = []
        for node in self.graph.nodes():
            out_degree = self.graph.out_degree(node)
            if out_degree > 0:
                name = self.graph.nodes[node]['name']
                dependencies.append((node, name, out_degree))
        
        dependencies.sort(key=lambda x: x[2], reverse=True)
        return dependencies[:top_n]
    
    def get_complexity_stats(self) -> Dict[str, float]:
        """Calculate complexity statistics across the codebase.
        
        Returns:
            Dictionary with average, max, and min complexity values
        """
        complexities = [d.get('complexity', 1) for _, d in self.graph.nodes(data=True)]
        
        if not complexities:
            return {'avg': 0, 'max': 0, 'min': 0}
        
        return {
            'avg': sum(complexities) / len(complexities),
            'max': max(complexities),
            'min': min(complexities)
        }
    
    def get_high_complexity_nodes(self, threshold: int = 10) -> List[Tuple[str, str, int]]:
        """Find nodes with complexity above threshold.
        
        Args:
            threshold: Minimum complexity to include
            
        Returns:
            List of tuples (node_id, name, complexity)
        """
        high_complexity = []
        for node, data in self.graph.nodes(data=True):
            complexity = data.get('complexity', 1)
            if complexity >= threshold:
                high_complexity.append((node, data['name'], complexity))
        
        high_complexity.sort(key=lambda x: x[2], reverse=True)
        return high_complexity
