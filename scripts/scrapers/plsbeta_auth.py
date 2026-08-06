"""
PLS Beta Auth - Authentication module for PLS Beta scraper
"""
import requests
import json
import os

class PLSBetaAuth:
    def __init__(self, base_url="https://www.pls-beta.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        url = f"{self.base_url}/api/login"
        resp = self.session.post(url, json={'username': username, 'password': password})
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get('token')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            return True
        return False

    def save_session(self, filename='pls_session.json'):
        with open(filename, 'w') as f:
            json.dump({
                'token': self.token,
                'cookies': dict(self.session.cookies),
            }, f)

    def load_session(self, filename='pls_session.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                for name, value in data.get('cookies', {}).items():
                    self.session.cookies.set(name, value)
                return True
        return False

if __name__ == '__main__':
    auth = PLSBetaAuth()
    # Example usage
    print("Auth module ready")
