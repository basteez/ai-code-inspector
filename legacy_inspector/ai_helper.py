"""AI-powered code analysis helper."""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from legacy_inspector.config import get_ai_config, PROMPTS_DIR


class AIHelper:
    """Helper for AI-powered code analysis and suggestions."""

    def __init__(self):
        self.config = get_ai_config()
        self.api_key = self.config.get("api_key", "")
        self.provider = self.config.get("provider", "openai")
        self.model = self.config.get("model", "gpt-4")
        self.max_tokens = self.config.get("max_tokens", 2000)
        self.temperature = self.config.get("temperature", 0.3)

        # Client will be initialized on first use
        self._client = None

    def _get_client(self):
        """Lazy initialization of AI client."""
        if self._client is not None:
            return self._client

        if not self.api_key:
            raise ValueError(
                "LLM_API_KEY environment variable is not set. "
                "AI features require an API key."
            )

        if self.provider == "openai":
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package is required. Install with: pip install openai")
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package is required. Install with: pip install anthropic"
                )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return self._client

    def _load_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from the prompts directory."""
        prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"

        if not prompt_file.exists():
            return ""

        return prompt_file.read_text(encoding="utf-8")

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM API.

        Args:
            system_prompt: System instructions
            user_prompt: User message

        Returns:
            LLM response text
        """
        client = self._get_client()

        try:
            if self.provider == "openai":
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                response = client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error: {str(e)}"

    def explain_module(
        self, code_summary: str, smells: List[Dict], snippet: str = ""
    ) -> Dict[str, Any]:
        """
        Explain a module and its issues.

        Args:
            code_summary: Summary of the code file
            smells: List of detected code smells
            snippet: Optional code snippet

        Returns:
            Dictionary with explanation and recommendations
        """
        system_prompt = self._load_prompt("explain_module")

        user_prompt = f"""
Code Summary:
{code_summary}

Detected Issues:
{', '.join([s.get('message', '') for s in smells[:5]])}

Code Snippet:
{snippet[:500] if snippet else 'N/A'}
"""

        response = self._call_llm(system_prompt, user_prompt)

        return {
            "explanation": response,
            "smells_count": len(smells),
        }

    def suggest_refactor(self, function_text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest refactoring for a function.

        Args:
            function_text: Source code of the function
            metrics: Metrics dictionary (LOC, complexity, etc.)

        Returns:
            Dictionary with refactoring suggestions
        """
        system_prompt = self._load_prompt("refactor_patch")

        user_prompt = f"""
Function Metrics:
- Lines of Code: {metrics.get('loc', 0)}
- Cyclomatic Complexity: {metrics.get('complexity', 0)}
- Parameters: {metrics.get('parameters', 0)}
- Nesting Depth: {metrics.get('nesting_depth', 0)}

Function Code:
```
{function_text[:1000]}
```
"""

        response = self._call_llm(system_prompt, user_prompt)

        return {
            "suggestion": response,
            "original_metrics": metrics,
        }

    def prioritize_issues(
        self, issues: List[Dict], project_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prioritize issues based on impact and effort.

        Args:
            issues: List of detected issues
            project_summary: Summary of the project

        Returns:
            Dictionary with prioritized issues and recommendations
        """
        system_prompt = self._load_prompt("prioritize")

        # Prepare issue summary
        issue_summary = "\n".join(
            [
                f"- {i.get('type', 'unknown')} ({i.get('severity', 'unknown')}): {i.get('message', '')}"
                for i in issues[:20]
            ]
        )

        user_prompt = f"""
Project Summary:
- Total Files: {project_summary.get('total_files', 0)}
- Total LOC: {project_summary.get('total_loc', 0)}
- Total Issues: {len(issues)}

Top Issues:
{issue_summary}
"""

        response = self._call_llm(system_prompt, user_prompt)

        return {
            "prioritization": response,
            "total_issues": len(issues),
        }

    def generate_summary(self, report_data: Dict[str, Any]) -> str:
        """
        Generate a high-level summary of the analysis.

        Args:
            report_data: Full report data

        Returns:
            Summary text
        """
        summary = report_data.get("summary", {})
        smells = report_data.get("smells", [])

        system_prompt = "You are a code quality expert. Provide a concise executive summary."

        user_prompt = f"""
Analyzed a codebase with:
- {summary.get('total_files', 0)} files
- {summary.get('total_loc', 0)} lines of code
- {summary.get('total_functions', 0)} functions
- {len(smells)} code quality issues detected

Top issues:
{', '.join(set([s.get('type', '') for s in smells[:10]]))}

Provide a 3-4 sentence executive summary highlighting the main findings and priority areas.
"""

        return self._call_llm(system_prompt, user_prompt)


def create_ai_helper() -> Optional[AIHelper]:
    """
    Create an AI helper instance if configured.

    Returns:
        AIHelper instance or None if not configured
    """
    try:
        api_key = os.getenv("LLM_API_KEY", "")
        if not api_key:
            return None

        return AIHelper()
    except Exception as e:
        print(f"Warning: Could not initialize AI helper: {e}")
        return None
