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
        self.base_url = self.config.get("base_url", "")

        # Client will be initialized on first use
        self._client = None

    def _get_client(self):
        """Lazy initialization of AI client."""
        if self._client is not None:
            return self._client

        # For LM Studio and other OpenAI-compatible endpoints, API key can be optional
        if self.provider == "openai" or self.provider == "lmstudio":
            try:
                from openai import OpenAI

                # LM Studio uses OpenAI-compatible API
                client_args = {}
                
                if self.base_url:
                    # Custom endpoint (LM Studio, LocalAI, etc.)
                    client_args["base_url"] = self.base_url
                    # For local models, API key might not be required
                    client_args["api_key"] = self.api_key if self.api_key else "lm-studio"
                else:
                    # Standard OpenAI
                    if not self.api_key:
                        raise ValueError(
                            "LLM_API_KEY environment variable is not set. "
                            "AI features require an API key for OpenAI."
                        )
                    client_args["api_key"] = self.api_key
                
                self._client = OpenAI(**client_args)
            except ImportError:
                raise ImportError("openai package is required. Install with: pip install openai")
                
        elif self.provider == "anthropic":
            if not self.api_key:
                raise ValueError(
                    "LLM_API_KEY environment variable is not set. "
                    "AI features require an API key for Anthropic."
                )
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package is required. Install with: pip install anthropic"
                )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'openai', 'lmstudio', or 'anthropic'")

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
            if self.provider in ["openai", "lmstudio"]:
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

    def clean_code_review(
        self, code_snippet: str, file_path: str, smells: List[Dict], metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive clean code review.

        Args:
            code_snippet: Source code to review
            file_path: Path to the file
            smells: Detected code smells
            metrics: Code metrics

        Returns:
            Dictionary with clean code analysis and recommendations
        """
        system_prompt = self._load_prompt("clean_code_review")

        # Format smells for context
        smells_summary = "\n".join([
            f"- {s.get('type', 'unknown')} ({s.get('severity', 'info')}): {s.get('message', '')} at line {s.get('line', '?')}"
            for s in smells[:10]
        ])

        user_prompt = f"""
File: {file_path}

Code Metrics:
- Lines of Code: {metrics.get('loc', 'N/A')}
- Functions: {metrics.get('functions_count', 'N/A')}
- Cyclomatic Complexity (avg): {metrics.get('avg_complexity', 'N/A')}
- Max Nesting Depth: {metrics.get('max_nesting', 'N/A')}

Detected Code Smells:
{smells_summary if smells_summary else 'None detected by static analysis'}

Code to Review:
```
{code_snippet[:2000]}
```

Perform a comprehensive clean code review following all the principles outlined in your instructions.
Focus on the most impactful improvements.
"""

        response = self._call_llm(system_prompt, user_prompt)

        return {
            "file": file_path,
            "review": response,
            "smells_count": len(smells),
        }

    def generate_detailed_analysis(self, report_data: Dict[str, Any], file_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate detailed AI analysis with specific recommendations for each problem.

        Args:
            report_data: Full report data
            file_metrics: List of file metrics with functions

        Returns:
            Dictionary with detailed analysis, priorities, and specific suggestions
        """
        summary = report_data.get("summary", {})
        smells = report_data.get("smells", [])

        # Analyze top problematic files
        file_issues = self._analyze_files(file_metrics, smells)
        
        # Prioritize issues
        priorities = self._prioritize_issues(smells, summary)
        
        # Generate specific recommendations per smell
        recommendations = self._generate_recommendations(smells[:15])  # Top 15 issues
        
        # Overall summary
        overall_summary = self._generate_summary(summary, smells, file_issues)

        return {
            "summary": overall_summary,
            "priorities": priorities,
            "recommendations": recommendations,
            "problematic_files": file_issues,
            "html": self._format_html(overall_summary, priorities, recommendations, file_issues),
        }

    def _analyze_files(self, file_metrics: List[Dict[str, Any]], smells: List[Dict]) -> List[Dict[str, Any]]:
        """Identify most problematic files."""
        file_smell_counts = {}
        for smell in smells:
            file = smell.get('file', 'unknown')
            file_smell_counts[file] = file_smell_counts.get(file, 0) + 1
        
        # Get top 5 files with most issues
        top_files = sorted(file_smell_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        result = []
        for file_path, smell_count in top_files:
            # Find file metrics
            file_metric = next((fm for fm in file_metrics if fm.get('file') == file_path), None)
            if file_metric:
                result.append({
                    "file": file_path,
                    "smell_count": smell_count,
                    "loc": file_metric.get('loc', 0),
                    "functions": len(file_metric.get('functions', [])),
                })
        
        return result

    def _prioritize_issues(self, smells: List[Dict], summary: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prioritize issues by severity and type."""
        system_prompt = self._load_prompt("prioritize")
        if not system_prompt:
            system_prompt = "You are a senior software engineer. Prioritize code quality issues by impact and effort."
        
        # Group by type and severity
        issue_groups = {}
        for smell in smells:
            key = f"{smell.get('type', 'unknown')}|{smell.get('severity', 'info')}"
            if key not in issue_groups:
                issue_groups[key] = {
                    "type": smell.get('type', 'unknown'),
                    "severity": smell.get('severity', 'info'),
                    "count": 0,
                    "examples": [],
                }
            issue_groups[key]["count"] += 1
            if len(issue_groups[key]["examples"]) < 2:
                issue_groups[key]["examples"].append({
                    "file": smell.get('file', ''),
                    "function": smell.get('function', 'N/A'),
                    "message": smell.get('message', ''),
                })
        
        # Format for LLM
        issue_summary = "\n".join([
            f"- {v['type']} ({v['severity']}): {v['count']} occurrences\n  Example: {v['examples'][0]['file']} - {v['examples'][0]['message']}"
            for v in sorted(issue_groups.values(), key=lambda x: (x['severity'] != 'severe', -x['count']))[:10]
        ])
        
        user_prompt = f"""
Codebase size: {summary.get('total_files', 0)} files, {summary.get('total_loc', 0)} LOC

Detected Issues:
{issue_summary}

For each issue type, provide:
1. Priority (High/Medium/Low)
2. Impact on code quality
3. Estimated effort to fix
4. Recommended action

Format as a concise list.
"""
        
        response = self._call_llm(system_prompt, user_prompt)
        
        return [{
            "type": g["type"],
            "severity": g["severity"],
            "count": g["count"],
            "priority_guidance": response,
        } for g in sorted(issue_groups.values(), key=lambda x: (x['severity'] != 'severe', -x['count']))[:5]]

    def _generate_recommendations(self, smells: List[Dict]) -> List[Dict[str, str]]:
        """Generate specific fix recommendations for each smell."""
        recommendations = []
        
        # Load the refactor prompt once for all smells
        refactor_prompt = self._load_prompt("refactor_patch")
        if not refactor_prompt:
            refactor_prompt = "You are an expert code reviewer. Provide a specific, actionable fix recommendation."
        
        for smell in smells:
            system_prompt = refactor_prompt
            
            user_prompt = f"""
Issue: {smell.get('type', 'unknown')}
Severity: {smell.get('severity', 'info')}
File: {smell.get('file', 'unknown')}
Function: {smell.get('function', 'N/A')}
Line: {smell.get('line', 'N/A')}
Message: {smell.get('message', '')}

Provide:
1. Root cause (1 sentence)
2. Specific fix (2-3 sentences with code technique)
3. Expected benefit

Be concise and technical.
"""
            
            try:
                response = self._call_llm(system_prompt, user_prompt)
                recommendations.append({
                    "file": smell.get('file', ''),
                    "function": smell.get('function', 'N/A'),
                    "type": smell.get('type', ''),
                    "severity": smell.get('severity', ''),
                    "recommendation": response,
                })
            except Exception as e:
                print(f"Warning: Could not generate recommendation for smell: {e}")
        
        return recommendations

    def _generate_summary(self, summary: Dict[str, Any], smells: List[Dict], file_issues: List[Dict]) -> str:
        """Generate overall summary."""
        system_prompt = "You are a code quality expert. Provide a concise executive summary."

        user_prompt = f"""
Analyzed codebase:
- {summary.get('total_files', 0)} files
- {summary.get('total_loc', 0)} lines of code
- {summary.get('total_functions', 0)} functions
- {len(smells)} code quality issues

Top problematic files:
{chr(10).join([f"- {f['file']}: {f['smell_count']} issues, {f['loc']} LOC" for f in file_issues[:3]])}

Most common issue types:
{', '.join(list(set([s.get('type', '') for s in smells[:10]]))[:5])}

Provide a 3-4 sentence executive summary with:
1. Overall code quality assessment
2. Main concerns
3. Recommended next steps
"""

        return self._call_llm(system_prompt, user_prompt)

    def _format_html(self, summary: str, priorities: List[Dict], recommendations: List[Dict], files: List[Dict]) -> str:
        """Format AI insights as HTML with proper code formatting."""
        import html
        
        html_parts = [f"<h3>Executive Summary</h3><p>{html.escape(summary)}</p>"]
        
        if files:
            html_parts.append("<h3>Most Problematic Files</h3><ul>")
            for f in files[:5]:
                html_parts.append(f"<li><strong>{html.escape(f['file'])}</strong>: {f['smell_count']} issues ({f['loc']} LOC, {f['functions']} functions)</li>")
            html_parts.append("</ul>")
        
        if recommendations:
            html_parts.append("<h3>Top Recommendations</h3>")
            for i, rec in enumerate(recommendations[:10], 1):
                html_parts.append("<div class='ai-recommendation'>")
                html_parts.append(f"<strong>{i}. {html.escape(rec['type'])}</strong> ({html.escape(rec['severity'])}) - <code>{html.escape(rec['file'])}</code>")
                if rec['function'] != 'N/A':
                    html_parts.append(f" → <code>{html.escape(rec['function'])}</code>")
                
                # Format the recommendation with code blocks properly
                recommendation_text = rec['recommendation']
                # Replace code blocks with <pre><code>
                import re
                # Match triple backticks code blocks
                recommendation_text = re.sub(
                    r'```(\w+)?\n(.*?)\n```',
                    lambda m: f'<pre><code>{html.escape(m.group(2))}</code></pre>',
                    recommendation_text,
                    flags=re.DOTALL
                )
                # Match inline code
                recommendation_text = re.sub(
                    r'`([^`]+)`',
                    lambda m: f'<code>{html.escape(m.group(1))}</code>',
                    recommendation_text
                )
                # Convert newlines to <br>
                recommendation_text = recommendation_text.replace('\n', '<br>')
                
                html_parts.append(f"<div style='margin-top: 8px;'>{recommendation_text}</div>")
                html_parts.append("</div>")
        
        return ''.join(html_parts)

    def generate_summary(self, report_data: Dict[str, Any]) -> str:
        """
        Generate a high-level summary of the analysis (backward compatibility).

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
