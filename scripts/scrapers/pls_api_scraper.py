#!/usr/bin/env python3
"""Scraper for PLS API endpoints."""

import requests
import json
import os
import sys

BASE_URL = os.environ.get("PLS_API_URL", "https://api.pakistanlawsite.com")
API_KEY = os.environ.get("PLS_API_KEY", "")


def get_headers():
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def fetch_cases(limit=100, offset=0):
    url = f"{BASE_URL}/cases"
    params = {"limit": limit, "offset": offset}
    resp = requests.get(url, params=params, headers=get_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    try:
        cases = fetch_cases(limit=50)
        print(json.dumps(cases, indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cases: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
