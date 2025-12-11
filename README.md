# AI Code Inspector

**Codename:** `ai-code-inspector`

A comprehensive static code analyzer for legacy multi-language codebases. Supports Python, JavaScript/TypeScript, and Java with extensible architecture.

## Features

- 🔍 **Multi-language scanning**: Python, JavaScript, TypeScript, Java
- 📊 **Metrics calculation**: LOC, cyclomatic complexity, function length, nesting depth
- 🐛 **Code smell detection**: Long functions, large files, unused variables/imports, code duplication
- 🕸️ **Dependency graph**: Visual representation of module dependencies
- 📝 **Multiple report formats**: JSON and HTML outputs
- 🤖 **Optional AI integration**: Code explanations, refactoring suggestions, issue prioritization
- 🔌 **Extensible architecture**: Easy to add new languages and rules

## Installation

### From source

```bash
git clone <repository-url>
cd ai-code-inspector
pip install -r requirements.txt
pip install -e .
```

### Using Docker

```bash
# Build the image
docker build -t ai-code-inspector .

# Analyze a project (reports saved in the project directory)
docker run -v $(pwd)/my-project:/code ai-code-inspector analyze . --output-json report.json --output-html report.html

# The reports will be saved in $(pwd)/my-project/

# With AI integration
docker run -v $(pwd)/my-project:/code \
  -e LLM_API_KEY=your-api-key \
  -e LLM_PROVIDER=openai \
  ai-code-inspector analyze . --output-json report.json --ai

# Analyze the examples included in the project
docker run -v $(pwd)/examples:/code ai-code-inspector analyze . --output-html report.html
```

**Note**: The working directory inside the container is `/code`, which is your mounted project directory. All reports will be saved there by default.

## Quick Start

### Basic analysis

```bash
ai-code-inspector analyze ./my-project --output-json report.json
```

### Generate HTML report

```bash
ai-code-inspector analyze ./my-project --output-html report.html
```

### With AI suggestions (requires API key)

```bash
export LLM_API_KEY=your-api-key
export LLM_PROVIDER=openai  # or anthropic
ai-code-inspector analyze ./my-project --output-json report.json --ai
```

### Summarize existing report

```bash
ai-code-inspector summarize report.json
```

## Configuration

Set environment variables:

- `LLM_API_KEY`: Your AI provider API key (optional)
- `LLM_PROVIDER`: `openai` or `anthropic` (default: `openai`)

## Output

### JSON Report Structure

```json
{
  "summary": {
    "total_files": 42,
    "total_loc": 5432,
    "languages": {"python": 30, "javascript": 12}
  },
  "files": [...],
  "functions": [...],
  "smells": [...],
  "graph": "path/to/dependencies.dot"
}
```

### HTML Report

Interactive HTML report with:

- File overview table
- Code smells list with severity
- Dependency graph visualization
- AI suggestions (if enabled)

## Detected Code Smells

- **Long functions**: > 30 LOC (warning), > 200 LOC (severe)
- **High complexity**: Cyclomatic complexity > 10
- **Large files**: > 1000 LOC
- **Unused variables**: Simple static analysis
- **Unused imports**: Detect unreferenced imports
- **Code duplication**: Hash-based snippet detection

## Extending

### Add a new language

1. Add tree-sitter grammar to dependencies
2. Update `parser_manager.py` with new language handler
3. Implement metric extractors in `metrics.py`
4. Add smell rules in `smells.py`

### Add custom rules

Edit `smells.py` and add new detection functions following the existing pattern.

## Development

### Run tests

```bash
pytest
```

### Lint

```bash
ruff check .
```

## License

MIT

## Requirements

- Python 3.11+
- tree-sitter (with language bindings)
- graphviz (for dependency graphs)

---

Built with ❤️ by the AI Code Inspector Team
