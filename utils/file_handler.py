"""File handling utilities for code analysis tool.

This module provides functionality for handling file uploads, extracting zip archives,
and managing Python source files for analysis.
"""

import zipfile
import tempfile
import os
from pathlib import Path
from typing import Dict, List


class FileHandler:
    """Handles file upload, extraction, and organization for code analysis.
    
    This class manages the extraction of Python files from uploads (single files or zip archives)
    and organizes them for parsing and analysis.
    """
    
    @staticmethod
    def extract_files(uploaded_file) -> Dict[str, str]:
        """Extract Python files from uploaded file or zip archive.
        
        Args:
            uploaded_file: Streamlit UploadedFile object containing either a .py file or .zip archive
            
        Returns:
            Dictionary mapping file paths to their source code content
            
        Raises:
            ValueError: If the uploaded file is not a .py or .zip file
        """
        files = {}
        
        if uploaded_file.name.endswith('.py'):
            content = uploaded_file.read().decode('utf-8')
            files[uploaded_file.name] = content
            
        elif uploaded_file.name.endswith('.zip'):
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, uploaded_file.name)
                with open(zip_path, 'wb') as f:
                    f.write(uploaded_file.read())
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                
                for root, _, filenames in os.walk(tmpdir):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            filepath = os.path.join(root, filename)
                            rel_path = os.path.relpath(filepath, tmpdir)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                try:
                                    files[rel_path] = f.read()
                                except Exception:
                                    continue
        else:
            raise ValueError("Only .py and .zip files are supported")
        
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
