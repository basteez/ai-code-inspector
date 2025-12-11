"""AI Code Inspector - Multi-language code analyzer."""

__version__ = "0.1.0"
__author__ = "AI Code Inspector Team"

from legacy_inspector.scanner import scan_directory
from legacy_inspector.metrics import calculate_metrics
from legacy_inspector.smells import detect_smells
from legacy_inspector.dependency_graph import build_dependency_graph
from legacy_inspector.reporter import generate_report

__all__ = [
    "scan_directory",
    "calculate_metrics",
    "detect_smells",
    "build_dependency_graph",
    "generate_report",
]
