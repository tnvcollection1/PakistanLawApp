#!/usr/bin/env python3
"""
DigiLawyer Scraper - Run this from your LOCAL machine (not cloud server).

DigiLawyer (pro.digilawyer.org) uses Vercel bot protection that blocks
cloud/server IPs. This script must be run from a residential IP.

Prerequisites:
    pip install httpx beautifulsoup4 pymongo

Usage:
    python digilawyer_scraper.py --email metalik.studio@gmail.com --password Metalik345!
    python digilawyer_scraper.py --mode discover --start-id 1 --end-id 500
    python digilawyer_scraper.py --mode import --file judgements.json --mongo-url mongodb://...

URL Pattern:
    https://pro.digilawyer.org/judgement/JD-{YEAR}-DIG-{NUMBER}-{HASH}

Data Structure (from HAR analysis):
    {
        "id": 24032,
        "identifier": "JD-2024-DIG-132-f9b5",
        "documentId": "1ca9d4ccb7f54365b2f12b603ca422e2",
        "selfCitation": "2024 PLC(CS) 529",
        "judges": "Honorable Justice Safdar Saleem Shahid",
        "advocates": "Saif ul Haq Ziay, Sikandar Azam",
        "court": "Lahore High Court",
        "whoVsWho": "Mst. KAUSAR KHATOON VS INSPECTOR GENERAL OF POLICE",
        "date": "2024-01-01",
        "caseText": "<html content>",
        "sections": [{"sectionId": "...", "statuteId": "..."}]
    }
"""

import httpx
import json
import time
import re
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://pro.digilawyer.org"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# Output directory
OUTPUT_DIR = Path("digilawyer_data")


