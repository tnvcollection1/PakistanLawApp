#!/usr/bin/env python3
"""
mac_dual_scraper.py
Dual-threaded MAC (Ministry of Law & Justice) scraper for PAKISTAN LEGAL SCALES.
One thread fetches cases; the second thread parses headnotes + metadata.
"""

import os, sys, re, json, time, logging, requests, concurrent.futures
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_URL = "https://www.moal.gov.pk/judgments-search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "scraped_data", "mac")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ────────────────────────────────────── fetcher

def fetch_page(url, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                return r.text
            logging.warning(f"HTTP {r.status_code} for {url}")
        except Exception as e:
            logging.warning(f"Attempt {attempt+1} failed for {url}: {e}")
        time.sleep(2 ** attempt)
    return None

# ────────────────────────────────────── parser

def parse_case_page(html):
    soup = BeautifulSoup(html, "html.parser")
    data = {
        "title": None,
        "case_number": None,
        "date": None,
        "court": None,
        "bench": None,
        "parties": None,
        "headnote": None,
        "full_text": None,
        "citations": [],
        "referred_cases": [],
    }

    # Title
    title_tag = soup.find("h1") or soup.find("h2")
    if title_tag:
        data["title"] = title_tag.get_text(strip=True)

    # Meta table
    for row in soup.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            label = tds[0].get_text(strip=True).lower()
            val = tds[1].get_text(strip=True)
            if "case number" in label:
                data["case_number"] = val
            elif "date" in label and "decision" in label:
                data["date"] = val
            elif "court" in label:
                data["court"] = val
            elif "bench" in label:
                data["bench"] = val
            elif "parties" in label:
                data["parties"] = val

    # Headnote (look for bold/heading "Headnote" or "Summary")
    for h in soup.find_all(["h3", "h4", "strong", "b"]):
        txt = h.get_text(strip=True).lower()
        if "headnote" in txt or "summary" in txt:
            nxt = h.find_next_sibling()
            if nxt:
                data["headnote"] = nxt.get_text(strip=True)
            break

    # Full text: grab everything after a likely heading
    full_text_parts = []
    started = False
    for elem in soup.find_all(["p", "div"]):
        if started:
            txt = elem.get_text(strip=True)
            if txt:
                full_text_parts.append(txt)
        txt = elem.get_text(strip=True).lower()
        if "judgment" in txt and len(txt) < 50:
            started = True
    if full_text_parts:
        data["full_text"] = "\n\n".join(full_text_parts)

    # Citations
    cite_pattern = re.compile(r"(\d{4}\s+\w+\s+\d+.*?)(?=\n|$)", re.IGNORECASE)
    text = soup.get_text()
    for m in cite_pattern.finditer(text):
        data["citations"].append(m.group(1).strip())

    return data

# ────────────────────────────────────── dual-threaded pipeline

class DualScraper:
    def __init__(self, start_page=1, max_pages=5):
        self.start_page = start_page
        self.max_pages = max_pages
        self.case_urls = []
        self.results = []

    def fetch_listing_page(self, page_num):
        """Fetch a listing page and extract case URLs."""
        url = f"{BASE_URL}?page={page_num}"
        html = fetch_page(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/judgment/" in href or "/case/" in href:
                if href.startswith("http"):
                    urls.append(href)
                else:
                    urls.append(f"https://www.moal.gov.pk{href}")
        # Deduplicate
        seen = set()
        unique = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique.append(u)
        return unique

    def fetch_and_parse(self, url):
        html = fetch_page(url)
        if not html:
            return None
        return parse_case_page(html)

    def run(self):
        logging.info(f"Starting dual scraper: pages {self.start_page} to {self.start_page + self.max_pages - 1}")

        # Phase 1: collect URLs (single-threaded for simplicity)
        for p in range(self.start_page, self.start_page + self.max_pages):
            logging.info(f"Fetching listing page {p}...")
            urls = self.fetch_listing_page(p)
            self.case_urls.extend(urls)
            logging.info(f"  Found {len(urls)} case URLs")
            time.sleep(1)

        logging.info(f"Total case URLs collected: {len(self.case_urls)}")

        # Phase 2: dual-threaded fetch + parse
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_url = {executor.submit(self.fetch_and_parse, url): url for url in self.case_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        result["source_url"] = url
                        result["scraped_at"] = datetime.now().isoformat()
                        self.results.append(result)
                except Exception as e:
                    logging.error(f"Error processing {url}: {e}")

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(OUTPUT_DIR, f"mac_cases_{timestamp}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved {len(self.results)} cases to {out_path}")

        return self.results

if __name__ == "__main__":
    scraper = DualScraper(start_page=1, max_pages=3)
    scraper.run()
