"""Unit tests for CodeMesh application."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.parser import PythonParser, CodeNode, ParseResult
from core.analyzer import CodeAnalyzer
from core.metrics import MetricsCalculator


class TestPythonParser(unittest.TestCase):
    """Test cases for PythonParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = PythonParser()
    
    def test_parse_simple_function(self):
        """Test parsing a simple function."""
        code = """
def hello_world():
    print("Hello, World!")
"""
        result = self.parser.parse_files({"test.py": code})
        self.assertIn("test.py::hello_world", result.nodes)
        node = result.nodes["test.py::hello_world"]
        self.assertEqual(node.name, "hello_world")
        self.assertEqual(node.node_type, "function")
    
    def test_parse_class(self):
        """Test parsing a class."""
        code = """
class MyClass:
    def method(self):
        pass
"""
        result = self.parser.parse_files({"test.py": code})
        self.assertIn("test.py::MyClass", result.nodes)
        self.assertIn("test.py::MyClass.method", result.nodes)
    
    def test_parse_with_syntax_error(self):
        """Test parsing file with syntax error."""
        code = "def broken("
        result = self.parser.parse_files({"test.py": code})
        self.assertIn("test.py", result.errors)


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for CodeAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        code = """
def func_a():
    func_b()

def func_b():
    pass
"""
        parser = PythonParser()
        self.parse_result = parser.parse_files({"test.py": code})
        self.analyzer = CodeAnalyzer(self.parse_result)
    
    def test_graph_creation(self):
        """Test graph is created with nodes."""
        self.assertGreater(self.analyzer.graph.number_of_nodes(), 0)
    
    def test_call_relationships(self):
        """Test call relationships are detected."""
        self.assertGreater(self.analyzer.graph.number_of_edges(), 0)


class TestMetricsCalculator(unittest.TestCase):
    """Test cases for MetricsCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        code = """
def simple():
    pass

def complex_func(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
"""
        parser = PythonParser()
        parse_result = parser.parse_files({"test.py": code})
        analyzer = CodeAnalyzer(parse_result)
        self.metrics = MetricsCalculator(analyzer.graph)
    
    def test_summary_metrics(self):
        """Test summary metrics calculation."""
        summary = self.metrics.get_summary_metrics()
        self.assertIn('total_functions', summary)
        self.assertGreater(summary['total_functions'], 0)
    
    def test_complexity_stats(self):
        """Test complexity statistics."""
        stats = self.metrics.get_complexity_stats()
        self.assertIn('avg', stats)
        self.assertIn('max', stats)
        self.assertIn('min', stats)


if __name__ == '__main__':
    unittest.main()
