"""Custom exceptions for CodeMesh application."""


class CodeMeshError(Exception):
    """Base exception for CodeMesh application."""
    pass


class FileProcessingError(CodeMeshError):
    """Raised when file processing fails."""
    pass


class ParseError(CodeMeshError):
    """Raised when code parsing fails."""
    pass


class AnalysisError(CodeMeshError):
    """Raised when code analysis fails."""
    pass


class ValidationError(CodeMeshError):
    """Raised when input validation fails."""
    pass


class FileSizeError(FileProcessingError):
    """Raised when file size exceeds limits."""
    pass


class UnsupportedFileError(FileProcessingError):
    """Raised when file type is not supported."""
    pass