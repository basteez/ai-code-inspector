# AI Prompts System

## Overview

The AI Code Inspector uses sophisticated prompt templates stored in the `prompts/` directory to guide AI analysis. These prompts are loaded dynamically and passed to the LLM (OpenAI, Anthropic, or LM Studio).

## Prompt Files

All prompts are stored in `prompts/*.txt`:

| Prompt File             | Used By                                              | Purpose                                                     |
| ----------------------- | ---------------------------------------------------- | ----------------------------------------------------------- |
| `explain_module.txt`    | `explain_module()`                                   | Comprehensive file/module analysis with refactoring roadmap |
| `refactor_patch.txt`    | `suggest_refactor()` & `_generate_recommendations()` | Specific fix recommendations for code smells                |
| `prioritize.txt`        | `_prioritize_issues()`                               | ROI-driven prioritization of technical debt                 |
| `clean_code_review.txt` | `clean_code_review()`                                | Deep Clean Code principles analysis                         |

## How It Works

### 1. Prompt Loading

```python
# In ai_helper.py
def _load_prompt(self, prompt_name: str) -> str:
    prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"
    if not prompt_file.exists():
        return ""  # Falls back to hardcoded prompt
    return prompt_file.read_text(encoding="utf-8")
```

### 2. Usage in Analysis

```python
# Load the comprehensive prompt template
system_prompt = self._load_prompt("prioritize")

# Fallback if file not found (development safety)
if not system_prompt:
    system_prompt = "You are a senior software engineer..."

# Pass to LLM
response = self._call_llm(system_prompt, user_prompt)
```

### 3. LLM Request Structure

When you see this in LM Studio logs:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a technical lead responsible for prioritizing technical debt..."
    },
    {
      "role": "user",
      "content": "Codebase size: 272 files, 16808 LOC\n\nDetected Issues:..."
    }
  ]
}
```

The `system` message content comes from the prompt files!

## Customizing Prompts

### Editing Existing Prompts

1. Open the prompt file: `prompts/prioritize.txt`
2. Modify the instructions
3. Save the file
4. Run analysis - changes are picked up immediately (no rebuild needed for editable install)

### Adding New Prompts

1. Create new file: `prompts/my_new_prompt.txt`
2. Add method in `ai_helper.py`:
   ```python
   def my_new_analysis(self, code: str) -> str:
       system_prompt = self._load_prompt("my_new_prompt")
       if not system_prompt:
           system_prompt = "Fallback prompt..."
       # ... rest of implementation
   ```
3. Call it from CLI or wherever needed

## Packaging & Distribution

### Development (Editable Install)

```bash
pip install -e .
```

- Prompts are loaded from the source directory
- Changes to `.txt` files take effect immediately
- No rebuild needed

### Docker

The `Dockerfile` includes:

```dockerfile
COPY prompts/ ./prompts/
```

This ensures prompts are available in the container.

### Source Distribution

The `MANIFEST.in` includes:

```
recursive-include prompts *.txt
```

This ensures prompts are included when you run `python -m build` or create a wheel.

## Verification

### Check Prompts are Loading

Run the test script:

```bash
python tests/test_prompts_integration.py
```

This verifies:

- ✅ Prompts directory exists
- ✅ All expected `.txt` files are present
- ✅ AIHelper can load them
- ✅ Methods are using `_load_prompt()`

### Debug During Analysis

Temporarily add debug logging:

```python
def _load_prompt(self, prompt_name: str) -> str:
    prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"
    if not prompt_file.exists():
        print(f"⚠️ Prompt not found: {prompt_file}")
        return ""
    content = prompt_file.read_text(encoding="utf-8")
    print(f"✅ Loaded {prompt_name}: {len(content)} chars")
    return content
```

## Troubleshooting

### "Short prompt" appearing in LM Studio logs

**Symptom**: LM Studio shows the fallback prompt like "You are a senior software engineer..." instead of the detailed prompt.

**Cause**: Prompt file not loading (returns empty string)

**Solutions**:

1. Check file exists: `ls -la prompts/prioritize.txt`
2. Check PROMPTS_DIR: `python -c "from legacy_inspector.config import PROMPTS_DIR; print(PROMPTS_DIR)"`
3. Reinstall: `pip install -e . --force-reinstall`
4. For Docker: Rebuild image `podman build -t ai-code-inspector .`

### Prompts not updating after editing

**Development (pip install -e .)**:

- Changes should be immediate - no action needed
- If not working, restart the Python process

**Docker**:

- Must rebuild: `podman build -t ai-code-inspector .`
- Changes to local files won't affect running container

**Installed package (pip install .)**:

- Must reinstall: `pip install . --force-reinstall`

## Best Practices

1. **Always use \_load_prompt()** - Don't hardcode long prompts in Python
2. **Provide fallbacks** - Short fallback for when file not found
3. **Keep prompts versioned** - Check `.txt` files into git
4. **Test locally first** - Use LM Studio to iterate on prompts quickly
5. **Document prompt purpose** - Add comments in the `.txt` file header
6. **Use clear formatting** - Prompts use markdown, numbered lists, headers

## Example: Complete Flow

```
User runs: ai-code-inspector analyze code/ --ai

1. CLI calls: ai_helper.generate_detailed_analysis()
2. Which calls: _prioritize_issues(smells, summary)
3. Which calls: _load_prompt("prioritize")
4. Which reads: prompts/prioritize.txt (3,179 chars)
5. Constructs user_prompt with actual data
6. Calls: _call_llm(system_prompt, user_prompt)
7. LLM receives full detailed prompt from file
8. Returns structured analysis following prompt instructions
```

## Prompt Engineering Tips

When editing prompts:

- **Be specific**: "Provide 3-5 examples" not "provide examples"
- **Use structure**: Numbered lists, headers, clear sections
- **Request format**: Specify exact output format wanted
- **Give context**: Explain the domain, constraints, goals
- **Show examples**: Include before/after code samples in prompts
- **Set tone**: "You are a senior architect" vs "You are helpful"
- **Limit scope**: "Focus on top 5" to avoid token overruns
- **Test iteratively**: Use LM Studio locally to refine prompts quickly

The prompts in this project are already highly optimized based on these principles!
