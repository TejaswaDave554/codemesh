"""Utility module for sample code.

This module provides utility functions used by sample_code.py to demonstrate
cross-file relationship tracking.
"""


def format_output(message, prefix=">>>"):
    """Format output message with prefix.
    
    Args:
        message: Message to format
        prefix: Prefix to add
        
    Returns:
        Formatted string
    """
    return f"{prefix} {message}"


def validate_input(value, min_val=0, max_val=100):
    """Validate input value is within range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False
    
    if value < min_val or value > max_val:
        return False
    
    return True


class Logger:
    """Simple logger class."""
    
    def __init__(self, name):
        """Initialize logger.
        
        Args:
            name: Logger name
        """
        self.name = name
        self.logs = []
    
    def log(self, message):
        """Log a message.
        
        Args:
            message: Message to log
        """
        formatted = format_output(message, f"[{self.name}]")
        self.logs.append(formatted)
        print(formatted)
    
    def get_logs(self):
        """Get all logged messages.
        
        Returns:
            List of log messages
        """
        return self.logs
    
    def clear(self):
        """Clear all logs."""
        self.logs = []


def process_data(data, logger=None):
    """Process data with optional logging.
    
    Args:
        data: Data to process
        logger: Optional Logger instance
        
    Returns:
        Processed data
    """
    if logger:
        logger.log(f"Processing {len(data)} items")
    
    result = []
    for item in data:
        if validate_input(item):
            result.append(item * 2)
        else:
            if logger:
                logger.log(f"Invalid item: {item}")
    
    if logger:
        logger.log(f"Processed {len(result)} valid items")
    
    return result
