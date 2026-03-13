"""Managers package for collapse and external dependency management."""

from .external_detector import ExternalDependencyDetector
from .collapse_manager import CollapseManager
from .external_grouper import ExternalGrouper
from .edge_styler import EdgeStyler

__all__ = [
    'ExternalDependencyDetector',
    'CollapseManager',
    'ExternalGrouper',
    'EdgeStyler',
]
