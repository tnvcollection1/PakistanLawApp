"""
LHC Playwright Scraper - Scraper for Lahore High Court using Playwright
"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://lhc.gov.pk"

async def scrape_lhc():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/judgments")
        await page.wait_for_selector(".judgment-list")
        judgments = await page.evaluate('''() => {
            const items = document.querySelectorAll('.judgment-item');
            return Array.from(items).map(item => ({
                title: item.querySelector('.title')?.textContent?.trim(),
                date: item.querySelector('.date')?.textContent?.trim(),
                url: item.querySelector('a')?.href,
            }));
        }''')
        await browser.close()
        return judgments

if __name__ == '__main__':
    results = asyncio.run(scrape_lhc())
    print(f"Scraped {len(results)} judgments")
    for r in results[:5]:
        print(r)
