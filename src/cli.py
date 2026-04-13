import click
import json
import asyncio
import os
import shutil
from rich.console import Console
from rich.panel import Panel

from crawler.spider import crawl_and_download
from analyzer.parser import JSAnalyzer
from detector.engine import SecretDetector
from validator.api_tester import KeyValidator
from github_scanner.scanner import GitHubScanner
from reporter.report import SecurityReporter

console = Console()

@click.group()
def cli():
    """API Token Leakage Detector - Scan modern frontend applications for exposed secrets."""
    pass

@cli.command()
@click.argument('url', required=True)
@click.option('--output', '-o', type=click.Path(), help='Output JSON report path')
@click.option('--threads', '-t', default=1, type=int, help='Number of threads for scanning')
def scan(url, output, threads):
    """Scan a target URL for leaked secrets in JS bundles."""
    console.print(Panel.fit(f"[bold blue]Starting scan for URL:[/bold blue] {url}"))
    console.print(f"[yellow]Threads:[/] {threads}")
    
    # 1. Crawler Module
    output_dir = "output/js_bundles"
    console.print("[cyan][Stage 1/5][/cyan] Crawling target to extract JS bundles...")
    downloaded_files = asyncio.run(crawl_and_download(url, output_dir=output_dir))
    
    if not downloaded_files:
        console.print("[red]No JS files were downloaded. Exiting.[/red]")
        return

    # 2. Analyzer Module
    console.print("[cyan][Stage 2/5][/cyan] Parsing JavaScript files to extract strings & configs...")
    all_strings = []
    all_configs = []
    
    for filepath in downloaded_files:
        analyzer = JSAnalyzer(filepath)
        res = analyzer.analyze()
        all_strings.extend(res["strings"])
        all_configs.extend(res["configs"])
        
    console.print(f"[green]Aggregated {len(all_strings)} strings and {len(all_configs)} configuration objects.[/green]")

    # 3. Detection Module
    console.print("[cyan][Stage 3/5][/cyan] Engaging Secret Detection Engine (Regex & Entropy)...")
    detector = SecretDetector(all_strings, all_configs)
    raw_findings = detector.analyze()
    console.print(f"Found {len(raw_findings)} potential secrets.")

    # 4. Validation Module & GitHub Scanning
    console.print("[cyan][Stage 4/5][/cyan] Validating discovered keys (API Abuse Testing)...")
    validator = KeyValidator(raw_findings)
    validated_findings = asyncio.run(validator.validate_all())

    console.print("[cyan][Stage 5/5][/cyan] Checking GitHub leak history...")
    gh_scanner = GitHubScanner()
    for finding in validated_findings:
        if gh_scanner.client:
            gh_res = gh_scanner.check_leaked_secret(finding["secret"])
            finding.update(gh_res)
        else:
            finding["github_exposed"] = "No GITHUB_TOKEN"

    # 5. Reporting Module
    reporter = SecurityReporter(url, validated_findings)
    reporter.display_terminal_report()
    
    if output:
        reporter.export_json(output)
        
    # Automatically save report in a txt format in the result directory
    parsed_url = url.replace("https://", "").replace("http://", "").split("/")[0]
    txt_output_path = os.path.join("result", f"{parsed_url}_report.txt")
    reporter.export_txt(txt_output_path)
        
    # Cleanup memory/files
    try:
        shutil.rmtree(output_dir)
    except Exception as e:
        console.print(f"[yellow]Failed to cleanup JS bundle dir: {e}[/yellow]")

if __name__ == '__main__':
    cli()
