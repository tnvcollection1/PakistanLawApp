#!/usr/bin/env python3
"""
Scraper with authentication support for protected legal databases.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class AuthenticatedScraper:
    """Scraper with authentication capabilities."""
    
    def __init__(self, base_url: str, auth_config: Dict[str, Any]):
        self.base_url = base_url
        self.auth_config = auth_config
        self.session = requests.Session()
        self.authenticated = False
        self.auth_token = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with the target system.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            auth_type = self.auth_config.get('type', 'basic')
            
            if auth_type == 'basic':
                return self._basic_auth()
            elif auth_type == 'bearer':
                return self._bearer_auth()
            elif auth_type == 'form':
                return self._form_auth()
            elif auth_type == 'api_key':
                return self._api_key_auth()
            else:
                print(f"Unsupported auth type: {auth_type}")
                return False
                
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _basic_auth(self) -> bool:
        """Basic HTTP authentication."""
        username = self.auth_config.get('username')
        password = self.auth_config.get('password')
        
        if not username or not password:
            print("Missing credentials for basic auth")
            return False
        
        self.session.auth = (username, password)
        
        # Test authentication
        test_url = self.auth_config.get('test_url', self.base_url)
        response = self.session.get(test_url)
        
        if response.status_code == 200:
            self.authenticated = True
            print("Basic authentication successful")
            return True
        else:
            print(f"Basic auth failed: {response.status_code}")
            return False
    
    def _bearer_auth(self) -> bool:
        """Bearer token authentication."""
        token = self.auth_config.get('token')
        
        if not token:
            # Try to get token from token endpoint
            token_url = self.auth_config.get('token_url')
            client_id = self.auth_config.get('client_id')
            client_secret = self.auth_config.get('client_secret')
            
            if token_url and client_id and client_secret:
                response = self.session.post(
                    token_url,
                    data={
                        'grant_type': 'client_credentials',
                        'client_id': client_id,
                        'client_secret': client_secret
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    token = token_data.get('access_token')
        
        if not token:
            print("No bearer token available")
            return False
        
        self.auth_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
        self.authenticated = True
        print("Bearer authentication successful")
        return True
    
    def _form_auth(self) -> bool:
        """Form-based authentication."""
        login_url = self.auth_config.get('login_url')
        username = self.auth_config.get('username')
        password = self.auth_config.get('password')
        
        if not login_url or not username or not password:
            print("Missing form auth configuration")
            return False
        
        # Get login form
        response = self.session.get(login_url)
        
        # Extract CSRF token if present
        csrf_token = None
        if 'csrf' in response.text.lower():
            # Simple CSRF extraction (would need proper parsing in production)
            import re
            match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            if match:
                csrf_token = match.group(1)
        
        # Submit login form
        login_data = {
            'username': username,
            'password': password
        }
        
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
        
        response = self.session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            self.authenticated = True
            print("Form authentication successful")
            return True
        else:
            print(f"Form auth failed: {response.status_code}")
            return False
    
    def _api_key_auth(self) -> bool:
        """API key authentication."""
        api_key = self.auth_config.get('api_key')
        header_name = self.auth_config.get('header_name', 'X-API-Key')
        
        if not api_key:
            print("No API key provided")
            return False
        
        self.session.headers.update({
            header_name: api_key
        })
        
        self.authenticated = True
        print("API key authentication successful")
        return True
    
    def fetch_page(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """
        Fetch a page with authentication.
        
        Args:
            url: URL to fetch
            params: Optional query parameters
            
        Returns:
            Page content or None if failed
        """
        if not self.authenticated:
            print("Not authenticated. Call authenticate() first.")
            return None
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 401:
                print("Authentication expired. Re-authenticating...")
                if self.authenticate():
                    return self.fetch_page(url, params)
                else:
                    return None
            else:
                print(f"Request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def save_session(self, filepath: str):
        """Save session cookies to file."""
        cookies = {cookie.name: cookie.value for cookie in self.session.cookies}
        with open(filepath, 'w') as f:
            json.dump(cookies, f)
        print(f"Session saved to {filepath}")
    
    def load_session(self, filepath: str):
        """Load session cookies from file."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                cookies = json.load(f)
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            print(f"Session loaded from {filepath}")


def main():
    """Main function to demonstrate authenticated scraping."""
    print("=" * 50)
    print("AUTHENTICATED SCRAPER")
    print("=" * 50)
    
    # Example configuration
    config = {
        "type": "basic",
        "username": os.getenv("SCRAPER_USERNAME", "user"),
        "password": os.getenv("SCRAPER_PASSWORD", "pass"),
        "test_url": "https://example.com/api/test"
    }
    
    scraper = AuthenticatedScraper("https://example.com", config)
    
    if scraper.authenticate():
        print("Authentication successful!")
        
        # Fetch a page
        content = scraper.fetch_page("https://example.com/protected-data")
        
        if content:
            print("Data fetched successfully")
            # Process data...
    else:
        print("Authentication failed")


if __name__ == "__main__":
    main()
