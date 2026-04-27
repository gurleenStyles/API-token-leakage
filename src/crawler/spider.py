import asyncio #lets Python do multiple things at the same time (download 10 files simultaneously instead of one by one)
import os
from urllib.parse import urljoin, urlparse #url tools 
from playwright.async_api import async_playwright #controls the browser from your python code
import aiohttp #fast async HTTP client for actually downloading the files
from rich.console import Console #makes the terminaloutput colourfull

# It opens a real browser, visits a target website,
# collects all the JavaScript file URLs it finds, 
# then downloads them to your computer.

console = Console()

#class is like a blueprint for creating objects
class WebCrawler:
    def __init__(self, target_url, output_dir="output/js_bundles"):
        self.target_url = target_url
        self.output_dir = output_dir
        self.js_links = set()
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        self.semaphore = asyncio.Semaphore(5)

    #extract links is the function that will extract the links from the page
    async def extract_links(self):
        """Use Playwright to render the page and intercept JS network requests."""
        console.print(f"[blue]Starting browser to crawl {self.target_url}...[/blue]")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            page = await context.new_page()

            # Listen for network responses to catch dynamically loaded JS
            #this function will capture the js files
            page.on("response", self._handle_response)

            try:
                await page.goto(self.target_url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                console.print(f"[red]Failed to load page: {e}[/red]")
            
            # Extract script tags from the DOM (document object model)as a fallback (html pages)
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
        content_type = response.headers.get("content-type", "")
        if response.ok and self._is_valid_js_url(url, content_type):
            self.js_links.add(url)

    def _is_valid_js_url(self, url, content_type=""):
        """Filter to include only JavaScript files and optionally exclude known generic libraries."""
        content_type = content_type or ""
        # check content-type: application/javascript or text/javascript
        if "application/javascript" in content_type.lower() or "text/javascript" in content_type.lower():
            return True
            
        parsed = urlparse(url)
        return parsed.path.endswith(".js")
 
    #download file is the function that will download the file
    #saves js to the disk 
    
    async def _download_file(self, session, url):
        """Download a single JS file."""
        try:
            async with self.semaphore:
                async with session.get(url) as response:
                    content_length = int(response.headers.get("content-length", 0))
                    if content_length > 10 * 1024 * 1024:
                        console.print(f"[yellow]Skipping {url}: File too large ({content_length} bytes)[/yellow]")
                        return None
                        
                    if response.status == 200:
                        content = await response.text()
                        
                        parsed_url = urlparse(url)
                        domain = parsed_url.netloc.replace('.', '_')
                        base_name = os.path.basename(parsed_url.path)
                        
                        if not base_name:
                            filename = f"{domain}_bundle_{hash(url)}.js"
                        else:
                            filename = f"{domain}_{base_name}"
                        
                        filepath = os.path.join(self.output_dir, filename)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        return filepath
        except Exception as e:
            console.print(f"[yellow]Failed to download {url}: {e}[/yellow]")
        return None
    #download js bundles is the function that will download all the js files
    #parallel downloading 
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
#wrapper that creates the crawler and calls the extract and download functions
async def crawl_and_download(url, output_dir="output/js_bundles"):
    crawler = WebCrawler(url, output_dir=output_dir)
    await crawler.extract_links()
    files = await crawler.download_js_bundles()
    return files

#visit URL → browser loads page → watch all network requests
        #→ also scan <script> tags → collect all .js URLs
        #→ download all of them in parallel → return file paths