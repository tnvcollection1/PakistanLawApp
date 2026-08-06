import requests
import os

BASE = "https://plsbeta.com"

def get_auth_token():
    username = os.getenv("PLSBETA_USER", "")
    password = os.getenv("PLSBETA_PASS", "")
    r = requests.post(f"{BASE}/api/auth/login", json={"username": username, "password": password})
    r.raise_for_status()
    return r.json()["token"]

def fetch_with_auth(endpoint):
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}{endpoint}", headers=headers)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    print(fetch_with_auth("/api/cases/recent"))
