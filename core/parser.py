"""Python AST parsing module for code structure extraction.

This module uses Python's built-in ast module to parse Python source files and extract
functions, classes, methods, calls, and import relationships.
"""

import ast
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """Represents a code element (function, class, or method)."""
    name: str
    node_type: str
    file_path: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    calls: Set[str] = field(default_factory=set)
    parent_class: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)
    source_code: str = ""
    complexity: int = 1
    external_refs: Set[str] = field(default_factory=set)
    decorators: List[str] = field(default_factory=list)
    is_external: bool = False
    package_name: Optional[str] = None
    package_type: Optional[str] = None
    external_calls: Set[str] = field(default_factory=set)
    is_collapsed: bool = False
    children: List[str] = field(default_factory=list)
    parent_group: Optional[str] = None


@dataclass
class ParseResult:
    """Container for parsed code analysis results.
    
    Attributes:
        nodes: Dictionary mapping node identifiers to CodeNode objects
        imports: Dictionary mapping file paths to their import statements
        errors: Dictionary mapping file paths to parsing error messages
    """
    nodes: Dict[str, CodeNode] = field(default_factory=dict)
    imports: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)


class PythonParser:
    """Parses Python source code to extract structure and relationships.
    
    This parser uses the ast module to analyze Python files and extract functions,
    classes, methods, function calls, and import relationships.
    """
    
    def __init__(self):
        """Initialize the parser with empty state."""
        self.current_file = ""
        self.current_class = None
        self.context_stack = []
        self.external_detector = None
        try:
            from managers.external_detector import ExternalDependencyDetector
            self.external_detector = ExternalDependencyDetector()
        except ImportError:
            pass
    
    def parse_files(self, files: Dict[str, str]) -> ParseResult:
        """Parse multiple Python files and extract code structure.
        
        Args:
            files: Dictionary mapping file paths to source code content
            
        Returns:
            ParseResult containing all extracted nodes, imports, and errors
        """
        result = ParseResult()
        
        for filepath, content in files.items():
            self.current_file = filepath
            try:
                # Skip empty or very small files
                if not content or len(content.strip()) < 10:
                    logger.warning(f"Skipping empty/small file: {filepath}")
                    continue
                
                # Try to parse with error recovery
                tree = self._safe_parse(content, filepath)
                if tree:
                    self._extract_imports(tree, result, filepath)
                    self._extract_nodes(tree, result, content)
                    self._extract_external_refs(content, result, filepath)
            except SyntaxError as e:
                result.errors[filepath] = f"Syntax error at line {e.lineno}: {e.msg}"
                logger.error(f"Syntax error in {filepath}: {e}")
            except UnicodeDecodeError as e:
                result.errors[filepath] = f"Encoding error: {str(e)}"
                logger.error(f"Encoding error in {filepath}: {e}")
            except Exception as e:
                result.errors[filepath] = f"Parse error: {str(e)}"
                logger.error(f"Unexpected error parsing {filepath}: {e}")
        
        return result
    
    def _safe_parse(self, content: str, filepath: str) -> Optional[ast.AST]:
        """Safely parse content with error recovery.
        
        Args:
            content: Source code content
            filepath: File path for logging
            
        Returns:
            AST tree or None if parsing fails
        """
        try:
            return ast.parse(content)
        except SyntaxError:
            # Try to parse with type comments disabled
            try:
                return ast.parse(content)
            except SyntaxError:
                raise
    
    def _extract_external_refs(self, content: str, result: ParseResult, filepath: str):
        """Extract references to external files (json, txt, csv, etc.).
        
        Args:
            content: Source code content
            result: ParseResult to populate
            filepath: Current file path
        """
        # Pattern to match file operations
        file_patterns = [
            r'open\(["\']([^"\'\n]+\.(json|txt|csv|xml|yaml|yml|ini|conf|log))["\']',
            r'read_csv\(["\']([^"\'\n]+\.csv)["\']',
            r'load\(["\']([^"\'\n]+\.(json|yaml|yml))["\']',
        ]
        
        external_files = set()
        for pattern in file_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                external_files.add(match.group(1))
        
        # Create external file nodes
        for ext_file in external_files:
            ext_id = f"{filepath}::external::{ext_file}"
            if ext_id not in result.nodes:
                result.nodes[ext_id] = CodeNode(
                    name=ext_file,
                    node_type='external_file',
                    file_path=filepath,
                    line_number=0,
                    external_refs={ext_file}
                )
    
    def _extract_imports(self, tree: ast.AST, result: ParseResult, filepath: str):
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(('import', alias.name))
                    self._process_external_import(alias.name, result, filepath)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(('from', f"{module}.{alias.name}"))
                    self._process_external_import(module, result, filepath)
        result.imports[filepath] = imports
    
    def _process_external_import(self, module_name: str, result: ParseResult, filepath: str):
        """Process external imports and create nodes."""
        if not self.external_detector:
            return
        
        if self.external_detector.is_external(module_name):
            package_type = self.external_detector.classify_import(module_name)
            package_name = self.external_detector.get_package_name(module_name)
            
            ext_id = f"__external__{package_name}::{module_name}"
            if ext_id not in result.nodes:
                result.nodes[ext_id] = CodeNode(
                    name=module_name,
                    node_type='external_function',
                    file_path='',
                    line_number=0,
                    is_external=True,
                    package_name=package_name,
                    package_type=package_type
                )
    
    def _extract_nodes(self, tree: ast.AST, result: ParseResult, source: str):
        """Extract functions, classes, and methods from AST.
        
        Args:
            tree: AST tree to analyze
            result: ParseResult to populate
            source: Original source code for extracting snippets
        """
        source_lines = source.split('\n')
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self._process_class(node, result, source_lines)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node, result, source_lines)
    
    def _process_class(self, node: ast.ClassDef, result: ParseResult, source_lines: List[str]):
        """Process a class definition node.
        
        Args:
            node: AST ClassDef node
            result: ParseResult to populate
            source_lines: Source code lines for extracting snippets
        """
        base_classes = [self._get_name(base) for base in node.bases]
        class_id = f"{self.current_file}::{node.name}"
        
        code_node = CodeNode(
            name=node.name,
            node_type='class',
            file_path=self.current_file,
            line_number=node.lineno,
            base_classes=base_classes,
            source_code=self._get_source_snippet(node, source_lines)
        )
        result.nodes[class_id] = code_node
        
        old_class = self.current_class
        self.current_class = node.name
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_method(item, result, source_lines)
        
        self.current_class = old_class
    
    def _process_function(self, node: ast.FunctionDef, result: ParseResult, source_lines: List[str]):
        """Process a function definition node.
        
        Args:
            node: AST FunctionDef node
            result: ParseResult to populate
            source_lines: Source code lines for extracting snippets
        """
        if self.current_class:
            return
        
        func_id = f"{self.current_file}::{node.name}"
        params = self._extract_params(node.args)
        calls = self._extract_calls(node)
        complexity = self._calculate_complexity(node)
        decorators = self._extract_decorators(node)
        
        code_node = CodeNode(
            name=node.name,
            node_type='function',
            file_path=self.current_file,
            line_number=node.lineno,
            parameters=params,
            calls=calls,
            source_code=self._get_source_snippet(node, source_lines),
            complexity=complexity,
            decorators=decorators
        )
        result.nodes[func_id] = code_node
    
    def _extract_params(self, args: ast.arguments) -> List[str]:
        """Extract parameter names including *args and **kwargs.
        
        Args:
            args: AST arguments node
            
        Returns:
            List of parameter names
        """
        params = [arg.arg for arg in args.args]
        if args.vararg:
            params.append(f"*{args.vararg.arg}")
        if args.kwarg:
            params.append(f"**{args.kwarg.arg}")
        return params
    
    def _extract_decorators(self, node: ast.FunctionDef) -> List[str]:
        """Extract decorator names from function.
        
        Args:
            node: AST FunctionDef node
            
        Returns:
            List of decorator names
        """
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
        return decorators
    
    def _process_method(self, node: ast.FunctionDef, result: ParseResult, source_lines: List[str]):
        """Process a method definition node.
        
        Args:
            node: AST FunctionDef node
            result: ParseResult to populate
            source_lines: Source code lines for extracting snippets
        """
        method_id = f"{self.current_file}::{self.current_class}.{node.name}"
        params = self._extract_params(node.args)
        calls = self._extract_calls(node)
        complexity = self._calculate_complexity(node)
        decorators = self._extract_decorators(node)
        
        code_node = CodeNode(
            name=node.name,
            node_type='method',
            file_path=self.current_file,
            line_number=node.lineno,
            parameters=params,
            calls=calls,
            parent_class=self.current_class,
            source_code=self._get_source_snippet(node, source_lines),
            complexity=complexity,
            decorators=decorators
        )
        result.nodes[method_id] = code_node
    
    def _extract_calls(self, node: ast.AST) -> Set[str]:
        """Extract function/method calls from a node.
        
        Args:
            node: AST node to analyze
            
        Returns:
            Set of called function/method names
        """
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = self._get_call_name(child.func)
                if call_name:
                    calls.add(call_name)
        return calls
    
    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        """Extract the name from a call node.
        
        Args:
            node: AST node representing a call
            
        Returns:
            Name of the called function/method or None
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def _get_name(self, node: ast.AST) -> str:
        """Extract name from an AST node.
        
        Args:
            node: AST node
            
        Returns:
            Name string or empty string
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""
    
    def _get_source_snippet(self, node: ast.AST, source_lines: List[str]) -> str:
        """Extract source code snippet for a node.
        
        Args:
            node: AST node
            source_lines: List of source code lines
            
        Returns:
            Source code snippet (up to 10 lines)
        """
        start = node.lineno - 1
        end = min(start + 10, len(source_lines))
        return '\n'.join(source_lines[start:end])
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate basic cyclomatic complexity.
        
        Args:
            node: AST node to analyze
            
        Returns:
            Estimated cyclomatic complexity
        """
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, 
                                 ast.With, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        return complexity
