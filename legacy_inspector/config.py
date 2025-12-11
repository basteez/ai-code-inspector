"""Configuration management for Legacy Inspector."""

import os
from pathlib import Path
from typing import Any

# Supported file extensions by language
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
}

# Directories to ignore during scanning
IGNORE_DIRS = {
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    ".egg-info",
    "target",  # Java/Maven
    ".gradle",  # Gradle
}

# File patterns to ignore
IGNORE_PATTERNS = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "*.so",
    "*.dll",
    "*.class",
}

# Code smell thresholds
THRESHOLDS = {
    "function_loc_warning": 30,
    "function_loc_severe": 200,
    "file_loc_warning": 1000,
    "complexity_warning": 10,
    "max_parameters": 7,
    "max_nesting_depth": 5,
}

# AI configuration
AI_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),
    "api_key": os.getenv("LLM_API_KEY", ""),
    "model": os.getenv("LLM_MODEL", "gpt-4"),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000")),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.3")),
    "base_url": os.getenv("LLM_BASE_URL", ""),  # For LM Studio or custom endpoints
}

# Prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_extensions_for_language(language: str) -> list[str]:
    """Get file extensions for a given language."""
    return LANGUAGE_EXTENSIONS.get(language.lower(), [])


def get_all_extensions() -> list[str]:
    """Get all supported file extensions."""
    extensions = []
    for exts in LANGUAGE_EXTENSIONS.values():
        extensions.extend(exts)
    return extensions


def should_ignore_dir(dirname: str) -> bool:
    """Check if directory should be ignored."""
    return dirname in IGNORE_DIRS or dirname.startswith(".")


def get_threshold(key: str, default: Any = None) -> Any:
    """Get a threshold value by key."""
    return THRESHOLDS.get(key, default)


def get_ai_config() -> dict[str, Any]:
    """Get AI configuration."""
    return AI_CONFIG.copy()
