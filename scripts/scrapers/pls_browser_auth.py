import requests
from bs4 import BeautifulSoup
import os

BASE = "https://plsbeta.com"

def browser_login(username, password):
    session = requests.Session()
    r = session.get(f"{BASE}/login", timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.select_one("input[name='csrf_token']")
    csrf = token["value"] if token else ""
    r = session.post(f"{BASE}/login", data={
        "username": username,
        "password": password,
        "csrf_token": csrf
    }, timeout=30)
    return session

def run():
    username = os.getenv("PLSBETA_USER", "")
    password = os.getenv("PLSBETA_PASS", "")
    session = browser_login(username, password)
    r = session.get(f"{BASE}/dashboard", timeout=30)
    print(f"Dashboard status: {r.status_code}")

if __name__ == "__main__":
    run()
