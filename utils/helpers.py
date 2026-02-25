"""Shared utility functions for the code analysis tool.

This module contains helper functions used across multiple components of the application.
"""

from typing import Any, Dict, List


def get_node_color(node_type: str) -> str:
    """Get color code for different node types in visualizations.
    
    Args:
        node_type: Type of node ('function', 'class', 'method')
        
    Returns:
        Hex color code string
    """
    colors = {
        'function': '#3498db',  # Blue
        'class': '#2ecc71',     # Green
        'method': '#e67e22'     # Orange
    }
    return colors.get(node_type, '#95a5a6')


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'


def format_parameters(params: List[str]) -> str:
    """Format parameter list for display.
    
    Args:
        params: List of parameter names
        
    Returns:
        Formatted parameter string
    """
    if not params:
        return "()"
    return f"({', '.join(params)})"
