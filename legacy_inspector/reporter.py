"""Report generation in JSON and HTML formats."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from jinja2 import Template

from legacy_inspector.dependency_graph import DependencyGraph
from legacy_inspector.metrics import FileMetrics
from legacy_inspector.scanner import ScanResult
from legacy_inspector.smells import CodeSmell


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI Code Inspector Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1, h2, h3 { color: #333; }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .severity-info { color: #17a2b8; }
        .severity-warning { color: #ffc107; font-weight: bold; }
        .severity-severe { color: #dc3545; font-weight: bold; }
        .code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .ai-section {
            background: #e7f3ff;
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #2196F3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 AI Code Inspector Report</h1>
        <p><strong>Generated:</strong> {{ generated_at }}</p>
        <p><strong>Project:</strong> {{ project_path }}</p>
    </div>

    <div class="container">
        <h2>📊 Summary</h2>
        <div class="summary">
            <div class="stat-box">
                <div class="stat-value">{{ summary.total_files }}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ summary.total_loc }}</div>
                <div class="stat-label">Lines of Code</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ summary.total_functions }}</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ summary.total_smells }}</div>
                <div class="stat-label">Code Smells</div>
            </div>
        </div>

        <h3>Languages</h3>
        <ul>
        {% for lang, count in summary.languages.items() %}
            <li><strong>{{ lang }}:</strong> {{ count }} files</li>
        {% endfor %}
        </ul>
    </div>

    <div class="container">
        <h2>🐛 Code Smells</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Type</th>
                    <th>File</th>
                    <th>Line</th>
                    <th>Function</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
            {% for smell in smells %}
                <tr>
                    <td class="severity-{{ smell.severity }}">{{ smell.severity|upper }}</td>
                    <td>{{ smell.type }}</td>
                    <td><span class="code">{{ smell.file }}</span></td>
                    <td>{{ smell.line }}</td>
                    <td>{{ smell.function or '-' }}</td>
                    <td>{{ smell.message }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="container">
        <h2>📁 Files Overview</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Language</th>
                    <th>LOC</th>
                    <th>Functions</th>
                    <th>Imports</th>
                </tr>
            </thead>
            <tbody>
            {% for file in files %}
                <tr>
                    <td><span class="code">{{ file.file }}</span></td>
                    <td>{{ file.language }}</td>
                    <td>{{ file.loc }}</td>
                    <td>{{ file.functions_count }}</td>
                    <td>{{ file.imports_count }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>

    {% if dependency_graph %}
    <div class="container">
        <h2>🕸️ Dependency Graph</h2>
        <p><strong>Total Modules:</strong> {{ dependency_graph.total_modules }}</p>
        <p><strong>Total Dependencies:</strong> {{ dependency_graph.total_dependencies }}</p>
        
        {% if dependency_graph.circular_dependencies %}
        <h3>⚠️ Circular Dependencies</h3>
        <ul>
        {% for cycle in dependency_graph.circular_dependencies %}
            <li>{{ cycle|join(' → ') }}</li>
        {% endfor %}
        </ul>
        {% endif %}
    </div>
    {% endif %}

    {% if ai_insights %}
    <div class="container ai-section">
        <h2>🤖 AI Insights</h2>
        {{ ai_insights|safe }}
    </div>
    {% endif %}

    <div class="container">
        <p style="text-align: center; color: #666; font-size: 0.9em;">
            Generated by <strong>AI Code Inspector</strong> v0.1.0
        </p>
    </div>
</body>
</html>
"""


def generate_json_report(
    scan_result: ScanResult,
    file_metrics: List[FileMetrics],
    smells: List[CodeSmell],
    dependency_graph: Optional[DependencyGraph] = None,
    ai_insights: Optional[dict] = None,
) -> dict:
    """
    Generate JSON report.

    Args:
        scan_result: ScanResult from scanner
        file_metrics: List of FileMetrics
        smells: List of detected CodeSmell objects
        dependency_graph: Optional DependencyGraph
        ai_insights: Optional AI-generated insights

    Returns:
        Dictionary representing the report
    """
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            **scan_result.get_summary(),
            "total_functions": sum(len(fm.functions) for fm in file_metrics),
            "total_smells": len(smells),
        },
        "files": [fm.to_dict() for fm in file_metrics],
        "smells": [smell.to_dict() for smell in smells],
    }

    if dependency_graph:
        report["dependency_graph"] = dependency_graph.to_dict()

    if ai_insights:
        report["ai_insights"] = ai_insights

    return report


def generate_html_report(
    report_data: dict,
    output_path: Path,
    project_path: str = "",
):
    """
    Generate HTML report from JSON report data.

    Args:
        report_data: Report dictionary from generate_json_report
        output_path: Path to save HTML file
        project_path: Path to analyzed project
    """
    template = Template(HTML_TEMPLATE)

    html = template.render(
        generated_at=report_data.get("generated_at", ""),
        project_path=project_path,
        summary=report_data.get("summary", {}),
        files=report_data.get("files", []),
        smells=report_data.get("smells", []),
        dependency_graph=report_data.get("dependency_graph"),
        ai_insights=report_data.get("ai_insights", {}).get("html", ""),
    )

    output_path.write_text(html, encoding="utf-8")


def save_json_report(report_data: dict, output_path: Path):
    """Save JSON report to file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)


def generate_report(
    scan_result: ScanResult,
    file_metrics: List[FileMetrics],
    smells: List[CodeSmell],
    dependency_graph: Optional[DependencyGraph] = None,
    ai_insights: Optional[dict] = None,
    json_path: Optional[Path] = None,
    html_path: Optional[Path] = None,
    project_path: str = "",
):
    """
    Generate and save reports.

    Args:
        scan_result: ScanResult from scanner
        file_metrics: List of FileMetrics
        smells: List of CodeSmell objects
        dependency_graph: Optional DependencyGraph
        ai_insights: Optional AI insights
        json_path: Path to save JSON report (optional)
        html_path: Path to save HTML report (optional)
        project_path: Path to analyzed project
    """
    # Generate JSON report
    report_data = generate_json_report(
        scan_result, file_metrics, smells, dependency_graph, ai_insights
    )

    # Save JSON if requested
    if json_path:
        save_json_report(report_data, json_path)
        print(f"JSON report saved to: {json_path}")

    # Save HTML if requested
    if html_path:
        generate_html_report(report_data, html_path, project_path)
        print(f"HTML report saved to: {html_path}")

    return report_data
