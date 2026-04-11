import os
from github import Github
from rich.console import Console
from datetime import datetime

console = Console()

class GitHubScanner:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.client = Github(self.github_token) if self.github_token else None
        
    def check_leaked_secret(self, secret_value):
        """Search GitHub for the exact secret string to see if it's publicly known."""
        if not self.client:
            return {"github_exposed": "Unknown - No Token"}
            
        # Refrain from hitting rate limits instantly
        # GitHub search syntax requires quotes for exact match
        query = f'"{secret_value}"'
        try:
            results = self.client.search_code(query=query)
            count = results.totalCount
            if count > 0:
                return {
                    "github_exposed": "True",
                    "repo_occurrences": count
                }
            return {
                "github_exposed": "False",
                "repo_occurrences": 0
            }
        except Exception as e:
            return {
                "github_exposed": f"Search Error ({str(e)[:30]})"
            }
