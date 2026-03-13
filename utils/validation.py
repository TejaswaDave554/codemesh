"""Security and validation utilities."""

import re
from typing import Optional
from config.constants import MAX_FILE_SIZE_MB, MAX_TOTAL_SIZE_MB
from config.exceptions import ValidationError


def validate_file_size(size: int, max_size: int = MAX_FILE_SIZE_MB * 1024 * 1024) -> None:
    """Validate file size is within limits."""
    if size <= 0:
        raise ValidationError("File size must be positive")
    if size > max_size:
        raise ValidationError(f"File size {size / (1024*1024):.1f}MB exceeds limit {max_size / (1024*1024):.1f}MB")


def validate_filename(filename: str) -> None:
    """Validate filename is safe."""
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    if len(filename) > 255:
        raise ValidationError("Filename too long")
    
    dangerous_patterns = [
        r'\.\.',
        r'^/',
        r'^\\',
        r'[\x00-\x1f]',
        r'[<>:"|?*]'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, filename):
            raise ValidationError(f"Unsafe filename: {filename}")


def validate_node_id(node_id: Optional[str]) -> None:
    """Validate node ID format."""
    if not node_id:
        raise ValidationError("Node ID cannot be empty")
    
    if not isinstance(node_id, str):
        raise ValidationError("Node ID must be a string")
    
    if len(node_id) > 1000:
        raise ValidationError("Node ID too long")
    
    if '::' not in node_id:
        raise ValidationError("Invalid node ID format")


def sanitize_display_limit(limit: int, min_val: int = 1, max_val: int = 100) -> int:
    """Sanitize display limit to safe range."""
    try:
        limit = int(limit)
        return max(min_val, min(limit, max_val))
    except (ValueError, TypeError):
        return 20


def sanitize_depth(depth: int, min_val: int = 1, max_val: int = 20) -> int:
    """Sanitize depth value to safe range."""
    try:
        depth = int(depth)
        return max(min_val, min(depth, max_val))
    except (ValueError, TypeError):
        return 10
