"""
Fetch Missing Content - Fetch content for cases that are missing it
"""
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pls-beta.com"

class MissingContentFetcher:
    def __init__(self):
        self.session = requests.Session()

    def fetch_content(self, case_id):
        url = f"{BASE_URL}/cases/{case_id}"
        resp = self.session.get(url)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        content = soup.select_one('.case-content')
        return content.get_text(strip=True) if content else None

    def process_missing(self, input_file, output_file):
        with open(input_file, 'r') as f:
            cases = json.load(f)
        updated = []
        for case in cases:
            if not case.get('content'):
                case_id = case.get('id')
                content = self.fetch_content(case_id)
                if content:
                    case['content'] = content
                    print(f"Fetched content for case {case_id}")
            updated.append(case)
        with open(output_file, 'w') as f:
            json.dump(updated, f, indent=2)
        print(f"Processed {len(updated)} cases")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python fetch_missing_content.py <input.json> <output.json>")
        sys.exit(1)
    fetcher = MissingContentFetcher()
    fetcher.process_missing(sys.argv[1], sys.argv[2])
