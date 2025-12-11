"""Parser manager using tree-sitter for multi-language support."""

from pathlib import Path
from typing import Any, Optional

try:
    from tree_sitter import Language, Parser, Tree
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    import tree_sitter_java as tsjava

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


class ASTWrapper:
    """Wrapper for parsed AST with common interface."""

    def __init__(self, tree: Any, language: str, source_code: str):
        self.tree = tree
        self.language = language
        self.source_code = source_code.encode("utf-8")
        self.root_node = tree.root_node if hasattr(tree, "root_node") else None

    def get_root(self):
        """Get root node of AST."""
        return self.root_node

    def get_functions(self) -> list:
        """Extract function definitions from AST."""
        if not self.root_node:
            return []

        functions = []

        def traverse(node):
            # Language-specific function node types
            function_types = {
                "python": ["function_definition"],
                "javascript": ["function_declaration", "function_expression", "arrow_function"],
                "typescript": ["function_declaration", "function_expression", "arrow_function"],
                "java": ["method_declaration"],
            }

            if node.type in function_types.get(self.language, []):
                functions.append(node)

            for child in node.children:
                traverse(child)

        traverse(self.root_node)
        return functions

    def get_imports(self) -> list:
        """Extract import statements from AST."""
        if not self.root_node:
            return []

        imports = []

        def traverse(node):
            import_types = {
                "python": ["import_statement", "import_from_statement"],
                "javascript": ["import_statement"],
                "typescript": ["import_statement"],
                "java": ["import_declaration"],
            }

            if node.type in import_types.get(self.language, []):
                imports.append(node)

            for child in node.children:
                traverse(child)

        traverse(self.root_node)
        return imports

    def get_node_text(self, node) -> str:
        """Get text content of a node."""
        if not node:
            return ""
        return self.source_code[node.start_byte : node.end_byte].decode("utf-8")


class ParserManager:
    """Manages tree-sitter parsers for different languages."""

    def __init__(self):
        if not TREE_SITTER_AVAILABLE:
            raise RuntimeError("tree-sitter is not available. Install required packages.")

        self.parsers = {}
        self._init_parsers()

    def _init_parsers(self):
        """Initialize parsers for supported languages."""
        # Python
        python_parser = Parser(Language(tspython.language()))
        self.parsers["python"] = python_parser

        # JavaScript/TypeScript
        js_parser = Parser(Language(tsjavascript.language()))
        self.parsers["javascript"] = js_parser
        self.parsers["typescript"] = js_parser

        # Java
        java_parser = Parser(Language(tsjava.language()))
        self.parsers["java"] = java_parser

    def parse_file(self, filepath: Path, language: str) -> Optional[ASTWrapper]:
        """
        Parse a source file and return AST wrapper.

        Args:
            filepath: Path to source file
            language: Programming language

        Returns:
            ASTWrapper or None if parsing fails
        """
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                source_code = f.read()

            return self.parse_code(source_code, language)

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

    def parse_code(self, source_code: str, language: str) -> Optional[ASTWrapper]:
        """
        Parse source code string and return AST wrapper.

        Args:
            source_code: Source code as string
            language: Programming language

        Returns:
            ASTWrapper or None if parsing fails
        """
        parser = self.parsers.get(language.lower())
        if not parser:
            print(f"No parser available for language: {language}")
            return None

        try:
            tree = parser.parse(source_code.encode("utf-8"))
            return ASTWrapper(tree, language, source_code)
        except Exception as e:
            print(f"Error parsing code: {e}")
            return None


# Singleton instance
_parser_manager: Optional[ParserManager] = None


def get_parser_manager() -> ParserManager:
    """Get or create parser manager singleton."""
    global _parser_manager
    if _parser_manager is None:
        _parser_manager = ParserManager()
    return _parser_manager
