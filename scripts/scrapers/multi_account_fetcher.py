"""
Multi Account Fetcher - Rotate through multiple accounts/cookies for scraping
"""
import json
import random
import requests

class MultiAccountFetcher:
    def __init__(self, accounts_file):
        with open(accounts_file, 'r') as f:
            self.accounts = json.load(f)
        self.current_index = 0

    def get_session(self):
        account = self.accounts[self.current_index]
        session = requests.Session()
        session.headers.update({
            "User-Agent": account.get("user_agent", "Mozilla/5.0"),
        })
        if "cookies" in account:
            for name, value in account["cookies"].items():
                session.cookies.set(name, value)
        self.current_index = (self.current_index + 1) % len(self.accounts)
        return session

    def fetch(self, url):
        session = self.get_session()
        resp = session.get(url)
        return resp

    def fetch_all(self, urls):
        results = []
        for url in urls:
            resp = self.fetch(url)
            results.append(resp)
        return results

if __name__ == '__main__':
    # Example usage
    fetcher = MultiAccountFetcher("accounts.json")
    resp = fetcher.fetch("https://example.com")
    print(f"Status: {resp.status_code}")
