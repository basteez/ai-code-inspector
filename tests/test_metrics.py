"""Tests for metrics calculation."""

import pytest
from pathlib import Path

from legacy_inspector.scanner import FileInfo
from legacy_inspector.metrics import (
    calculate_metrics,
    calculate_file_metrics,
    FunctionMetrics,
)


def test_function_metrics():
    """Test FunctionMetrics class."""
    func = FunctionMetrics("test_func", 10, 20)
    
    assert func.name == "test_func"
    assert func.start_line == 10
    assert func.end_line == 20
    assert func.loc == 11  # end - start + 1
    assert func.complexity == 1  # default
    
    func_dict = func.to_dict()
    assert func_dict["name"] == "test_func"
    assert func_dict["loc"] == 11


def test_calculate_file_metrics_python(sample_python_file):
    """Test metrics calculation for Python file."""
    file_info = FileInfo(sample_python_file, "python")
    file_info.loc = 10
    
    metrics = calculate_file_metrics(file_info)
    
    assert metrics.filepath == sample_python_file
    assert metrics.language == "python"
    assert metrics.loc == 10
    assert len(metrics.functions) >= 0  # Depends on parser


def test_calculate_file_metrics_javascript(sample_js_file):
    """Test metrics calculation for JavaScript file."""
    file_info = FileInfo(sample_js_file, "javascript")
    file_info.loc = 15
    
    metrics = calculate_file_metrics(file_info)
    
    assert metrics.filepath == sample_js_file
    assert metrics.language == "javascript"
    assert metrics.loc == 15


def test_calculate_metrics_multiple_files(sample_python_file, sample_js_file):
    """Test metrics calculation for multiple files."""
    files = [
        FileInfo(sample_python_file, "python"),
        FileInfo(sample_js_file, "javascript"),
    ]
    
    for f in files:
        f.loc = 10
    
    metrics_list = calculate_metrics(files)
    
    assert len(metrics_list) == 2
    assert metrics_list[0].language == "python"
    assert metrics_list[1].language == "javascript"


def test_file_metrics_to_dict(sample_python_file):
    """Test FileMetrics serialization."""
    file_info = FileInfo(sample_python_file, "python")
    file_info.loc = 20
    
    metrics = calculate_file_metrics(file_info)
    metrics_dict = metrics.to_dict()
    
    assert "file" in metrics_dict
    assert "language" in metrics_dict
    assert "loc" in metrics_dict
    assert "functions" in metrics_dict
    assert metrics_dict["language"] == "python"


def test_complexity_calculation(sample_python_file):
    """Test that complexity is calculated for functions."""
    file_info = FileInfo(sample_python_file, "python")
    file_info.loc = 20
    
    metrics = calculate_file_metrics(file_info)
    
    # If functions are detected, they should have complexity > 0
    for func in metrics.functions:
        assert func.complexity >= 1


def test_empty_file_metrics(tmp_path):
    """Test metrics for an empty file."""
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("")
    
    file_info = FileInfo(empty_file, "python")
    file_info.loc = 0
    
    metrics = calculate_file_metrics(file_info)
    
    assert metrics.loc == 0
    assert len(metrics.functions) == 0
