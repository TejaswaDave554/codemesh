"""Constants and configuration values for CodeMesh application."""

from typing import Dict, List, Tuple

# File handling constants
MAX_FILE_SIZE_MB = 100
MAX_TOTAL_SIZE_MB = 500
SUPPORTED_EXTENSIONS = ['.py', '.zip']

# Analysis constants
DEFAULT_MAX_DEPTH = 10
DEFAULT_DISPLAY_LIMIT = 20
COMPLEXITY_THRESHOLD_WARNING = 10
COMPLEXITY_THRESHOLD_ERROR = 20

# UI constants
SEARCH_RESULTS_LIMIT = 10
FILE_TREE_EXPANDED = False

# Cache settings
CACHE_TTL_SECONDS = 300

# External file patterns for detection
EXTERNAL_FILE_PATTERNS = [
    r'open\(["\']([^"\'\n]+\.(json|txt|csv|xml|yaml|yml|ini|conf|log))["\']\)',
    r'read_csv\(["\']([^"\'\n]+\.csv)["\']\)',
    r'load\(["\']([^"\'\n]+\.(json|yaml|yml))["\']\)',
]

# Node type colors for visualizations
NODE_TYPE_COLORS = {
    'function': '#3498db',
    'method': '#2ecc71', 
    'class': '#e74c3c',
    'external_file': '#f39c12'
}

# Complexity color mapping
COMPLEXITY_COLORS = {
    'low': '#2ecc71',      # Green for complexity 1-5
    'medium': '#f39c12',   # Orange for complexity 6-10
    'high': '#e74c3c'      # Red for complexity 11+
}

# Export file names
EXPORT_JSON_FILENAME = 'codemesh_analysis.json'
EXPORT_CSV_FILENAME = 'codemesh_metrics.csv'

# Logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'