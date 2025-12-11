"""Command-line interface for Legacy Inspector."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from legacy_inspector.scanner import scan_directory
from legacy_inspector.metrics import calculate_metrics
from legacy_inspector.smells import detect_smells
from legacy_inspector.dependency_graph import build_dependency_graph, generate_dependency_report
from legacy_inspector.reporter import generate_report
from legacy_inspector.ai_helper import create_ai_helper

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """AI Code Inspector - Multi-language code analyzer."""
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output-json", type=click.Path(), help="Output JSON report path")
@click.option("--output-html", type=click.Path(), help="Output HTML report path")
@click.option("--ai", is_flag=True, help="Enable AI-powered insights")
@click.option("--export-graph", type=click.Path(), help="Export dependency graph (DOT format)")
def analyze(
    path: str,
    output_json: Optional[str],
    output_html: Optional[str],
    ai: bool,
    export_graph: Optional[str],
):
    """Analyze a codebase and generate reports."""
    console.print(f"\n[bold blue]🔍 Analyzing: {path}[/bold blue]\n")

    # Step 1: Scan directory
    console.print("[cyan]📁 Scanning files...[/cyan]")
    scan_result = scan_directory(path)

    if scan_result.errors:
        console.print(f"[yellow]⚠️  {len(scan_result.errors)} errors during scanning[/yellow]")

    console.print(
        f"[green]✓ Found {len(scan_result.files)} files "
        f"({scan_result.total_loc} LOC)[/green]\n"
    )

    if len(scan_result.files) == 0:
        console.print("[red]No supported files found![/red]")
        return

    # Step 2: Calculate metrics
    console.print("[cyan]📊 Calculating metrics...[/cyan]")
    file_metrics = calculate_metrics(scan_result.files)

    total_functions = sum(len(fm.functions) for fm in file_metrics)
    console.print(f"[green]✓ Analyzed {total_functions} functions[/green]\n")

    # Step 3: Detect smells
    console.print("[cyan]🐛 Detecting code smells...[/cyan]")
    smells = detect_smells(file_metrics)

    # Count by severity
    severity_counts = {}
    for smell in smells:
        severity_counts[smell.severity] = severity_counts.get(smell.severity, 0) + 1

    console.print(f"[green]✓ Found {len(smells)} issues[/green]")
    for severity, count in severity_counts.items():
        color = "red" if severity == "severe" else "yellow" if severity == "warning" else "blue"
        console.print(f"  [{color}]{severity}: {count}[/{color}]")
    console.print()

    # Step 4: Build dependency graph
    console.print("[cyan]🕸️  Building dependency graph...[/cyan]")
    dep_graph = build_dependency_graph(file_metrics)
    dep_report = generate_dependency_report(dep_graph)

    console.print(
        f"[green]✓ {dep_report['total_modules']} modules, "
        f"{dep_report['total_dependencies']} dependencies[/green]"
    )

    if dep_report.get("circular_dependencies"):
        console.print(
            f"[red]⚠️  Found {len(dep_report['circular_dependencies'])} "
            f"circular dependencies![/red]"
        )
    console.print()

    # Export graph if requested
    if export_graph:
        graph_path = Path(export_graph)
        dep_graph.export_dot(graph_path)
        console.print(f"[green]✓ Dependency graph exported to: {graph_path}[/green]\n")

    # Step 5: AI insights (optional)
    ai_insights = None
    if ai:
        console.print("[cyan]🤖 Generating AI insights...[/cyan]")
        ai_helper = create_ai_helper()

        if ai_helper:
            try:
                # Generate summary
                report_data = {
                    "summary": {
                        **scan_result.get_summary(),
                        "total_functions": total_functions,
                    },
                    "smells": [s.to_dict() for s in smells],
                }

                summary = ai_helper.generate_summary(report_data)
                console.print(f"[green]✓ AI Summary:[/green]\n{summary}\n")

                ai_insights = {
                    "summary": summary,
                    "html": f"<p>{summary}</p>",
                }

            except Exception as e:
                console.print(f"[red]Error generating AI insights: {e}[/red]\n")
        else:
            console.print("[yellow]AI helper not available (check LLM_API_KEY)[/yellow]\n")

    # Step 6: Generate reports
    json_path = Path(output_json) if output_json else None
    html_path = Path(output_html) if output_html else None

    generate_report(
        scan_result=scan_result,
        file_metrics=file_metrics,
        smells=smells,
        dependency_graph=dep_graph,
        ai_insights=ai_insights,
        json_path=json_path,
        html_path=html_path,
        project_path=path,
    )

    # Summary table
    console.print("\n[bold]📋 Summary[/bold]")
    table = Table()
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Files", str(len(scan_result.files)))
    table.add_row("Lines of Code", str(scan_result.total_loc))
    table.add_row("Functions", str(total_functions))
    table.add_row("Code Smells", str(len(smells)))
    table.add_row("Modules", str(dep_report["total_modules"]))

    console.print(table)
    console.print()


@main.command()
@click.argument("report_path", type=click.Path(exists=True))
def summarize(report_path: str):
    """Summarize an existing JSON report."""
    import json

    console.print(f"\n[bold blue]📄 Reading report: {report_path}[/bold blue]\n")

    with open(report_path, "r") as f:
        report = json.load(f)

    summary = report.get("summary", {})

    table = Table(title="Report Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Files", str(summary.get("total_files", 0)))
    table.add_row("Total LOC", str(summary.get("total_loc", 0)))
    table.add_row("Total Functions", str(summary.get("total_functions", 0)))
    table.add_row("Total Smells", str(summary.get("total_smells", 0)))

    console.print(table)
    console.print()

    # Show language breakdown
    languages = summary.get("languages", {})
    if languages:
        console.print("[bold]Languages:[/bold]")
        for lang, count in languages.items():
            console.print(f"  • {lang}: {count} files")
        console.print()

    # Show top smells
    smells = report.get("smells", [])
    if smells:
        smell_types = {}
        for smell in smells:
            smell_type = smell.get("type", "unknown")
            smell_types[smell_type] = smell_types.get(smell_type, 0) + 1

        console.print("[bold]Top Code Smells:[/bold]")
        for smell_type, count in sorted(smell_types.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            console.print(f"  • {smell_type}: {count}")
        console.print()


@main.command()
@click.argument("report_path", type=click.Path(exists=True))
@click.option("--port", default=8000, help="Port to serve on")
def serve(report_path: str, port: int):
    """Serve an HTML report locally (simple HTTP server)."""
    import http.server
    import socketserver
    import webbrowser

    report_file = Path(report_path)

    if not report_file.exists():
        console.print(f"[red]Report not found: {report_path}[/red]")
        return

    # If it's a JSON report, we need to generate HTML first
    if report_file.suffix == ".json":
        console.print("[yellow]Converting JSON to HTML...[/yellow]")
        import json
        from legacy_inspector.reporter import generate_html_report

        with open(report_file, "r") as f:
            report_data = json.load(f)

        html_path = report_file.with_suffix(".html")
        generate_html_report(report_data, html_path)
        report_file = html_path
        console.print(f"[green]HTML generated: {html_path}[/green]")

    # Serve the file
    directory = report_file.parent
    filename = report_file.name

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    console.print(f"\n[green]🌐 Serving report at http://localhost:{port}/{filename}[/green]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")

    webbrowser.open(f"http://localhost:{port}/{filename}")

    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped[/yellow]")


if __name__ == "__main__":
    main()
