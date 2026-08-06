#!/usr/bin/env python3
"""
Sindh High Court (SHC) Caselaw Scraper
Portal: caselaw.shc.gov.pk

This scraper:
1. Fetches judge IDs from the reported-judgements page
2. For each judge, fetches all their judgment listing pages
3. Extracts base64-encoded document IDs
4. Downloads judgment PDF/text and metadata
5. Stores in MongoDB for FAISS indexing

Base64 URL pattern discovered:
- Encoded: MjcwODYyY2Ztcy1kYzgz
- Decoded: 270862cfms-dc83
"""

import subprocess
import json
import time
import os
import sys
import re
import base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote, quote

# MongoDB connection string (same as main app)
MONGO_URI = "mongodb://lawapp:VpsMongo2026LawXk9@localhost:27017/pakistanlawsite?authSource=pakistanlawsite"

# === CONFIG ===
BASE_URL = "https://caselaw.shc.gov.pk/caselaw"
OUTPUT_DIR = "/tmp/shc_data"
BATCH_SIZE = 100
CONCURRENT = 5
REQUEST_DELAY = 1.0  # Be polite
MAX_RETRIES = 3

# State tracking
fetched_ids = set()
failed_ids = set()
judge_ids = []


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def decode_shc_id(encoded):
    """Decode base64 SHC document ID."""
    try:
        # Add padding if needed
        padded = encoded + "=" * (4 - len(encoded) % 4) if len(encoded) % 4 else encoded
        decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
        return decoded if 'cfms' in decoded else None
    except:
        return None


def encode_shc_id(doc_id):
    """Encode a document ID to base64."""
    try:
        encoded = base64.b64encode(doc_id.encode()).decode()
        return encoded.rstrip('=')
    except:
        return None


