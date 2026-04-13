import json
import os
from rich.console import Console
from rich.table import Table

console = Console()

class SecurityReporter:
    def __init__(self, target_url, findings):
        self.target_url = target_url
        self.findings = findings

    def display_terminal_report(self):
        console.print("\n[bold red]=== API Token Leakage Report ===[/bold red]")
        console.print(f"[bold]Target:[/] {self.target_url}")
        console.print(f"[bold]Total Secrets Found:[/] {len(self.findings)}\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", width=25)
        table.add_column("Secret Fragment", width=35)
        table.add_column("Validation", width=25)
        table.add_column("Severity")
        
        for f in self.findings:
            secret_preview = f["secret"][:10] + "..." + f["secret"][-5:] if len(f["secret"]) > 15 else f["secret"]
            val_status = f.get("validation", "N/A")
            severity = f.get("severity", "Info")
            
            color = "white"
            if severity == "Critical":
                color = "red bold"
            elif severity == "High":
                color = "red"
            elif severity == "Medium":
                color = "yellow"
                
            table.add_row(
                f["type"],
                secret_preview,
                val_status,
                f"[{color}]{severity}[/{color}]"
            )
        
        console.print(table)

    def export_json(self, filepath):
        report_data = {
            "target": self.target_url,
            "total_findings": len(self.findings),
            "findings": self.findings
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4)
        console.print(f"[green]Report saved to {filepath}[/green]")

    def export_txt(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== API Token Leakage Report ===\n")
            f.write(f"Target: {self.target_url}\n")
            f.write(f"Total Secrets Found: {len(self.findings)}\n\n")
            for finding in self.findings:
                f.write("-" * 40 + "\n")
                f.write(f"Type: {finding.get('type')}\n")
                f.write(f"Secret: {finding.get('secret')}\n")
                f.write(f"Validation: {finding.get('validation', 'N/A')}\n")
                f.write(f"Severity: {finding.get('severity', 'Info')}\n")
                if "github_exposed" in finding:
                    f.write(f"GitHub Exposed: {finding.get('github_exposed')}\n")
            f.write("-" * 40 + "\n")
        console.print(f"[green]Text report saved to {filepath}[/green]")
