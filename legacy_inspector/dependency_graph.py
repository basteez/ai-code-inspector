"""Dependency graph generation."""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional

import networkx as nx

from legacy_inspector.metrics import FileMetrics
from legacy_inspector.parser_manager import get_parser_manager


class DependencyGraph:
    """Represents the dependency graph of a project."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.modules: Set[str] = set()

    def add_dependency(self, source: str, target: str):
        """Add a dependency edge from source to target."""
        self.graph.add_edge(source, target)
        self.modules.add(source)
        self.modules.add(target)

    def get_dependencies(self, module: str) -> List[str]:
        """Get all modules that the given module depends on."""
        if module not in self.graph:
            return []
        return list(self.graph.successors(module))

    def get_dependents(self, module: str) -> List[str]:
        """Get all modules that depend on the given module."""
        if module not in self.graph:
            return []
        return list(self.graph.predecessors(module))

    def get_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except Exception:
            return []

    def export_dot(self, output_path: Path):
        """Export graph to DOT format."""
        try:
            from networkx.drawing.nx_pydot import write_dot

            write_dot(self.graph, str(output_path))
        except Exception as e:
            print(f"Error exporting DOT: {e}")

    def export_png(self, output_path: Path):
        """Export graph to PNG format (requires graphviz)."""
        try:
            import pygraphviz as pgv

            agraph = pgv.AGraph(directed=True)

            for node in self.graph.nodes():
                agraph.add_node(node)

            for source, target in self.graph.edges():
                agraph.add_edge(source, target)

            agraph.layout(prog="dot")
            agraph.draw(str(output_path))
        except Exception as e:
            print(f"Error exporting PNG: {e}. Make sure graphviz is installed.")

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "nodes": list(self.modules),
            "edges": [{"source": s, "target": t} for s, t in self.graph.edges()],
            "circular_dependencies": self.get_circular_dependencies(),
        }


def extract_python_imports(ast_wrapper) -> List[str]:
    """Extract imported modules from Python AST."""
    imports = []

    import_nodes = ast_wrapper.get_imports()

    for node in import_nodes:
        text = ast_wrapper.get_node_text(node)

        # Parse import statements
        # import foo, import foo.bar
        if text.startswith("import "):
            parts = text.replace("import ", "").split(",")
            for part in parts:
                module = part.strip().split()[0]  # Handle 'import foo as bar'
                imports.append(module)

        # from foo import bar
        elif text.startswith("from "):
            match = re.match(r"from\s+([\w.]+)\s+import", text)
            if match:
                imports.append(match.group(1))

    return imports


def extract_javascript_imports(ast_wrapper) -> List[str]:
    """Extract imported modules from JavaScript/TypeScript AST."""
    imports = []

    import_nodes = ast_wrapper.get_imports()

    for node in import_nodes:
        text = ast_wrapper.get_node_text(node)

        # import ... from 'module'
        match = re.search(r"from\s+['\"]([^'\"]+)['\"]", text)
        if match:
            imports.append(match.group(1))

        # require('module')
        match = re.search(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", text)
        if match:
            imports.append(match.group(1))

    return imports


def extract_java_imports(ast_wrapper) -> List[str]:
    """Extract imported modules from Java AST."""
    imports = []

    import_nodes = ast_wrapper.get_imports()

    for node in import_nodes:
        text = ast_wrapper.get_node_text(node)

        # import package.Class;
        match = re.match(r"import\s+([\w.]+);", text)
        if match:
            imports.append(match.group(1))

    return imports


def build_dependency_graph(file_metrics_list: List[FileMetrics]) -> DependencyGraph:
    """
    Build dependency graph from analyzed files.

    Args:
        file_metrics_list: List of FileMetrics objects

    Returns:
        DependencyGraph object
    """
    graph = DependencyGraph()
    parser = get_parser_manager()

    for file_metrics in file_metrics_list:
        try:
            # Parse file to get imports
            ast = parser.parse_file(file_metrics.filepath, file_metrics.language)

            if not ast:
                continue

            # Get module name (relative path or filename)
            module_name = file_metrics.filepath.stem

            # Extract imports based on language
            imports = []
            if file_metrics.language == "python":
                imports = extract_python_imports(ast)
            elif file_metrics.language in ["javascript", "typescript"]:
                imports = extract_javascript_imports(ast)
            elif file_metrics.language == "java":
                imports = extract_java_imports(ast)

            # Add dependencies to graph
            for imported in imports:
                # Normalize import paths
                # Skip standard library imports (basic heuristic)
                if not imported.startswith((".", "/")):
                    # Could be standard library or external package
                    # For now, include everything
                    pass

                graph.add_dependency(module_name, imported)

        except Exception as e:
            print(f"Error building dependency graph for {file_metrics.filepath}: {e}")

    return graph


def generate_dependency_report(graph: DependencyGraph) -> dict:
    """Generate a summary report of the dependency graph."""
    report = {
        "total_modules": len(graph.modules),
        "total_dependencies": graph.graph.number_of_edges(),
        "circular_dependencies": graph.get_circular_dependencies(),
    }

    # Find most connected modules
    in_degrees = dict(graph.graph.in_degree())
    out_degrees = dict(graph.graph.out_degree())

    # Most depended upon
    if in_degrees:
        most_depended = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        report["most_depended_upon"] = [
            {"module": m, "dependents": c} for m, c in most_depended if c > 0
        ]

    # Most dependencies
    if out_degrees:
        most_depending = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        report["most_dependencies"] = [
            {"module": m, "dependencies": c} for m, c in most_depending if c > 0
        ]

    return report
