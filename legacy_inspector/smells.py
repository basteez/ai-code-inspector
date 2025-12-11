"""Code smell detection."""

import hashlib
from pathlib import Path
from typing import List, Dict, Set

from legacy_inspector.config import get_threshold
from legacy_inspector.metrics import FileMetrics, FunctionMetrics
from legacy_inspector.parser_manager import get_parser_manager


class CodeSmell:
    """Represents a detected code smell."""

    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_SEVERE = "severe"

    def __init__(
        self,
        smell_type: str,
        severity: str,
        message: str,
        file_path: Path,
        line: int = 0,
        function_name: str = "",
    ):
        self.smell_type = smell_type
        self.severity = severity
        self.message = message
        self.file_path = file_path
        self.line = line
        self.function_name = function_name

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "type": self.smell_type,
            "severity": self.severity,
            "message": self.message,
            "file": str(self.file_path),
            "line": self.line,
            "function": self.function_name,
        }

    def __repr__(self):
        return f"<CodeSmell {self.smell_type} ({self.severity}) at {self.file_path}:{self.line}>"


def detect_long_function(func: FunctionMetrics) -> List[CodeSmell]:
    """Detect functions that are too long."""
    smells = []
    warning_threshold = get_threshold("function_loc_warning", 30)
    severe_threshold = get_threshold("function_loc_severe", 200)

    if func.loc > severe_threshold:
        smells.append(
            CodeSmell(
                smell_type="long_function",
                severity=CodeSmell.SEVERITY_SEVERE,
                message=f"Function '{func.name}' is very long ({func.loc} LOC, threshold: {severe_threshold})",
                file_path=func.file_path,
                line=func.start_line,
                function_name=func.name,
            )
        )
    elif func.loc > warning_threshold:
        smells.append(
            CodeSmell(
                smell_type="long_function",
                severity=CodeSmell.SEVERITY_WARNING,
                message=f"Function '{func.name}' is long ({func.loc} LOC, threshold: {warning_threshold})",
                file_path=func.file_path,
                line=func.start_line,
                function_name=func.name,
            )
        )

    return smells


def detect_high_complexity(func: FunctionMetrics) -> List[CodeSmell]:
    """Detect functions with high cyclomatic complexity."""
    smells = []
    threshold = get_threshold("complexity_warning", 10)

    if func.complexity > threshold:
        smells.append(
            CodeSmell(
                smell_type="high_complexity",
                severity=CodeSmell.SEVERITY_WARNING,
                message=f"Function '{func.name}' has high complexity ({func.complexity}, threshold: {threshold})",
                file_path=func.file_path,
                line=func.start_line,
                function_name=func.name,
            )
        )

    return smells


def detect_too_many_parameters(func: FunctionMetrics) -> List[CodeSmell]:
    """Detect functions with too many parameters."""
    smells = []
    threshold = get_threshold("max_parameters", 7)

    if func.parameters > threshold:
        smells.append(
            CodeSmell(
                smell_type="too_many_parameters",
                severity=CodeSmell.SEVERITY_WARNING,
                message=f"Function '{func.name}' has too many parameters ({func.parameters}, threshold: {threshold})",
                file_path=func.file_path,
                line=func.start_line,
                function_name=func.name,
            )
        )

    return smells


def detect_deep_nesting(func: FunctionMetrics) -> List[CodeSmell]:
    """Detect functions with deep nesting."""
    smells = []
    threshold = get_threshold("max_nesting_depth", 5)

    if func.nesting_depth > threshold:
        smells.append(
            CodeSmell(
                smell_type="deep_nesting",
                severity=CodeSmell.SEVERITY_WARNING,
                message=f"Function '{func.name}' has deep nesting ({func.nesting_depth}, threshold: {threshold})",
                file_path=func.file_path,
                line=func.start_line,
                function_name=func.name,
            )
        )

    return smells


def detect_large_file(file_metrics: FileMetrics) -> List[CodeSmell]:
    """Detect files that are too large."""
    smells = []
    threshold = get_threshold("file_loc_warning", 1000)

    if file_metrics.loc > threshold:
        smells.append(
            CodeSmell(
                smell_type="large_file",
                severity=CodeSmell.SEVERITY_WARNING,
                message=f"File is very large ({file_metrics.loc} LOC, threshold: {threshold})",
                file_path=file_metrics.filepath,
            )
        )

    return smells


def detect_unused_variables(file_metrics: FileMetrics) -> List[CodeSmell]:
    """
    Detect potentially unused variables (simple heuristic).
    This is a basic implementation - a full implementation would require
    data flow analysis.
    """
    # Placeholder for future implementation
    # Would require analyzing variable declarations and usage
    return []


def detect_unused_imports(file_metrics: FileMetrics) -> List[CodeSmell]:
    """
    Detect potentially unused imports (simple heuristic).
    This is a basic implementation.
    """
    # Placeholder for future implementation
    # Would require parsing imports and checking if they're referenced
    return []


def detect_code_duplication(all_file_metrics: List[FileMetrics]) -> List[CodeSmell]:
    """
    Detect code duplication using hash-based approach.
    Simple implementation that looks for duplicate function bodies.
    """
    smells = []
    function_hashes: Dict[str, List[FunctionMetrics]] = {}

    # Hash all functions
    for file_metrics in all_file_metrics:
        try:
            parser = get_parser_manager()
            ast = parser.parse_file(file_metrics.filepath, file_metrics.language)

            if not ast:
                continue

            for func in file_metrics.functions:
                # Get function source
                func_node = None
                for f in ast.get_functions():
                    if f.start_point[0] + 1 == func.start_line:
                        func_node = f
                        break

                if func_node:
                    func_text = ast.get_node_text(func_node)
                    # Normalize whitespace for comparison
                    normalized = " ".join(func_text.split())
                    func_hash = hashlib.md5(normalized.encode()).hexdigest()

                    if func_hash not in function_hashes:
                        function_hashes[func_hash] = []
                    function_hashes[func_hash].append(func)

        except Exception as e:
            print(f"Error detecting duplication in {file_metrics.filepath}: {e}")

    # Find duplicates
    for func_hash, funcs in function_hashes.items():
        if len(funcs) > 1:
            # Report duplication
            locations = ", ".join([f"{f.file_path}:{f.start_line}" for f in funcs])
            for func in funcs:
                smells.append(
                    CodeSmell(
                        smell_type="code_duplication",
                        severity=CodeSmell.SEVERITY_INFO,
                        message=f"Function '{func.name}' appears duplicated. Also found at: {locations}",
                        file_path=func.file_path,
                        line=func.start_line,
                        function_name=func.name,
                    )
                )

    return smells


def detect_smells(file_metrics_list: List[FileMetrics]) -> List[CodeSmell]:
    """
    Detect all code smells in the analyzed files.

    Args:
        file_metrics_list: List of FileMetrics objects

    Returns:
        List of detected CodeSmell objects
    """
    all_smells = []

    # File-level smells
    for file_metrics in file_metrics_list:
        all_smells.extend(detect_large_file(file_metrics))
        all_smells.extend(detect_unused_variables(file_metrics))
        all_smells.extend(detect_unused_imports(file_metrics))

        # Function-level smells
        for func in file_metrics.functions:
            all_smells.extend(detect_long_function(func))
            all_smells.extend(detect_high_complexity(func))
            all_smells.extend(detect_too_many_parameters(func))
            all_smells.extend(detect_deep_nesting(func))

    # Cross-file smells
    all_smells.extend(detect_code_duplication(file_metrics_list))

    return all_smells