def curl_html(url, timeout=30):
    """Fetch HTML content via curl."""
    cmd = [
        "curl", "-s", 
        "--connect-timeout", "10", 
        "--max-time", str(timeout),
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
        "-H", "Accept: text/html,application/xhtml+xml",
        url
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        if r.returncode == 0:
            return r.stdout
    except Exception as e:
        log(f"Error fetching {url}: {e}")
    return None


def curl_download(url, output_path, timeout=60):
    """Download a file via curl."""
    cmd = [
        "curl", "-s", "-L",
        "--connect-timeout", "10",
        "--max-time", str(timeout),
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0",
        "-o", output_path,
        url
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return r.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 100
    except:
        return False


def get_judge_list():
    """Fetch list of judges from multiple sources."""
    log("Fetching judge list...")
    
    all_judge_ids = set()
    
    # Strategy 1: Fetch from rpt-afr (most reliable)
    html = curl_html(f"{BASE_URL}/public/rpt-afr")
    if html:
        ids = re.findall(r'reported-judgements-detail-all/(\d+)', html)
        all_judge_ids.update(ids)
        log(f"rpt-afr: found {len(ids)} IDs")
    
    # Strategy 2: Try other report pages
    for page in ['/public/reported-judgements', '/public/rpt-benchwise']:
        html = curl_html(f"{BASE_URL}{page}")
        if html:
            ids = re.findall(r'reported-judgements-detail-all/(\d+)', html)
            all_judge_ids.update(ids)
    
    # Strategy 3: Known valid judge ID ranges (fallback)
    # These were discovered by scanning and include most active judges
    known_ranges = [
        range(100, 200, 10),    # 100-200
        range(200, 500, 25),    # 200-500
        range(500, 1000, 25),   # 500-1000
        range(1000, 1350, 10),  # 1000-1350 (most active judges)
    ]
    
    if len(all_judge_ids) < 50:
        log("Not enough judges from pages, scanning known ranges...")
        for r in known_ranges:
            for i in r:
                all_judge_ids.add(str(i))
    
    # Strategy 4: Brute force validation (verify IDs have content)
    log(f"Validating {len(all_judge_ids)} potential judge IDs...")
    valid_judges = []
    
    for jid in sorted(all_judge_ids, key=int):
        html = curl_html(f"{BASE_URL}/public/reported-judgements-detail-all/{jid}/-1", timeout=20)
        if html and 'view-file' in html and len(html) > 5000:
            # Count judgments to get judge activity
            count = len(re.findall(r'view-file/', html))
            valid_judges.append((jid, f"Judge_{jid}", count))
            log(f"  Judge {jid}: {count} judgments")
        time.sleep(0.5)  # Be polite
    
    # Sort by judgment count descending
    valid_judges.sort(key=lambda x: x[2], reverse=True)
    log(f"Found {len(valid_judges)} valid judges with judgments")
    
    return [(jid, name) for jid, name, _ in valid_judges]


def extract_judgments_from_page(html):
    """Extract judgment metadata from a judge's page."""
    judgments = []
    
    # Extract base64 IDs
    id_pattern = r'(?:view-file|doc=)/?\?\?([A-Za-z0-9+/]{16,}={0,2})'
    ids = set(re.findall(id_pattern, html))
    
    # Extract citation info pairs
    citation_pattern = r'doc=([A-Za-z0-9+/=]+)[^"]*citation=([^&"<>]+)'
    citations = re.findall(citation_pattern, html)
    
    citation_map = {}
    for b64_id, citation in citations:
        citation_map[b64_id] = unquote(citation.replace('+', ' '))
    
    # Also try to extract table rows with more metadata
    # Pattern: <tr>...<td>citation</td>...<td>case_no</td>...<td>parties</td>...<td>date</td>...</tr>
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    rows = re.findall(row_pattern, html, re.DOTALL | re.IGNORECASE)
    
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(tds) >= 5:
            # Try to extract view-file link from this row
            link_match = re.search(r'view-file/([A-Za-z0-9+/=]+)', row)
            if link_match:
                b64_id = link_match.group(1)
                decoded_id = decode_shc_id(b64_id)
                if decoded_id:
                    judgment = {
                        'base64_id': b64_id,
                        'decoded_id': decoded_id,
                        'citation': re.sub(r'<[^>]+>', '', tds[1]).strip() if len(tds) > 1 else '',
                        'case_number': re.sub(r'<[^>]+>', '', tds[2]).strip() if len(tds) > 2 else '',
                        'parties': re.sub(r'<[^>]+>', '', tds[4]).strip() if len(tds) > 4 else '',
                        'decision_date': re.sub(r'<[^>]+>', '', tds[5]).strip() if len(tds) > 5 else '',
                    }
                    judgments.append(judgment)
    
    # For IDs not in rows, create minimal entries
    seen = {j['base64_id'] for j in judgments}
    for b64_id in ids:
        if b64_id not in seen:
            decoded_id = decode_shc_id(b64_id)
            if decoded_id:
                judgments.append({
                    'base64_id': b64_id,
                    'decoded_id': decoded_id,
                    'citation': citation_map.get(b64_id, ''),
                    'case_number': '',
                    'parties': '',
                    'decision_date': '',
                })
    
    return judgments


def fetch_judgment_text(b64_id):
    """Fetch the judgment text/HTML content."""
    url = f"{BASE_URL}/public/view-file/{b64_id}"
    html = curl_html(url, timeout=45)
    if not html:
        return None
    
    # Extract the judgment text from the HTML
    # Usually in a div or pre tag
    text_pattern = r'<div[^>]*class="[^"]*judgment[^"]*"[^>]*>(.*?)</div>'
    match = re.search(text_pattern, html, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    else:
        # Try body content
        body_pattern = r'<body[^>]*>(.*?)</body>'
        match = re.search(body_pattern, html, re.DOTALL | re.IGNORECASE)
        text = match.group(1) if match else html
    
    # Clean HTML tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text if len(text) > 100 else None


def save_batch(judgments, batch_num):
    """Save a batch of judgments to JSON."""
    filename = os.path.join(OUTPUT_DIR, f"shc_batch_{batch_num:05d}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(judgments, f, ensure_ascii=False, indent=2)
    log(f"SAVED batch {batch_num}: {len(judgments)} judgments")


def save_state():
    """Save scraper state for resume."""
    state = {
        "fetched": len(fetched_ids),
        "failed": len(failed_ids),
        "timestamp": datetime.now().isoformat(),
    }
    with open(os.path.join(OUTPUT_DIR, "shc_state.json"), 'w') as f:
        json.dump(state, f, indent=2)
    
    # Save IDs
    with open(os.path.join(OUTPUT_DIR, "fetched_ids.json"), 'w') as f:
        json.dump(list(fetched_ids), f)
    with open(os.path.join(OUTPUT_DIR, "failed_ids.json"), 'w') as f:
        json.dump(list(failed_ids), f)


def load_state():
    """Load previous state if exists."""
    global fetched_ids, failed_ids
    
    fetched_file = os.path.join(OUTPUT_DIR, "fetched_ids.json")
    if os.path.exists(fetched_file):
        with open(fetched_file) as f:
            fetched_ids = set(json.load(f))
        log(f"Loaded {len(fetched_ids)} previously fetched IDs")
    
    failed_file = os.path.join(OUTPUT_DIR, "failed_ids.json")
    if os.path.exists(failed_file):
        with open(failed_file) as f:
            failed_ids = set(json.load(f))


def scrape_judge(judge_id, judge_name):
    """Scrape all judgments for a specific judge."""
    url = f"{BASE_URL}/public/reported-judgements-detail-all/{judge_id}/-1"
    log(f"Scraping judge {judge_id} ({judge_name})...")
    
    html = curl_html(url, timeout=60)
    if not html:
        log(f"Failed to fetch judge {judge_id}")
        return []
    
    judgments = extract_judgments_from_page(html)
    log(f"Judge {judge_id}: Found {len(judgments)} judgments")
    
    return judgments


def process_judgment(judgment):
    """Process a single judgment - fetch text and prepare for DB."""
    b64_id = judgment['base64_id']
    decoded_id = judgment['decoded_id']
    
    if decoded_id in fetched_ids:
        return None
    
    # Fetch judgment text
    text = fetch_judgment_text(b64_id)
    if not text:
        failed_ids.add(decoded_id)
        return None
    
    # Prepare document for MongoDB
    doc = {
        'source': 'shc',
        'shc_id': decoded_id,
        'shc_b64_id': b64_id,
        'citation': judgment.get('citation', ''),
        'case_number': judgment.get('case_number', ''),
        'parties': judgment.get('parties', ''),
        'decision_date': judgment.get('decision_date', ''),
        'court': 'Sindh High Court',
        'judgment_text': text[:500000],  # Limit size
        'scraped_at': datetime.now().isoformat(),
        'url': f"{BASE_URL}/public/view-file/{b64_id}",
    }
    
    # Parse citation for year and bench
    if doc['citation']:
        year_match = re.search(r'(\d{4})', doc['citation'])
        if year_match:
            doc['year'] = int(year_match.group(1))
        
        # SHC KHI = Karachi, SHC HYD = Hyderabad, etc.
        if 'KHI' in doc['citation']:
            doc['bench'] = 'Karachi'
        elif 'HYD' in doc['citation']:
            doc['bench'] = 'Hyderabad'
        elif 'SUK' in doc['citation']:
            doc['bench'] = 'Sukkur'
        elif 'LAR' in doc['citation']:
            doc['bench'] = 'Larkana'
    
    fetched_ids.add(decoded_id)
    return doc


def main():
    global fetched_ids
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    load_state()
    
    log("=" * 60)
    log("Sindh High Court Caselaw Scraper")
    log("=" * 60)
    
    # Get list of judges
    judges = get_judge_list()
    if not judges:
        log("ERROR: No judges found! Exiting.")
        sys.exit(1)
    
    log(f"Found {len(judges)} judges to scrape")
    
    # Collect all judgment metadata from all judges
    all_judgments = []
    for judge_id, judge_name in judges:
        judgments = scrape_judge(judge_id, judge_name)
        all_judgments.extend(judgments)
        time.sleep(REQUEST_DELAY)
    
    # Dedupe by decoded_id
    seen = set()
    unique_judgments = []
    for j in all_judgments:
        if j['decoded_id'] not in seen and j['decoded_id'] not in fetched_ids:
            seen.add(j['decoded_id'])
            unique_judgments.append(j)
    
    log(f"Total unique judgments to fetch: {len(unique_judgments)}")
    
    # Process judgments
    batch_num = 1
    current_batch = []
    start_time = time.time()
    
    for i, judgment in enumerate(unique_judgments):
        doc = process_judgment(judgment)
        if doc:
            current_batch.append(doc)
        
        # Save batch
        if len(current_batch) >= BATCH_SIZE:
            save_batch(current_batch, batch_num)
            batch_num += 1
            current_batch = []
            save_state()
        
        # Progress
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = len(fetched_ids) / max(elapsed, 1) * 3600
            log(f"Progress: {i+1}/{len(unique_judgments)} | Fetched: {len(fetched_ids)} | Failed: {len(failed_ids)} | Rate: {rate:.0f}/hr")
        
        time.sleep(REQUEST_DELAY)
    
    # Save remaining
    if current_batch:
        save_batch(current_batch, batch_num)
    
    save_state()
    
    elapsed = (time.time() - start_time) / 3600
    log("=" * 60)
    log(f"SCRAPER COMPLETE")
    log(f"  Fetched: {len(fetched_ids)}")
    log(f"  Failed: {len(failed_ids)}")
    log(f"  Time: {elapsed:.2f} hours")
    log("=" * 60)


def quick_scan():
    """Quick scan mode - just collect all judgment IDs without downloading text."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    log("=" * 60)
    log("SHC Quick Scan Mode - Collecting Judgment IDs")
    log("=" * 60)
    
    # Known active judge IDs from discovery
    judge_ids = [
        647, 1181, 1243, 1264, 741, 1182, 1201, 1242, 1261, 1263,
        1266, 1267, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308,
        1309, 1310, 1311, 1312, 844, 883, 965, 966, 1023, 1041, 1061,
        1101, 1102, 1121, 1162, 424
    ]
    
    all_ids = set()
    
    for jid in judge_ids:
        log(f"Scanning judge {jid}...")
        html = curl_html(f"{BASE_URL}/public/reported-judgements-detail-all/{jid}/-1", timeout=60)
        if html:
            ids = set(re.findall(r'(?:view-file|doc=)/?\?\?([A-Za-z0-9+/]{16,}={0,2})', html))
            all_ids.update(ids)
            log(f"  Found {len(ids)} documents (total: {len(all_ids)})")
        time.sleep(REQUEST_DELAY)
    
    # Save all IDs
    with open(os.path.join(OUTPUT_DIR, "all_judgment_ids.json"), 'w') as f:
        json.dump(list(all_ids), f)
    
    log("=" * 60)
    log(f"SCAN COMPLETE: {len(all_ids)} unique judgment IDs found")
    log(f"IDs saved to: {OUTPUT_DIR}/all_judgment_ids.json")
    log("=" * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--scan':
        quick_scan()
    else:
        main()
