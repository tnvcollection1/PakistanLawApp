#!/usr/bin/env python3
"""
PLS Content Fetcher - Fetches full text content from PLS case pages.
"""
import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://beta.pakistanlawsite.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_case_content(case_id):
    """Fetch full text content for a specific case."""
    url = f"{BASE_URL}/case/{case_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching case {case_id}: {e}")
        return None


def parse_case_content(html):
    """Parse case HTML and extract structured content."""
    soup = BeautifulSoup(html, "html.parser")
    content = {
        "title": None,
        "date": None,
        "court": None,
        "judgment_text": None,
        "headnote": None,
        "citation": None,
    }
    title_elem = soup.find("h1", class_="case-title")
    if title_elem:
        content["title"] = title_elem.get_text(strip=True)
    date_elem = soup.find("span", class_="case-date")
    if date_elem:
        content["date"] = date_elem.get_text(strip=True)
    court_elem = soup.find("span", class_="case-court")
    if court_elem:
        content["court"] = court_elem.get_text(strip=True)
    text_elem = soup.find("div", class_="judgment-text")
    if text_elem:
        content["judgment_text"] = text_elem.get_text(separator="\n", strip=True)
    headnote_elem = soup.find("div", class_="headnote")
    if headnote_elem:
        content["headnote"] = headnote_elem.get_text(strip=True)
    citation_elem = soup.find("span", class_="citation")
    if citation_elem:
        content["citation"] = citation_elem.get_text(strip=True)
    return content


def fetch_and_parse(case_id):
    """Fetch and parse a case in one step."""
    html = fetch_case_content(case_id)
    if html:
        return parse_case_content(html)
    return None


if __name__ == "__main__":
    case_id = "example-case-123"
    result = fetch_and_parse(case_id)
    if result:
        print(f"Title: {result['title']}")
        print(f"Date: {result['date']}")
        print(f"Court: {result['court']}")
        print(f"Text length: {len(result['judgment_text'] or '')}")
    else:
        print("Failed to fetch case")