class DigiLawyerScraper:
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.client = httpx.Client(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": UA},
        )
        self.session_cookie = None
        self.clerk_token = None

    def login(self):
        """Login via Clerk authentication."""
        logger.info("Attempting DigiLawyer login...")

        # Step 1: Hit homepage to get Clerk configuration
        r = self.client.get(BASE_URL)
        if r.status_code == 429:
            logger.error(
                "BLOCKED by Vercel bot protection (429). "
                "You must run this from a residential IP, not a cloud server."
            )
            return False

        # Step 2: Clerk sign-in
        # DigiLawyer uses Clerk (clerk.digilawyer.org) for auth
        clerk_url = "https://clerk.digilawyer.org"

        # Get Clerk environment
        r_env = self.client.get(f"{clerk_url}/v1/environment")
        if r_env.status_code != 200:
            logger.error(f"Clerk environment failed: {r_env.status_code}")
            return False

        # Create sign-in
        r_signin = self.client.post(
            f"{clerk_url}/v1/client/sign_ins",
            json={
                "identifier": self.email,
                "password": self.password,
                "strategy": "password",
            },
            headers={"Origin": BASE_URL, "Referer": f"{BASE_URL}/"},
        )

        if r_signin.status_code == 200:
            data = r_signin.json()
            sessions = data.get("client", {}).get("sessions", [])
            if sessions:
                token = sessions[0].get("last_active_token", {}).get("jwt")
                if token:
                    self.clerk_token = token
                    logger.info("Login successful!")
                    return True

        logger.error(f"Login failed: {r_signin.status_code}")
        logger.error(
            "Try signing in manually at https://pro.digilawyer.org, "
            "then extract cookies from browser DevTools."
        )
        return False

    def set_cookie(self, cookie_string):
        """Manually set session cookie from browser."""
        self.session_cookie = cookie_string
        self.client.headers["Cookie"] = cookie_string
        logger.info("Cookie set manually")

    def fetch_judgement_page(self, identifier):
        """Fetch a judgement page and extract data from Next.js RSC."""
        url = f"{BASE_URL}/judgement/{identifier}"

        headers = {"User-Agent": UA, "Accept": "text/html"}
        if self.clerk_token:
            headers["Authorization"] = f"Bearer {self.clerk_token}"

        try:
            r = self.client.get(url, headers=headers)
            if r.status_code == 429:
                logger.warning(f"Rate limited on {identifier}, waiting 10s...")
                time.sleep(10)
                return None
            if r.status_code == 404:
                return None
            if r.status_code != 200:
                logger.warning(f"HTTP {r.status_code} for {identifier}")
                return None

            html = r.text

            # Extract judgement data from RSC flight format
            judgement_data = self._extract_rsc_data(html, identifier)
            return judgement_data

        except Exception as e:
            logger.error(f"Error fetching {identifier}: {e}")
            return None

    def _extract_rsc_data(self, html, identifier):
        """Extract judgement data from Next.js RSC stream in HTML."""
        data = {"identifier": identifier, "raw_html_length": len(html)}

        # Find escaped JSON with judgement data
        match = re.search(
            r'\\"judgement\\":\{(.*?)\}(?:,\\"|\})', html, re.DOTALL
        )
        if match:
            raw = match.group(1)
            unescaped = raw.replace('\\"', '"').replace("\\\\", "\\")

            # Extract individual fields
            fields = {
                "id": r'"id":(\d+)',
                "identifier": r'"identifier":"([^"]+)"',
                "documentId": r'"documentId":"([^"]+)"',
                "selfCitation": r'"selfCitation":"([^"]+)"',
                "judges": r'"judges":"([^"]+)"',
                "advocates": r'"advocates":"([^"]+)"',
                "court": r'"court":"([^"]+)"',
                "whoVsWho": r'"whoVsWho":"([^"]+)"',
                "date": r'"date":"([^"]+)"',
                "afrNr": r'"afrNr":(true|false)',
            }

            for field, pattern in fields.items():
                m = re.search(pattern, unescaped)
                if m:
                    val = m.group(1)
                    if field == "id":
                        val = int(val)
                    elif field == "afrNr":
                        val = val == "true"
                    data[field] = val

        # Also try to extract case text from RSC chunks
        # Case text is typically in a separate RSC chunk
        text_matches = re.findall(
            r'self\.__next_f\.push\(\[.*?"([^"]{500,})"', html
        )
        if text_matches:
            # The longest match is likely the case text
            longest = max(text_matches, key=len)
            data["case_text_length"] = len(longest)
            data["case_text_preview"] = longest[:500]

        return data if len(data) > 2 else None

    def discover_judgements(self, start_id=1, end_id=500, year=2024):
        """Discover judgement URLs by iterating through IDs."""
        logger.info(f"Discovering judgements: IDs {start_id}-{end_id}, year={year}")

        found = []
        consecutive_misses = 0

        for num in range(start_id, end_id + 1):
            # Try common hash patterns
            # The hash suffix is 4 hex chars, we can't predict it
            # But we can try fetching the listing page instead

            # Try without hash first (some sites redirect)
            test_url = f"{BASE_URL}/judgement/JD-{year}-DIG-{num}"
            try:
                r = self.client.get(
                    test_url,
                    headers={"User-Agent": UA},
                    follow_redirects=True,
                )

                if r.status_code == 200 and "judgement" in r.text.lower():
                    # Extract the full identifier from the page
                    id_match = re.search(
                        r"JD-\d{4}-[A-Z]+-\d+-[a-f0-9]+", r.text
                    )
                    if id_match:
                        full_id = id_match.group(0)
                        data = self._extract_rsc_data(r.text, full_id)
                        if data and data.get("selfCitation"):
                            found.append(data)
                            consecutive_misses = 0
                            logger.info(
                                f"  Found #{num}: {data.get('selfCitation')} - "
                                f"{data.get('court')} - {data.get('whoVsWho', '')[:50]}"
                            )
                elif r.status_code == 429:
                    logger.warning("Rate limited, waiting 15s...")
                    time.sleep(15)
                    continue
                else:
                    consecutive_misses += 1

            except Exception as e:
                logger.error(f"Error on #{num}: {e}")
                consecutive_misses += 1

            # Save progress periodically
            if len(found) % 10 == 0 and found:
                self._save_progress(found, year)

            # Stop after too many consecutive misses
            if consecutive_misses > 20:
                logger.info(f"Stopping after {consecutive_misses} consecutive misses")
                break

            time.sleep(1)  # Rate limit

        self._save_progress(found, year)
        return found

    def scrape_from_listing(self, page=1, per_page=20):
        """Try to scrape from DigiLawyer's listing/search API."""
        # Common tRPC patterns for Next.js apps
        endpoints = [
            f"{BASE_URL}/api/trpc/judgement.getAll?input=%7B%22page%22%3A{page}%2C%22perPage%22%3A{per_page}%7D",
            f"{BASE_URL}/api/trpc/judgement.search?input=%7B%22query%22%3A%22%22%2C%22page%22%3A{page}%7D",
            f"{BASE_URL}/api/judgements?page={page}&limit={per_page}",
        ]

        headers = {"User-Agent": UA, "Accept": "application/json"}
        if self.clerk_token:
            headers["Authorization"] = f"Bearer {self.clerk_token}"

        for endpoint in endpoints:
            try:
                r = self.client.get(endpoint, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    logger.info(f"Listing API found: {endpoint}")
                    return data
            except Exception:
                continue

        logger.warning("No listing API found")
        return None

    def _save_progress(self, data, year):
        """Save discovered judgements to file."""
        OUTPUT_DIR.mkdir(exist_ok=True)
        filepath = OUTPUT_DIR / f"judgements_{year}.json"
        with open(filepath, "w") as f:
            json.dump(
                {
                    "scraped_at": datetime.now().isoformat(),
                    "count": len(data),
                    "judgements": data,
                },
                f,
                indent=2,
            )
        logger.info(f"Saved {len(data)} judgements to {filepath}")

    def close(self):
        self.client.close()


def import_to_mongodb(json_file, mongo_url, db_name="pakistan_law"):
    """Import scraped judgements into MongoDB."""
    from pymongo import MongoClient

    with open(json_file) as f:
        data = json.load(f)

    client = MongoClient(mongo_url)
    db = client[db_name]
    collection = db.pls_caselaws

    imported = 0
    skipped = 0

    for j in data.get("judgements", []):
        citation = j.get("selfCitation", "")
        if not citation:
            continue

        # Check if already exists
        existing = collection.find_one({"citation": citation})
        if existing:
            skipped += 1
            continue

        # Parse citation for year and journal
        cite_match = re.match(r"(\d{4})\s+([A-Z()]+)\s+(\d+)", citation)
        year = int(cite_match.group(1)) if cite_match else None
        journal = cite_match.group(2) if cite_match else None

        doc = {
            "case_id": j.get("identifier", ""),
            "citation": citation,
            "court": j.get("court", ""),
            "year": year,
            "journal": journal,
            "judge": j.get("judges", ""),
            "lawyers": j.get("advocates", ""),
            "petitioner": j.get("whoVsWho", "").split(" VS ")[0].strip()
            if " VS " in j.get("whoVsWho", "")
            else "",
            "respondent": j.get("whoVsWho", "").split(" VS ")[1].strip()
            if " VS " in j.get("whoVsWho", "")
            else "",
            "full_content": j.get("case_text_preview", ""),
            "source": "digilawyer",
            "digilawyer_id": j.get("id"),
            "digilawyer_doc_id": j.get("documentId"),
            "scraped_at": datetime.now().isoformat(),
        }

        collection.insert_one(doc)
        imported += 1

    logger.info(f"Import complete: {imported} imported, {skipped} skipped (already exist)")
    client.close()


def main():
    parser = argparse.ArgumentParser(description="DigiLawyer Scraper")
    parser.add_argument("--email", type=str, help="DigiLawyer email")
    parser.add_argument("--password", type=str, help="DigiLawyer password")
    parser.add_argument("--cookie", type=str, help="Browser cookie string (manual)")
    parser.add_argument(
        "--mode",
        choices=["discover", "single", "listing", "import"],
        default="discover",
    )
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--end-id", type=int, default=500)
    parser.add_argument("--identifier", type=str, help="Single judgement ID")
    parser.add_argument("--file", type=str, help="JSON file for import")
    parser.add_argument("--mongo-url", type=str, help="MongoDB URL for import")
    parser.add_argument("--db-name", type=str, default="pakistan_law")

    args = parser.parse_args()

    if args.mode == "import":
        if not args.file or not args.mongo_url:
            print("Import requires --file and --mongo-url")
            sys.exit(1)
        import_to_mongodb(args.file, args.mongo_url, args.db_name)
        return

    scraper = DigiLawyerScraper(email=args.email, password=args.password)

    # Set cookie if provided
    if args.cookie:
        scraper.set_cookie(args.cookie)
    elif args.email and args.password:
        if not scraper.login():
            logger.error("Login failed. Try providing --cookie instead.")
            logger.info(
                "To get cookie: Open browser DevTools > Network tab > "
                "Copy 'Cookie' header from any request to pro.digilawyer.org"
            )
            scraper.close()
            sys.exit(1)

    try:
        if args.mode == "single":
            if not args.identifier:
                print("Single mode requires --identifier (e.g. JD-2024-DIG-132-f9b5)")
                sys.exit(1)
            data = scraper.fetch_judgement_page(args.identifier)
            if data:
                print(json.dumps(data, indent=2))
            else:
                print("No data found")

        elif args.mode == "discover":
            found = scraper.discover_judgements(
                start_id=args.start_id, end_id=args.end_id, year=args.year
            )
            print(f"\nDiscovered {len(found)} judgements")

        elif args.mode == "listing":
            data = scraper.scrape_from_listing()
            if data:
                print(json.dumps(data, indent=2)[:2000])

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
