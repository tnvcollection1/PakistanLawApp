#!/usr/bin/env python3
"""Fast content fetcher using async requests"""

import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup

async def fetch_url(session, url):
    """Fetch URL asynchronously"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            return {
                'url': url,
                'title': soup.find('title').text.strip() if soup.find('title') else '',
                'content': soup.find('body').text.strip() if soup.find('body') else ''
            }
    except Exception as e:
        return {'url': url, 'error': str(e)}

async def fetch_all(urls):
    """Fetch all URLs concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def main():
    urls = [
        "https://www.pakistanlawsite.com/cases/1",
        "https://www.pakistanlawsite.com/statutes/1"
    ]
    results = asyncio.run(fetch_all(urls))
    with open('fast_fetch_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Fetched {len(results)} URLs")

if __name__ == '__main__':
    main()
