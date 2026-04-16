import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        def handle_response(response):
            print("Sync Headers property:", hasattr(response, "headers"))
            if hasattr(response, "headers"):
                print("Headers type:", type(response.headers))
                print("Content-type:", response.headers.get("content-type", ""))
                
        page.on("response", handle_response)
        await page.goto("https://example.com")
        await asyncio.sleep(1)
        await browser.close()

asyncio.run(run())
