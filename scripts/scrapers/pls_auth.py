import requests
from bs4 import BeautifulSoup
import os, json

BASE_URL = "https://www.pakistanlawsite.com"
LOGIN_URL = f"{BASE_URL}/login"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def pls_login():
    session = requests.Session()
    r = session.get(LOGIN_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})
    if not token:
        raise ValueError("No CSRF token found")
    data = {
        '_token': token['value'],
        'email': os.getenv('PLS_EMAIL'),
        'password': os.getenv('PLS_PASSWORD'),
        'remember': 'on',
    }
    r = session.post(LOGIN_URL, data=data, headers=HEADERS)
    if r.status_code != 200 and 'dashboard' not in r.url:
        raise ValueError("Login failed")
    return session

def get_auth_headers():
    return {
        "Authorization": f"Bearer {os.getenv('PLS_API_TOKEN', '')}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

if __name__ == '__main__':
    session = pls_login()
    print("[+] Authenticated successfully")
