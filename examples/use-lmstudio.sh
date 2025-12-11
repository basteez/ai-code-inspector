#!/bin/bash

# Example script for using AI Code Inspector with LM Studio
# 
# Prerequisites:
# 1. Install and start LM Studio (https://lmstudio.ai/)
# 2. Load a model in LM Studio (recommended: codellama-13b-instruct or mistral-7b-instruct)
# 3. Enable the local server in LM Studio (usually runs on http://localhost:1234)

# Configure for LM Studio
export LLM_PROVIDER="lmstudio"
export LLM_BASE_URL="http://localhost:1234/v1"
export LLM_MODEL="local-model"  # LM Studio uses whatever model you loaded
export LLM_API_KEY="not-needed"  # Not required for local models
export LLM_MAX_TOKENS="2000"
export LLM_TEMPERATURE="0.3"

# Run analysis
echo "🚀 Running AI Code Inspector with LM Studio..."
echo "📍 LM Studio endpoint: $LLM_BASE_URL"
echo "🤖 Provider: $LLM_PROVIDER"
echo ""

ai-code-inspector analyze "$1" \
    --ai \
    --clean-code \
    --output-html "report-lmstudio.html" \
    --output-json "report-lmstudio.json"

echo ""
echo "✅ Analysis complete!"
echo "📄 HTML Report: report-lmstudio.html"
echo "📊 JSON Report: report-lmstudio.json"
