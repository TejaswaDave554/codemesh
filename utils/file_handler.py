"""File handling utilities for code analysis tool.

This module provides functionality for handling file uploads, extracting zip archives,
and managing Python source files for analysis.
"""

import zipfile
import tempfile
import os
from pathlib import Path
from typing import Dict, List
import logging

from config.constants import MAX_FILE_SIZE_MB, MAX_TOTAL_SIZE_MB
from config.exceptions import FileSizeError, UnsupportedFileError, FileProcessingError

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_TOTAL_SIZE = MAX_TOTAL_SIZE_MB * 1024 * 1024


class FileHandler:
    """Handles file upload, extraction, and organization for code analysis.
    
    This class manages the extraction of Python files from uploads (single files or zip archives)
    and organizes them for parsing and analysis.
    """
    
    @staticmethod
    def extract_files(uploaded_files) -> Dict[str, str]:
        """Extract Python files from uploaded files or zip archives.
        
        Args:
            uploaded_files: Single file or list of Streamlit UploadedFile objects
            
        Returns:
            Dictionary mapping file paths to their source code content
            
        Raises:
            ValueError: If files exceed size limits or invalid format
        """
        files = {}
        total_size = 0
        
        # Handle single file or list
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        
        for uploaded_file in uploaded_files:
            try:
                # Check file size
                file_size = uploaded_file.size if hasattr(uploaded_file, 'size') else len(uploaded_file.getvalue())
                if file_size > MAX_FILE_SIZE:
                    raise FileSizeError(f"File {uploaded_file.name} exceeds {MAX_FILE_SIZE_MB}MB limit")
                
                total_size += file_size
                if total_size > MAX_TOTAL_SIZE:
                    raise FileSizeError(f"Total file size exceeds {MAX_TOTAL_SIZE_MB}MB limit")
                
                if uploaded_file.name.endswith('.py'):
                    content = uploaded_file.read().decode('utf-8', errors='ignore')
                    files[uploaded_file.name] = content
                    
                elif uploaded_file.name.endswith('.zip'):
                    extracted = FileHandler._extract_zip(uploaded_file)
                    files.update(extracted)
                else:
                    raise UnsupportedFileError(f"Unsupported file type: {uploaded_file.name}")
                    
            except (UnicodeDecodeError, FileProcessingError) as e:
                logger.error(f"Error processing {uploaded_file.name}: {e}")
                continue
        
        if not files:
            raise FileProcessingError("No valid Python files found")
        
        return files
    
    @staticmethod
    def _extract_zip(uploaded_file) -> Dict[str, str]:
        """Extract Python files from zip archive.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Dictionary of extracted Python files
        """
        files = {}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, uploaded_file.name)
            
            try:
                # Read file content safely
                file_content = uploaded_file.read()
                if not file_content:
                    raise FileProcessingError("Empty zip file")
                
                with open(zip_path, 'wb') as f:
                    f.write(file_content)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Check for zip bombs - both compressed and uncompressed size
                    total_size = sum(info.file_size for info in zip_ref.filelist)
                    compressed_size = sum(info.compress_size for info in zip_ref.filelist)
                    
                    if total_size > MAX_TOTAL_SIZE:
                        raise FileProcessingError(f"Zip archive too large: {total_size / (1024*1024):.1f}MB (max {MAX_TOTAL_SIZE_MB}MB)")
                    
                    # Check compression ratio for zip bomb detection
                    if compressed_size > 0 and total_size / compressed_size > 100:
                        raise FileProcessingError("Suspicious compression ratio detected (possible zip bomb)")
                    
                    # Safely extract files with path traversal protection
                    for member in zip_ref.namelist():
                        # Normalize path and check for traversal
                        member_path = os.path.normpath(os.path.join(tmpdir, member))
                        if not member_path.startswith(os.path.abspath(tmpdir) + os.sep):
                            raise FileProcessingError(f"Path traversal attempt detected: {member}")
                        
                        # Check for suspicious filenames
                        if member.startswith('/') or '..' in member or member.startswith('\\'):
                            raise FileProcessingError(f"Unsafe path in zip: {member}")
                    
                    zip_ref.extractall(tmpdir)
            except zipfile.BadZipFile as e:
                logger.error(f"Invalid zip file: {uploaded_file.name} - {e}")
                raise FileProcessingError(f"Invalid zip file: {uploaded_file.name}")
            except Exception as e:
                logger.error(f"Error extracting zip {uploaded_file.name}: {e}")
                raise
            
            # Extract Python files with size limits
            for root, _, filenames in os.walk(tmpdir):
                for filename in filenames:
                    if filename.endswith('.py'):
                        filepath = os.path.join(root, filename)
                        rel_path = os.path.relpath(filepath, tmpdir)
                        
                        # Skip __pycache__, hidden files, and test files
                        if any(skip in rel_path for skip in ['__pycache__', 'site-packages', '.git']):
                            continue
                        if rel_path.startswith('.') or filename.startswith('.'):
                            continue
                        
                        try:
                            # Check file size before reading
                            file_size = os.path.getsize(filepath)
                            if file_size > MAX_FILE_SIZE:
                                logger.warning(f"Skipping large file {rel_path}: {file_size / (1024*1024):.1f}MB")
                                continue
                            
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if content.strip():  # Only add non-empty files
                                    files[rel_path] = content
                        except (IOError, OSError) as e:
                            logger.error(f"Error reading {rel_path}: {e}")
                        except Exception as e:
                            logger.error(f"Unexpected error reading {rel_path}: {e}")
        
        return files
    
    @staticmethod
    def get_file_tree(files: Dict[str, str]) -> List[str]:
        """Generate a sorted list of file paths for display.
        
        Args:
            files: Dictionary mapping file paths to their content
            
        Returns:
            Sorted list of file paths
        """
        return sorted(files.keys())
