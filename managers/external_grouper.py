"""Groups external dependencies by package type."""

from typing import Dict, List
from core.parser import CodeNode


class ExternalGrouper:
    """Groups external dependencies by package type."""
    
    def create_groups(self, nodes: Dict[str, CodeNode]) -> Dict[str, List[str]]:
        """Create grouped nodes for external dependencies."""
        groups = {
            'stdlib': [],
            'third_party': [],
            'builtin': []
        }
        
        for node_id, node in nodes.items():
            if hasattr(node, 'is_external') and node.is_external:
                package_type = getattr(node, 'package_type', 'third_party')
                if package_type in groups:
                    groups[package_type].append(node_id)
        
        return groups
    
    def create_group_nodes(self, groups: Dict[str, List[str]]) -> Dict[str, CodeNode]:
        """Create collapsed group nodes."""
        group_nodes = {}
        
        icons = {
            'stdlib': '📚',
            'third_party': '📦',
            'builtin': '⚙️'
        }
        
        for group_type, members in groups.items():
            if members:
                group_id = f"__group__{group_type}"
                group_nodes[group_id] = CodeNode(
                    name=f"{icons[group_type]} {group_type.replace('_', ' ').title()} ({len(members)})",
                    node_type='external_group',
                    file_path='',
                    line_number=0
                )
                setattr(group_nodes[group_id], 'is_external', True)
                setattr(group_nodes[group_id], 'is_collapsed', True)
                setattr(group_nodes[group_id], 'children', members)
                setattr(group_nodes[group_id], 'package_type', group_type)
        
        return group_nodes
    
    def group_by_package(self, nodes: Dict[str, CodeNode]) -> Dict[str, List[str]]:
        """Group external nodes by specific package name."""
        package_groups = {}
        
        for node_id, node in nodes.items():
            if hasattr(node, 'is_external') and node.is_external:
                package_name = getattr(node, 'package_name', 'unknown')
                if package_name not in package_groups:
                    package_groups[package_name] = []
                package_groups[package_name].append(node_id)
        
        return package_groups
