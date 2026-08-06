import requests
from bs4 import BeautifulSoup

BASE = "https://plsbeta.com"

def extract_cookies():
    session = requests.Session()
    r = session.get(f"{BASE}/login", timeout=30)
    cookies = session.cookies.get_dict()
    return cookies

def run():
    cookies = extract_cookies()
    print(json.dumps(cookies, indent=2))

if __name__ == "__main__":
    import json
    run()
