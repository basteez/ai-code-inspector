"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a temporary Python file for testing."""
    code = """
def test_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
    return 0

def simple_function(x):
    return x * 2
"""
    file_path = tmp_path / "sample.py"
    file_path.write_text(code)
    return file_path


@pytest.fixture
def sample_js_file(tmp_path):
    """Create a temporary JavaScript file for testing."""
    code = """
function complexFunction(a, b, c) {
    if (a > 0) {
        if (b > 0) {
            if (c > 0) {
                return a + b + c;
            }
        }
    }
    return 0;
}
"""
    file_path = tmp_path / "sample.js"
    file_path.write_text(code)
    return file_path


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample project structure for testing."""
    # Create Python files
    py_dir = tmp_path / "src"
    py_dir.mkdir()
    
    (py_dir / "main.py").write_text("""
def main():
    print("Hello")
    
import os
import sys
""")
    
    (py_dir / "utils.py").write_text("""
def helper(x):
    return x + 1
""")
    
    # Create JavaScript file
    js_dir = tmp_path / "frontend"
    js_dir.mkdir()
    
    (js_dir / "app.js").write_text("""
function app() {
    console.log("App");
}
""")
    
    return tmp_path
