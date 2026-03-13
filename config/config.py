"""Configuration settings for CodeMesh application."""

from typing import Dict, Any

# Application settings
APP_CONFIG: Dict[str, Any] = {
    'page_title': 'CodeMesh - Python Code Analyzer',
    'page_icon': '🔍',
    'layout': 'wide',
    'max_file_size_mb': 500,
    'cache_ttl_seconds': 300,
}

# UI settings
UI_CONFIG: Dict[str, Any] = {
    'max_depth_range': (1, 20),
    'max_depth_default': 10,
    'display_limit_range': (5, 100),
    'display_limit_default': 20,
    'search_results_limit': 10,
    'file_tree_expanded': False,
}

# Analysis settings
ANALYSIS_CONFIG: Dict[str, Any] = {
    'supported_extensions': ['.py', '.zip'],
    'default_sort_by': 'calls',
    'complexity_threshold_warning': 10,
    'complexity_threshold_error': 20,
}

# Logging settings
LOGGING_CONFIG: Dict[str, Any] = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# Export settings
EXPORT_CONFIG: Dict[str, Any] = {
    'json_filename': 'codemesh_analysis.json',
    'csv_filename': 'codemesh_metrics.csv',
    'json_indent': 2,
}

# Error messages
ERROR_MESSAGES: Dict[str, str] = {
    'no_files': '📤 Upload Python files to start analysis',
    'no_analyzer': 'No analyzer available',
    'node_not_found': 'Node not found',
    'validation_error': '❌ Validation error: {}',
    'processing_error': '❌ Error processing files: {}',
    'no_matches': 'No matches found',
}

# Success messages
SUCCESS_MESSAGES: Dict[str, str] = {
    'analysis_complete': '✅ Successfully analyzed {} file(s) with {} code elements',
    'parsing_warning': '⚠️ Failed to parse {} file(s)',
}