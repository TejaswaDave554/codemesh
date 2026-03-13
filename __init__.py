"""CodeMesh - Python Code Analysis and Visualization Tool.

A comprehensive tool for analyzing Python codebases, extracting relationships,
and creating interactive visualizations of code structure and dependencies.
"""

__version__ = "1.0.0"
__author__ = "CodeMesh Team"

from .core.parser import PythonParser, ParseResult, CodeNode
from .core.analyzer import CodeAnalyzer
from .core.metrics import MetricsCalculator
from .config.exceptions import (
    CodeMeshError,
    FileProcessingError,
    ParseError,
    AnalysisError,
    ValidationError,
    FileSizeError,
    UnsupportedFileError
)

__all__ = [
    "PythonParser",
    "ParseResult", 
    "CodeNode",
    "CodeAnalyzer",
    "MetricsCalculator",
    "CodeMeshError",
    "FileProcessingError",
    "ParseError",
    "AnalysisError",
    "ValidationError",
    "FileSizeError",
    "UnsupportedFileError",
]