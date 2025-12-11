# Using AI Code Inspector with LM Studio

This guide shows how to use AI Code Inspector with LM Studio, a free local LLM runtime.

## Why LM Studio?

- ✅ **Free** - No API costs
- ✅ **Private** - Your code stays on your machine
- ✅ **Offline** - Works without internet
- ✅ **Fast** - Local inference
- ✅ **Easy** - Simple UI to manage models

## Setup

### 1. Install LM Studio

Download from: https://lmstudio.ai/

### 2. Download a Model

Recommended models for code analysis:

- **CodeLlama 13B Instruct** - Best for code understanding
- **Mistral 7B Instruct** - Good balance of speed/quality
- **DeepSeek Coder 33B** - Excellent for code-specific tasks

In LM Studio:

1. Go to "Discover" tab
2. Search for model (e.g., "codellama")
3. Download the model you want

### 3. Start the Local Server

1. In LM Studio, go to "Local Server" tab
2. Select your downloaded model
3. Click "Start Server"
4. Note the endpoint (usually `http://localhost:1234/v1`)

## Usage

### Option 1: Using the Shell Script

```bash
cd examples
./use-lmstudio.sh path/to/your/code
```

### Option 2: Manual Configuration

```bash
export LLM_PROVIDER="lmstudio"
export LLM_BASE_URL="http://localhost:1234/v1"
export LLM_MODEL="local-model"
export LLM_API_KEY="not-needed"

ai-code-inspector analyze your-code --ai --output-html report.html
```

### Option 3: Docker with LM Studio

If LM Studio is running on your host machine:

```bash
# Use host.docker.internal to access host's localhost from container
podman run -v $(pwd):/code \
  -e LLM_PROVIDER="lmstudio" \
  -e LLM_BASE_URL="http://host.docker.internal:1234/v1" \
  -e LLM_MODEL="local-model" \
  -e LLM_API_KEY="not-needed" \
  ai-code-inspector analyze /code --ai --output-html report.html
```

On Linux, use `--network=host` instead:

```bash
podman run --network=host -v $(pwd):/code \
  -e LLM_PROVIDER="lmstudio" \
  -e LLM_BASE_URL="http://localhost:1234/v1" \
  -e LLM_MODEL="local-model" \
  -e LLM_API_KEY="not-needed" \
  ai-code-inspector analyze /code --ai --output-html report.html
```

## Performance Tips

1. **Use GPU acceleration** if available (configured in LM Studio settings)
2. **Adjust context length** based on your model's capacity
3. **Use smaller models** (7B) for faster analysis, larger models (13B+) for better quality
4. **Reduce max_tokens** if responses are too slow:
   ```bash
   export LLM_MAX_TOKENS="1000"
   ```

## Troubleshooting

### "Connection refused" error

- Make sure LM Studio server is running
- Check the port number (default: 1234)
- Verify `LLM_BASE_URL` matches LM Studio's endpoint

### Slow responses

- Use a smaller model (7B instead of 13B)
- Reduce `LLM_MAX_TOKENS`
- Enable GPU acceleration in LM Studio

### Out of memory

- Use a smaller model
- Reduce context length in LM Studio settings
- Close other applications

## Model Recommendations

| Model                  | Size  | Speed  | Quality   | Best For            |
| ---------------------- | ----- | ------ | --------- | ------------------- |
| Mistral 7B Instruct    | ~4GB  | Fast   | Good      | Quick analysis      |
| CodeLlama 13B Instruct | ~7GB  | Medium | Excellent | Code-specific tasks |
| DeepSeek Coder 33B     | ~20GB | Slow   | Best      | In-depth analysis   |
| Llama 2 13B Chat       | ~7GB  | Medium | Good      | General purpose     |

Choose based on your available RAM and desired speed/quality trade-off.
