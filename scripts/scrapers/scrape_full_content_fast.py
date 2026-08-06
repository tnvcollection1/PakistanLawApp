import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures

def scrape_full_content_fast():
    base_url = "https://pakistanlawsite.com"
    resp = requests.get(base_url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    links = [a['href'] for a in soup.find_all('a', href=True)[:20]]
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(requests.get, base_url + link, timeout=10): link for link in links}
        for future in concurrent.futures.as_completed(futures):
            link = futures[future]
            try:
                page = future.result()
                results.append({"link": link, "status": page.status_code})
            except Exception as e:
                results.append({"link": link, "error": str(e)})
    
    with open('full_content_fast.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Fast scraped {len(results)} pages")

if __name__ == '__main__':
    scrape_full_content_fast()
