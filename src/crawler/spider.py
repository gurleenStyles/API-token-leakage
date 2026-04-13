import asyncio #lets Python do multiple things at the same time (download 10 files simultaneously instead of one by one)
import os
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
import aiohttp
from rich.console import Console

# It opens a real browser, visits a target website,
# collects all the JavaScript file URLs it finds, 
# then downloads them to your computer.

console = Console()

class WebCrawler:
    def __init__(self, target_url, output_dir="output/js_bundles"):
        self.target_url = target_url
        self.output_dir = output_dir
        self.js_links = set()
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    async def extract_links(self):
        """Use Playwright to render the page and intercept JS network requests."""
        console.print(f"[blue]Starting browser to crawl {self.target_url}...[/blue]")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Listen for network responses to catch dynamically loaded JS
            page.on("response", self._handle_response)

            try:
                await page.goto(self.target_url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                console.print(f"[red]Failed to load page: {e}[/red]")
            
            # Extract script tags from the DOM as a fallback
            script_tags = await page.locator("script[src]").all()
            for tag in script_tags:
                src = await tag.get_attribute("src")
                if src:
                    full_url = urljoin(self.target_url, src)
                    if self._is_valid_js_url(full_url):
                        self.js_links.add(full_url)
            
            await browser.close()
            
        console.print(f"[green]Extracted {len(self.js_links)} JS bundle links.[/green]")
        return list(self.js_links)

    def _handle_response(self, response):
        """Callback to capture JS files loaded via network."""
        url = response.url
        if response.ok and self._is_valid_js_url(url):
            self.js_links.add(url)

    def _is_valid_js_url(self, url):
        """Filter to include only JavaScript files and optionally exclude known generic libraries."""
        parsed = urlparse(url)
        return parsed.path.endswith(".js")

    async def _download_file(self, session, url):
        """Download a single JS file."""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    filename = os.path.basename(urlparse(url).path)
                    if not filename:
                        filename = f"bundle_{hash(url)}.js"
                    
                    filepath = os.path.join(self.output_dir, filename)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    return filepath
        except Exception as e:
            console.print(f"[yellow]Failed to download {url}: {e}[/yellow]")
        return None

    async def download_js_bundles(self):
        """Download all extracted JS links concurrently."""
        if not self.js_links:
            console.print("[yellow]No JS links found to download.[/yellow]")
            return []

        console.print(f"[blue]Downloading {len(self.js_links)} JS packages...[/blue]")
        
        downloaded_files = []
        async with aiohttp.ClientSession() as session:
            tasks = [self._download_file(session, url) for url in self.js_links]
            results = await asyncio.gather(*tasks)
            
            downloaded_files = [res for res in results if res]
            
        console.print(f"[green]Successfully downloaded {len(downloaded_files)} JS files.[/green]")
        return downloaded_files

async def crawl_and_download(url, output_dir="output/js_bundles"):
    crawler = WebCrawler(url, output_dir=output_dir)
    await crawler.extract_links()
    files = await crawler.download_js_bundles()
    return files
