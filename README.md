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
git clone https://github.com/basteez/ai-code-inspector
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

- `LLM_API_KEY`: Your AI provider API key (optional for local models)
- `LLM_PROVIDER`: `openai`, `lmstudio`, or `anthropic` (default: `openai`)
- `LLM_BASE_URL`: Base URL for custom endpoints (for LM Studio or other OpenAI-compatible APIs)
- `LLM_MODEL`: Model name (default: `gpt-4`)
- `LLM_MAX_TOKENS`: Maximum tokens in response (default: `2000`)
- `LLM_TEMPERATURE`: Temperature for generation (default: `0.3`)

### Using LM Studio (Local LLM)

LM Studio provides a local OpenAI-compatible API server. To use it:

1. **Start LM Studio** and load your preferred model
2. **Enable the local server** (default: `http://localhost:1234/v1`)
3. **Configure environment variables:**

```bash
export LLM_PROVIDER="lmstudio"
export LLM_BASE_URL="http://localhost:1234/v1"
export LLM_MODEL="your-model-name"  # e.g., "mistral-7b-instruct"
# API key not required for LM Studio
export LLM_API_KEY="not-needed"

ai-code-inspector analyze path/to/code --ai --output-html report.html
```

**Benefits of using LM Studio:**

- ✅ Free and runs locally
- ✅ No API costs
- ✅ Privacy - your code stays on your machine
- ✅ Works offline
- ✅ Supports many open-source models (Mistral, Llama, CodeLlama, etc.)

**Recommended models for code analysis:**

- `codellama-13b-instruct` - Best for code understanding
- `mistral-7b-instruct` - Good balance of speed and quality
- `deepseek-coder-33b` - Excellent for code-specific tasks
- `llama-2-13b-chat` - General purpose

### Using OpenAI

```bash
export LLM_API_KEY="sk-..."
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4"  # or gpt-3.5-turbo

ai-code-inspector analyze path/to/code --ai --output-html report.html
```

### Using Anthropic (Claude)

```bash
export LLM_API_KEY="sk-ant-..."
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-3-opus-20240229"

ai-code-inspector analyze path/to/code --ai --output-html report.html
```

### AI-Powered Detailed Analysis

With the `--ai` flag, the tool generates comprehensive, granular insights:

```bash
export LLM_API_KEY="your-api-key"
ai-code-inspector analyze path/to/code --ai --output-html report.html
```

**AI Analysis includes:**

1. **Executive Summary**: Overall code quality assessment with main concerns and next steps
2. **Prioritized Issues**: Issues ranked by impact and effort with specific guidance
3. **Detailed Recommendations**: For each code smell, you get:
   - Root cause explanation (1 sentence)
   - Specific fix with code examples (2-3 sentences)
   - Expected benefits
4. **Problematic Files**: Top files with most issues, with LOC and function count
5. **File-level Analysis**: Granular insights for each problematic module

### Clean Code Review (Advanced)

For a comprehensive analysis based on Robert C. Martin's "Clean Code" principles:

```bash
export LLM_API_KEY="your-api-key"
ai-code-inspector analyze path/to/code --ai --clean-code --output-html report.html
```

**Clean Code Review analyzes:**

- **Meaningful Names**: Intention-revealing names, avoiding mental mapping, proper conventions
- **Functions**: Size, single responsibility, abstraction levels, argument count
- **Comments**: Good vs bad comments, when code should replace comments
- **Formatting**: Vertical and horizontal formatting, file organization
- **Objects & Data Structures**: Law of Demeter, proper abstraction, avoiding hybrids
- **Error Handling**: Exceptions vs return codes, proper context
- **SOLID Principles**: Single Responsibility, Open/Closed, Dependency Inversion
- **Code Smells**: Dead code, duplication, feature envy, inappropriate intimacy

**Clean Code Output includes:**

- Clean Code Score (0-10)
- Detailed violation reports with before/after examples
- Impact assessment (readability, maintainability, testability)
- Prioritized improvement list
- Reading recommendations from Clean Code book

**Example Output:**

```
🤖 Generating detailed AI insights...
✓ AI Summary:
The codebase has 8 quality issues across 3 files. Main concerns are long
functions, high complexity, and deep nesting in complex_legacy.py.

📝 Top AI Recommendations:

1. long_function (warning) - examples/complex_legacy.py
   Function: process_data
   Root Cause: Function exceeds 30 lines.
   Specific Fix: Break down into smaller functions (clean_data, transform_data,
   analyze_data) following single responsibility principle...
   Expected Benefit: Improved maintainability, testability, and readability.

⚠️  Most Problematic Files:
   • complex_legacy.py: 7 issues (124 LOC)

🧹 Performing Clean Code Review on most problematic files...
   Reviewing: complex_legacy.py...
   ✓ Clean Code Review completed
✓ Generated 1 Clean Code reviews
```

The HTML report includes both **AI Insights** and **Clean Code Reviews** sections with detailed, actionable recommendations.

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

Built with ❤️ by Tiziano Basile
