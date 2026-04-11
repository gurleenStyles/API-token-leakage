import asyncio
import aiohttp
from rich.console import Console

console = Console()

class KeyValidator:
    def __init__(self, findings):
        self.findings = findings
        self.validated_results = []
        
    async def validate_all(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for finding in self.findings:
                if finding["type"] == "Google API Key":
                    tasks.append(self.test_google_maps(session, finding))
                elif "Stripe" in finding["type"]:
                    tasks.append(self.test_stripe(session, finding))
                else:
                    finding["validation"] = "untested"
                    finding["severity"] = "Low"
                    self.validated_results.append(finding)
                    
            if tasks:
                await asyncio.gather(*tasks)
                
        return self.validated_results

    async def test_google_maps(self, session, finding):
        api_key = finding["secret"]
        # Basic Places API check
        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Museum%20of%20Contemporary%20Art%20Australia&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key={api_key}"
        try:
            async with session.get(url) as response:
                data = await response.json()
                if "error_message" in data:
                    finding["validation"] = "Invalid or Restricted"
                    finding["severity"] = "Info"
                else:
                    finding["validation"] = "Valid - Places API Accessible"
                    finding["severity"] = "High"
        except:
            finding["validation"] = "Error Testing"
            finding["severity"] = "Unknown"
        self.validated_results.append(finding)

    async def test_stripe(self, session, finding):
        api_key = finding["secret"]
        url = "https://api.stripe.com/v1/charges"
        try:
            async with session.get(url, auth=aiohttp.BasicAuth(api_key, '')) as response:
                if response.status == 200:
                    finding["validation"] = "Valid - Full Access"
                    finding["severity"] = "Critical"
                elif response.status == 403:
                    finding["validation"] = "Valid - Restricted Access"
                    finding["severity"] = "Medium"
                else:
                    finding["validation"] = "Invalid Key"
                    finding["severity"] = "Info"
        except:
            finding["validation"] = "Error Testing"
            finding["severity"] = "Unknown"
        self.validated_results.append(finding)
