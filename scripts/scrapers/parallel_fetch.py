"""
Parallel Fetch - Parallel content fetching for scrapers
"""
import concurrent.futures
import requests

class ParallelFetcher:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers

    def fetch_single(self, url):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return {'url': url, 'status': resp.status_code, 'content': resp.text[:1000]}
        except Exception as e:
            return {'url': url, 'error': str(e)}

    def fetch_many(self, urls):
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_single, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                results.append(result)
        return results

if __name__ == '__main__':
    fetcher = ParallelFetcher()
    urls = ["https://example.com"] * 5
    results = fetcher.fetch_many(urls)
    print(f"Fetched {len(results)} URLs")
    for r in results[:3]:
        print(r)
