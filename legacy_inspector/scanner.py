"""File system scanner for multi-language projects."""

import os
from pathlib import Path
from typing import Dict, List

from legacy_inspector.config import (
    IGNORE_DIRS,
    get_all_extensions,
    should_ignore_dir,
)


class FileInfo:
    """Information about a scanned file."""

    def __init__(self, path: Path, language: str):
        self.path = path
        self.language = language
        self.loc = 0
        self.size_bytes = 0

    def __repr__(self):
        return f"<FileInfo {self.path} ({self.language}, {self.loc} LOC)>"


class ScanResult:
    """Result of directory scan."""

    def __init__(self):
        self.files: List[FileInfo] = []
        self.total_loc = 0
        self.languages: Dict[str, int] = {}
        self.errors: List[str] = []

    def add_file(self, file_info: FileInfo):
        """Add a file to scan results."""
        self.files.append(file_info)
        self.total_loc += file_info.loc
        self.languages[file_info.language] = self.languages.get(file_info.language, 0) + 1

    def get_summary(self) -> dict:
        """Get summary statistics."""
        return {
            "total_files": len(self.files),
            "total_loc": self.total_loc,
            "languages": self.languages,
            "errors": len(self.errors),
        }


def detect_language(filepath: Path) -> str | None:
    """Detect language from file extension."""
    ext = filepath.suffix.lower()
    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
    }
    return lang_map.get(ext)


def count_lines(filepath: Path) -> int:
    """Count lines of code (simple implementation)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            # Count non-empty, non-comment lines (basic implementation)
            code_lines = 0
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith(("#", "//", "/*", "*")):
                    code_lines += 1
            return code_lines
    except Exception:
        return 0


def scan_directory(root_path: str | Path) -> ScanResult:
    """
    Recursively scan directory for supported source files.

    Args:
        root_path: Root directory to scan

    Returns:
        ScanResult object with scanned files and statistics
    """
    root = Path(root_path).resolve()
    result = ScanResult()

    if not root.exists():
        result.errors.append(f"Path does not exist: {root}")
        return result

    if not root.is_dir():
        result.errors.append(f"Path is not a directory: {root}")
        return result

    supported_extensions = set(get_all_extensions())

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d)]

        current_dir = Path(dirpath)

        for filename in filenames:
            filepath = current_dir / filename

            # Check if file has supported extension
            if filepath.suffix.lower() not in supported_extensions:
                continue

            language = detect_language(filepath)
            if not language:
                continue

            # Create file info
            file_info = FileInfo(filepath, language)

            try:
                file_info.size_bytes = filepath.stat().st_size
                file_info.loc = count_lines(filepath)
                result.add_file(file_info)
            except Exception as e:
                result.errors.append(f"Error scanning {filepath}: {e}")

    return result


def get_file_content(filepath: Path) -> str:
    """Read file content safely."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Cannot read file {filepath}: {e}")
