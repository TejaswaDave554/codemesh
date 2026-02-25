"""Code quality metrics calculation module.

This module provides functions to calculate various code metrics such as
function call counts, complexity, and dependency analysis.
"""

import networkx as nx
from typing import Dict, List, Tuple
from collections import Counter


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
            List of tuples (node_id, name, call_count)
        """
        call_counts = []
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            if in_degree > 0:
                name = self.graph.nodes[node]['name']
                call_counts.append((node, name, in_degree))
        
        call_counts.sort(key=lambda x: x[2], reverse=True)
        return call_counts[:top_n]
    
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
            return nx.dag_longest_path_length(self.graph)
        except:
            return 0
    
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
