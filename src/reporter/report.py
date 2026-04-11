import json
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
