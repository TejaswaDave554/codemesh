"""Python AST parsing module for code structure extraction.

This module uses Python's built-in ast module to parse Python source files and extract
functions, classes, methods, calls, and import relationships.
"""

import ast
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple


@dataclass
class CodeNode:
    """Represents a code element (function, class, or method).
    
    Attributes:
        name: Name of the code element
        node_type: Type of element ('function', 'class', 'method')
        file_path: Path to the file containing this element
        line_number: Line number where element is defined
        parameters: List of parameter names
        calls: Set of function/method names called by this element
        parent_class: Name of parent class (for methods)
        base_classes: List of base class names (for classes)
        source_code: Source code snippet of the element
        complexity: Cyclomatic complexity estimate
    """
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
                tree = ast.parse(content)
                self._extract_imports(tree, result, filepath)
                self._extract_nodes(tree, result, content)
            except SyntaxError as e:
                result.errors[filepath] = f"Syntax error: {str(e)}"
            except Exception as e:
                result.errors[filepath] = f"Parse error: {str(e)}"
        
        return result
    
    def _extract_imports(self, tree: ast.AST, result: ParseResult, filepath: str):
        """Extract import statements from AST.
        
        Args:
            tree: AST tree to analyze
            result: ParseResult to populate
            filepath: Path to the file being parsed
        """
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(('import', alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(('from', f"{module}.{alias.name}"))
        result.imports[filepath] = imports
    
    def _extract_nodes(self, tree: ast.AST, result: ParseResult, source: str):
        """Extract functions, classes, and methods from AST.
        
        Args:
            tree: AST tree to analyze
            result: ParseResult to populate
            source: Original source code for extracting snippets
        """
        source_lines = source.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._process_class(node, result, source_lines)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
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
        params = [arg.arg for arg in node.args.args]
        calls = self._extract_calls(node)
        complexity = self._calculate_complexity(node)
        
        code_node = CodeNode(
            name=node.name,
            node_type='function',
            file_path=self.current_file,
            line_number=node.lineno,
            parameters=params,
            calls=calls,
            source_code=self._get_source_snippet(node, source_lines),
            complexity=complexity
        )
        result.nodes[func_id] = code_node
    
    def _process_method(self, node: ast.FunctionDef, result: ParseResult, source_lines: List[str]):
        """Process a method definition node.
        
        Args:
            node: AST FunctionDef node
            result: ParseResult to populate
            source_lines: Source code lines for extracting snippets
        """
        method_id = f"{self.current_file}::{self.current_class}.{node.name}"
        params = [arg.arg for arg in node.args.args]
        calls = self._extract_calls(node)
        complexity = self._calculate_complexity(node)
        
        code_node = CodeNode(
            name=node.name,
            node_type='method',
            file_path=self.current_file,
            line_number=node.lineno,
            parameters=params,
            calls=calls,
            parent_class=self.current_class,
            source_code=self._get_source_snippet(node, source_lines),
            complexity=complexity
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
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
