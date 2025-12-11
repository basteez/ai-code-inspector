"""Tests for scanner module."""

import pytest
from pathlib import Path

from legacy_inspector.scanner import (
    scan_directory,
    detect_language,
    count_lines,
    FileInfo,
)


def test_detect_language():
    """Test language detection from file extensions."""
    assert detect_language(Path("test.py")) == "python"
    assert detect_language(Path("test.js")) == "javascript"
    assert detect_language(Path("test.jsx")) == "javascript"
    assert detect_language(Path("test.ts")) == "typescript"
    assert detect_language(Path("test.tsx")) == "typescript"
    assert detect_language(Path("test.java")) == "java"
    assert detect_language(Path("test.txt")) is None


def test_count_lines(sample_python_file):
    """Test line counting."""
    loc = count_lines(sample_python_file)
    assert loc > 0


def test_scan_directory_empty(tmp_path):
    """Test scanning an empty directory."""
    result = scan_directory(tmp_path)
    assert len(result.files) == 0
    assert result.total_loc == 0


def test_scan_directory_with_files(sample_project):
    """Test scanning a directory with multiple files."""
    result = scan_directory(sample_project)
    
    assert len(result.files) > 0
    assert result.total_loc > 0
    
    # Check languages are detected
    assert "python" in result.languages
    assert "javascript" in result.languages


def test_scan_directory_ignores_common_dirs(tmp_path):
    """Test that common directories are ignored."""
    # Create ignored directories
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "test.js").write_text("console.log('test');")
    
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git config")
    
    # Create valid file
    (tmp_path / "app.py").write_text("print('hello')")
    
    result = scan_directory(tmp_path)
    
    # Should only find app.py
    assert len(result.files) == 1
    assert result.files[0].path.name == "app.py"


def test_scan_nonexistent_directory():
    """Test scanning a non-existent directory."""
    result = scan_directory("/nonexistent/path/xyz")
    assert len(result.errors) > 0
    assert len(result.files) == 0


def test_file_info():
    """Test FileInfo class."""
    path = Path("test.py")
    file_info = FileInfo(path, "python")
    
    assert file_info.path == path
    assert file_info.language == "python"
    assert file_info.loc == 0
    assert file_info.size_bytes == 0
