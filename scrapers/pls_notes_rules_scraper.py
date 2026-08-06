#!/usr/bin/env python3
"""Scraper for PLS notes and rules data."""

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


def fetch_notes(case_id):
    url = f"{BASE_URL}/cases/{case_id}/notes"
    resp = requests.get(url, headers=get_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_rules(limit=100):
    url = f"{BASE_URL}/rules"
    params = {"limit": limit}
    resp = requests.get(url, params=params, headers=get_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    try:
        rules = fetch_rules(limit=50)
        print(json.dumps(rules, indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rules: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
