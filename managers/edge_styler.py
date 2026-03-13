"""Edge styling system for different relationship types."""

from typing import Dict, Any


class EdgeStyler:
    """Manages edge styling based on relationship type."""
    
    STYLES = {
        'internal': {
            'color': '#2c3e50',
            'width': 2,
            'dash': 'solid'
        },
        'stdlib': {
            'color': '#f39c12',
            'width': 1.5,
            'dash': 'dash'
        },
        'third_party': {
            'color': '#e74c3c',
            'width': 1,
            'dash': 'dot'
        },
        'builtin': {
            'color': '#9b59b6',
            'width': 1,
            'dash': 'dashdot'
        },
        'inherits': {
            'color': '#e74c3c',
            'width': 2,
            'dash': 'solid'
        },
        'uses': {
            'color': '#f39c12',
            'width': 1,
            'dash': 'dot'
        }
    }
    
    @classmethod
    def get_edge_style(cls, source_data: Dict[str, Any], target_data: Dict[str, Any], 
                      relation: str = 'calls') -> Dict[str, Any]:
        """Get edge style based on source, target, and relationship type."""
        if relation in ['inherits', 'uses']:
            return cls.STYLES[relation]
        
        if target_data.get('is_external', False):
            package_type = target_data.get('package_type', 'third_party')
            return cls.STYLES.get(package_type, cls.STYLES['third_party'])
        
        return cls.STYLES['internal']
    
    @classmethod
    def get_glow_style(cls) -> Dict[str, Any]:
        """Get glow effect style for nodes with external dependencies."""
        return {
            'color': 'rgba(255, 165, 0, 0.3)',
            'size_multiplier': 1.5,
            'line_width': 10,
            'line_color': 'rgba(255, 165, 0, 0.1)'
        }