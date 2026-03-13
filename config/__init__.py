"""Configuration package for CodeMesh application."""

from .config import (
    APP_CONFIG,
    UI_CONFIG,
    ANALYSIS_CONFIG,
    LOGGING_CONFIG,
    EXPORT_CONFIG,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)
from .constants import (
    MAX_FILE_SIZE_MB,
    MAX_TOTAL_SIZE_MB,
    SUPPORTED_EXTENSIONS,
    DEFAULT_MAX_DEPTH,
    DEFAULT_DISPLAY_LIMIT,
    COMPLEXITY_THRESHOLD_WARNING,
    COMPLEXITY_THRESHOLD_ERROR,
    NODE_TYPE_COLORS,
    COMPLEXITY_COLORS
)
from .exceptions import (
    CodeMeshError,
    FileProcessingError,
    ParseError,
    AnalysisError,
    ValidationError,
    FileSizeError,
    UnsupportedFileError
)

__all__ = [
    'APP_CONFIG',
    'UI_CONFIG',
    'ANALYSIS_CONFIG',
    'LOGGING_CONFIG',
    'EXPORT_CONFIG',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
    'MAX_FILE_SIZE_MB',
    'MAX_TOTAL_SIZE_MB',
    'SUPPORTED_EXTENSIONS',
    'DEFAULT_MAX_DEPTH',
    'DEFAULT_DISPLAY_LIMIT',
    'COMPLEXITY_THRESHOLD_WARNING',
    'COMPLEXITY_THRESHOLD_ERROR',
    'NODE_TYPE_COLORS',
    'COMPLEXITY_COLORS',
    'CodeMeshError',
    'FileProcessingError',
    'ParseError',
    'AnalysisError',
    'ValidationError',
    'FileSizeError',
    'UnsupportedFileError',
]
