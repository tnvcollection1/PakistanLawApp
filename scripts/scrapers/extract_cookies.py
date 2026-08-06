#!/usr/bin/env python3
"""
Extract cookies from a browser session for authenticated scraping.
"""
import json
import os
from pathlib import Path

COOKIE_FILE = Path.home() / ".pakistanlaw_cookies.json"


def save_cookies(cookies_dict):
    """Save cookies to file."""
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies_dict, f, indent=2)
    print(f"Cookies saved to {COOKIE_FILE}")


def load_cookies():
    """Load cookies from file."""
    if COOKIE_FILE.exists():
        with open(COOKIE_FILE) as f:
            return json.load(f)
    return {}


def extract_from_headers(headers):
    """Extract cookie values from HTTP response headers."""
    cookie_header = headers.get("Set-Cookie", "")
    cookies = {}
    for cookie in cookie_header.split(";"):
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value
    return cookies


def main():
    """Interactive cookie extraction."""
    print("Paste your cookies (JSON format) or browser cookie string:")
    user_input = input("> ")
    try:
        cookies = json.loads(user_input)
        save_cookies(cookies)
    except json.JSONDecodeError:
        print("Trying to parse as cookie string...")
        cookies = {}
        for pair in user_input.split(";"):
            if "=" in pair:
                key, value = pair.strip().split("=", 1)
                cookies[key] = value
        save_cookies(cookies)


if __name__ == "__main__":
    main()
