"""Metrics calculation for code analysis."""

from pathlib import Path
from typing import Dict, List, Optional

from legacy_inspector.parser_manager import ASTWrapper, get_parser_manager
from legacy_inspector.scanner import FileInfo


class FunctionMetrics:
    """Metrics for a single function."""

    def __init__(self, name: str, start_line: int, end_line: int):
        self.name = name
        self.start_line = start_line
        self.end_line = end_line
        self.loc = end_line - start_line + 1
        self.complexity = 1  # Cyclomatic complexity
        self.parameters = 0
        self.nesting_depth = 0
        self.file_path: Optional[Path] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file": str(self.file_path) if self.file_path else "",
            "start_line": self.start_line,
            "end_line": self.end_line,
            "loc": self.loc,
            "complexity": self.complexity,
            "parameters": self.parameters,
            "nesting_depth": self.nesting_depth,
        }


class FileMetrics:
    """Metrics for a single file."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.loc = 0
        self.functions: List[FunctionMetrics] = []
        self.imports_count = 0
        self.language = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "file": str(self.filepath),
            "language": self.language,
            "loc": self.loc,
            "functions_count": len(self.functions),
            "imports_count": self.imports_count,
            "functions": [f.to_dict() for f in self.functions],
        }


def calculate_cyclomatic_complexity(node, ast_wrapper: ASTWrapper) -> int:
    """
    Calculate cyclomatic complexity for a node.
    Counts decision points: if, while, for, case, &&, ||, etc.
    """
    complexity = 1  # Base complexity

    # Decision point node types by language
    decision_types = {
        "python": ["if_statement", "while_statement", "for_statement", "except_clause"],
        "javascript": [
            "if_statement",
            "while_statement",
            "for_statement",
            "switch_case",
            "catch_clause",
        ],
        "typescript": [
            "if_statement",
            "while_statement",
            "for_statement",
            "switch_case",
            "catch_clause",
        ],
        "java": [
            "if_statement",
            "while_statement",
            "for_statement",
            "enhanced_for_statement",
            "switch_label",
            "catch_clause",
        ],
    }

    decision_nodes = decision_types.get(ast_wrapper.language, [])

    def traverse(n):
        nonlocal complexity
        if n.type in decision_nodes:
            complexity += 1

        # Count logical operators
        if n.type in ["boolean_operator", "binary_expression"]:
            text = ast_wrapper.get_node_text(n)
            complexity += text.count("&&") + text.count("||") + text.count("and") + text.count("or")

        for child in n.children:
            traverse(child)

    traverse(node)
    return complexity


def calculate_nesting_depth(node) -> int:
    """Calculate maximum nesting depth of control structures."""
    max_depth = 0

    def traverse(n, current_depth):
        nonlocal max_depth
        max_depth = max(max_depth, current_depth)

        control_structures = [
            "if_statement",
            "while_statement",
            "for_statement",
            "try_statement",
            "with_statement",
        ]

        new_depth = current_depth + 1 if n.type in control_structures else current_depth

        for child in n.children:
            traverse(child, new_depth)

    traverse(node, 0)
    return max_depth


def count_parameters(func_node, ast_wrapper: ASTWrapper) -> int:
    """Count function parameters."""
    param_types = {
        "python": ["parameters"],
        "javascript": ["formal_parameters"],
        "typescript": ["formal_parameters"],
        "java": ["formal_parameters"],
    }

    param_node_types = param_types.get(ast_wrapper.language, [])

    for child in func_node.children:
        if child.type in param_node_types:
            # Count parameter identifiers
            params = [c for c in child.children if c.type in ["identifier", "parameter"]]
            return len(params)

    return 0


def extract_function_name(func_node, ast_wrapper: ASTWrapper) -> str:
    """Extract function name from node."""
    # Look for identifier node
    for child in func_node.children:
        if child.type == "identifier":
            return ast_wrapper.get_node_text(child)

    return "<anonymous>"


def calculate_file_metrics(file_info: FileInfo) -> FileMetrics:
    """
    Calculate metrics for a single file.

    Args:
        file_info: FileInfo object from scanner

    Returns:
        FileMetrics object with calculated metrics
    """
    metrics = FileMetrics(file_info.path)
    metrics.loc = file_info.loc
    metrics.language = file_info.language

    try:
        parser = get_parser_manager()
        ast = parser.parse_file(file_info.path, file_info.language)

        if not ast or not ast.root_node:
            return metrics

        # Count imports
        imports = ast.get_imports()
        metrics.imports_count = len(imports)

        # Analyze functions
        functions = ast.get_functions()

        for func_node in functions:
            name = extract_function_name(func_node, ast)
            start_line = func_node.start_point[0] + 1
            end_line = func_node.end_point[0] + 1

            func_metrics = FunctionMetrics(name, start_line, end_line)
            func_metrics.file_path = file_info.path
            func_metrics.complexity = calculate_cyclomatic_complexity(func_node, ast)
            func_metrics.parameters = count_parameters(func_node, ast)
            func_metrics.nesting_depth = calculate_nesting_depth(func_node)

            metrics.functions.append(func_metrics)

    except Exception as e:
        print(f"Error calculating metrics for {file_info.path}: {e}")

    return metrics


def calculate_metrics(file_infos: List[FileInfo]) -> List[FileMetrics]:
    """
    Calculate metrics for multiple files.

    Args:
        file_infos: List of FileInfo objects

    Returns:
        List of FileMetrics objects
    """
    results = []

    for file_info in file_infos:
        metrics = calculate_file_metrics(file_info)
        results.append(metrics)

    return results
