"""External dependency detection and classification."""

import sys
import site
from typing import Set, Optional


class ExternalDependencyDetector:
    """Detects and classifies external dependencies."""
    
    def __init__(self):
        self.stdlib_modules = self._get_stdlib_modules()
        self.builtin_modules = set(sys.builtin_module_names)
        self.site_packages = self._get_site_packages()
    
    def classify_import(self, module_name: str) -> str:
        """Classify import as stdlib, third_party, builtin, or internal."""
        base_module = module_name.split('.')[0]
        
        if base_module in self.builtin_modules:
            return 'builtin'
        elif base_module in self.stdlib_modules:
            return 'stdlib'
        elif self._is_third_party(base_module):
            return 'third_party'
        else:
            return 'internal'
    
    def is_external(self, module_name: str) -> bool:
        """Check if module is external (not internal code)."""
        classification = self.classify_import(module_name)
        return classification in ['stdlib', 'third_party', 'builtin']
    
    def get_package_name(self, module_name: str) -> str:
        """Extract package name from module path."""
        return module_name.split('.')[0]
    
    def _get_stdlib_modules(self) -> Set[str]:
        """Get list of standard library modules."""
        if hasattr(sys, 'stdlib_module_names'):
            return sys.stdlib_module_names
        
        stdlib = {
            'os', 'sys', 'json', 're', 'math', 'datetime', 'time', 'random',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'logging', 'unittest', 'argparse', 'subprocess', 'threading',
            'multiprocessing', 'asyncio', 'socket', 'http', 'urllib',
            'email', 'csv', 'xml', 'html', 'sqlite3', 'pickle', 'tempfile',
            'shutil', 'glob', 'fnmatch', 'io', 'struct', 'array', 'queue',
            'heapq', 'bisect', 'weakref', 'copy', 'pprint', 'enum', 'dataclasses'
        }
        return stdlib
    
    def _get_site_packages(self) -> Set[str]:
        """Get site-packages directories."""
        try:
            return set(site.getsitepackages())
        except Exception:
            return set()
    
    def _is_third_party(self, module_name: str) -> bool:
        """Check if module is third party."""
        try:
            module = __import__(module_name)
            if hasattr(module, '__file__') and module.__file__:
                for site_pkg in self.site_packages:
                    if site_pkg in module.__file__:
                        return True
        except (ImportError, AttributeError):
            pass
        return False
