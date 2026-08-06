"""PLSBeta Unified Scraper v2 — Auto-Login & Cookie Refresh

Features: Auto-login with retry, session refresh, resume, concurrency, MongoDB writes.
Supports: case IDs, case content, statutes, terms, words, maxims.
"""

import asyncio, httpx, re, os, json, signal, argparse, logging
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

import sys
sys.path.insert(0, str(Path(__file__).parent))
from plsbeta_auth import PLSBetaAuth

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://www.plsbeta.com/LawOnline/law"
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
PROGRESS_DIR = Path(__file__).parent / "progress"
PROGRESS_DIR.mkdir(exist_ok=True)

CONCURRENCY = 3
BATCH_SIZE = 20
DELAY_BETWEEN_BATCHES = 1.0

stop_requested = False


def handle_signal(sig, frame):
    global stop_requested
    stop_requested = True
    logger.warning("STOP signal received, finishing current batch...")


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


class PLSBetaScraperV2:
    def __init__(self, concurrency=CONCURRENCY):
        self.auth = PLSBetaAuth()
        self.db = None
        self.http_client = None
        self.concurrency = concurrency
        self.stats = {'ids_discovered': 0, 'content_fetched': 0, 'empty': 0, 'errors': 0, 'relogins': 0}
        self.start_time = None
        self._relogin_lock = asyncio.Lock()

    async def init(self):
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'pakistanlawsite')
        client = AsyncIOMotorClient(mongo_url)
        self.db = client[db_name]
        self.http_client = httpx.AsyncClient(timeout=30, follow_redirects=True)
        success = await self.auth.login_with_retry(self.http_client, max_retries=3, wait_minutes=5)
        if not success:
            raise RuntimeError("PLSBeta login failed after retries. Close any browser tabs with plsbeta.com, wait 5 minutes, try again.")
        self.start_time = datetime.now()
        logger.info("PLSBeta Scraper v2 initialized")

    async def _relogin(self):
        async with self._relogin_lock:
            self.stats['relogins'] += 1
            logger.warning(f"Session expired, re-authenticating (#{self.stats['relogins']})...")
            success = await self.auth.login_with_client(self.http_client)
            if not success:
                success = await self.auth.login_with_retry(self.http_client, max_retries=2, wait_minutes=5)
            return success

    async def _get_with_refresh(self, url, max_retries=2):
        for attempt in range(max_retries + 1):
            try:
                r = await self.http_client.get(url, headers={'User-Agent': UA})
                if not self.auth.is_session_expired(r): return r
                if attempt < max_retries:
                    await self._relogin(); await asyncio.sleep(2); continue
                return None
            except httpx.TimeoutException:
                if attempt < max_retries: await asyncio.sleep(2); continue
                return None
            except Exception as e:
                logger.error(f"Request error: {e}"); return None
        return None

    async def close(self):
        if self.http_client: await self.http_client.aclose()

    def _progress_file(self, task): return PROGRESS_DIR / f"plsbeta_{task}_progress.json"
    def _save_progress(self, task, data):
        data['updated_at'] = datetime.now().isoformat(); data['stats'] = self.stats.copy()
        self._progress_file(task).write_text(json.dumps(data, indent=2))
    def _load_progress(self, task):
        f = self._progress_file(task); return json.loads(f.read_text()) if f.exists() else {}

    async def discover_case_ids(self, start_id=1, end_id=200000):
        logger.info(f"=== DISCOVER CASE IDS: {start_id} to {end_id} ===")
        progress = self._load_progress('ids')
        resume_id = progress.get('last_id', start_id - 1) + 1
        if resume_id > start_id: start_id = resume_id; logger.info(f"Resuming from ID {resume_id}")
        col = self.db.plsbeta_caselaws; semaphore = asyncio.Semaphore(self.concurrency)
        async def scan_id(case_id):
            if stop_requested: return 0
            async with semaphore:
                url = f"{BASE_URL}/Result.asp?description=Case&CatSearch=Case&ID={case_id}"
                r = await self._get_with_refresh(url)
                if not r or r.status_code != 200: return 0
                text = r.text
                if 'No Record Found' in text or len(text) < 1000: return 0
                soup = BeautifulSoup(text, 'html.parser'); found = 0
                for link in soup.find_all('a', href=True):
                    href = link.get('href', ''); link_text = link.get_text(strip=True)
                    if not link_text or len(link_text) < 10: continue
                    if any(x in href.lower() for x in ['content', 'viewcase', 'judgement', 'caseno']):
                        cit = re.search(r'(\d{4})\s+(PLD|SCMR|CLC|PCrLJ|YLR|MLD|PLC|PTD|CLD|GBLR)\s+(\d+)', link_text)
                        case_data = {'plsbeta_id': case_id, 'title': link_text[:1000],
                            'source_url': href if href.startswith('http') else f"{BASE_URL}/{href}",
                            'source': 'plsbeta_v2', 'discovered_at': datetime.now(timezone.utc).isoformat()}
                        if cit:
                            case_data['year'] = int(cit.group(1)); case_data['journal'] = cit.group(2)
                            case_data['citation'] = f"{cit.group(1)} {cit.group(2)} {cit.group(3)}"
                            case_data['case_id'] = f"{cit.group(1)}{cit.group(2)[0]}{cit.group(3)}"
                        else: case_data['case_id'] = f"plsbeta_{case_id}_{found}"
                        exists = await col.find_one({'case_id': case_data['case_id']})
                        if not exists: await col.insert_one(case_data); self.stats['ids_discovered'] += 1; found += 1
                return found
        for batch_start in range(start_id, end_id + 1, BATCH_SIZE):
            if stop_requested: break
            batch_end = min(batch_start + BATCH_SIZE, end_id + 1)
            results = await asyncio.gather(*[scan_id(i) for i in range(batch_start, batch_end)])
            total_found = sum(r for r in results if r)
            processed = batch_end - start_id; total_range = end_id - start_id + 1
            pct = (processed / total_range) * 100; elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = processed / elapsed if elapsed > 0 else 0
            if (batch_start - start_id) % (BATCH_SIZE * 10) == 0 or total_found > 0:
                logger.info(f"IDs {batch_start}-{batch_end}: +{total_found} | {pct:.1f}% | New: {self.stats['ids_discovered']} | {rate:.0f} IDs/s | Relogins: {self.stats['relogins']}")
            self._save_progress('ids', {'last_id': batch_end - 1, 'start_id': start_id, 'end_id': end_id})
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        logger.info(f"=== ID DISCOVERY COMPLETE: {self.stats['ids_discovered']} new ===")

    async def fetch_case_content(self, limit=0):
        logger.info("=== FETCH CASE CONTENT ===")
        col = self.db.plsbeta_caselaws
        query = {'source_url': {'$exists': True, '$ne': ''}, '$or': [{'full_content': {'$exists': False}}, {'full_content': ''}, {'full_content': None}]}
        pending = await col.find(query, {'_id': 1, 'case_id': 1, 'source_url': 1}).to_list(length=limit or 500000)
        total = len(pending); logger.info(f"Cases needing content: {total:,}"); return if total == 0
        semaphore = asyncio.Semaphore(self.concurrency)
        async def fetch_one(doc):
            if stop_requested: return
            async with semaphore:
                url = doc.get('source_url', ''); return if not url
                if not url.startswith('http'): url = f"http://www.plsbeta.com/LawOnline/law/{url}"
                r = await self._get_with_refresh(url)
                if not r or r.status_code != 200 or len(r.text) < 200:
                    self.stats['errors' if not r or r.status_code != 200 else 'empty'] += 1; return
                soup = BeautifulSoup(r.text, 'html.parser')
                for tag in soup(['script', 'style', 'nav', 'header', 'footer']): tag.decompose()
                text = soup.get_text(separator='\n', strip=True)
                if len(text) < 50: self.stats['empty'] += 1; return
                update = {'full_content': text, 'content_fetched_at': datetime.now(timezone.utc).isoformat()}
                meta = self._extract_metadata(text); update.update(meta)
                await col.update_one({'_id': doc['_id']}, {'$set': update})
                self.stats['content_fetched'] += 1
        for batch_start in range(0, total, BATCH_SIZE):
            if stop_requested: break
            batch = pending[batch_start:batch_start + BATCH_SIZE]
            await asyncio.gather(*[fetch_one(doc) for doc in batch])
            processed = batch_start + len(batch)
            if processed % 200 == 0 or processed == total:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = self.stats['content_fetched'] / elapsed if elapsed > 0 else 0
                logger.info(f"Content: {processed:,}/{total:,} | Fetched: {self.stats['content_fetched']:,} | {rate:.1f}/s")
            self._save_progress('content', {'processed': processed, 'total': total})
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        logger.info("=== CONTENT FETCH COMPLETE ===")

    def _extract_metadata(self, content):
        meta = {}; lines = content.split('\n')
        for i, line in enumerate(lines[:30]):
            if re.match(r'^(?:Before|Present):?\s*$', line, re.I) and i + 1 < len(lines):
                j = re.sub(r',?\s*JJ?\.?\s*$', '', lines[i + 1].strip())
                if j and 3 < len(j) < 200: meta['judge'] = j; break
        for line in lines[:40]:
            if re.search(r'[-—‑]+\s*(?:Appellant|Petitioner)', line):
                pet = re.sub(r'[-—‑]+\s*(?:Appellant|Petitioner).*', '', line).strip()
                if pet and len(pet) > 2: meta['petitioner'] = pet[:300]
            elif re.search(r'[-—‑]+\s*Respondent', line):
                resp = re.sub(r'[-—‑]+\s*Respondent.*', '', line).strip()
                if resp and len(resp) > 2: meta['respondent'] = resp[:300]
        return meta

    async def scrape_statutes(self):
        logger.info("=== SCRAPE STATUTES ===")
        categories = [("Copyright", "/LawOnline/law/intellectuallaw.asp"), ("Criminal", "/LawOnline/law/criminallaw.asp"), ("General", "/LawOnline/law/generallaw.asp"), ("Services/Labour", "/LawOnline/law/servicelaw.asp"), ("Taxation", "/LawOnline/law/taxlaw.asp"), ("Banking/Financial", "/LawOnline/law/bankinglaw.asp"), ("Civil", "/LawOnline/law/civillaw.asp"), ("Constitutional", "/LawOnline/law/constitutionallaw.asp"), ("Family", "/LawOnline/law/familylaw.asp")]
        col = self.db.plsbeta_statutes; total = 0
        for cat_name, cat_path in categories:
            url = f"http://www.plsbeta.com{cat_path}"
            r = await self._get_with_refresh(url); continue if not r or r.status_code != 200
            soup = BeautifulSoup(r.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if 'statutesnext.asp' in link['href']:
                    text = link.get_text(strip=True); continue if not text
                    yr = re.search(r'\b(19\d{2}|20\d{2})\b', text)
                    await col.update_one({'name': text, 'category': cat_name}, {'$set': {'name': text, 'category': cat_name, 'year': int(yr.group(1)) if yr else None, 'url': link['href'], 'scraped_at': datetime.now(timezone.utc).isoformat()}}, upsert=True); total += 1
            logger.info(f"  {cat_name}: done"); await asyncio.sleep(1)
        logger.info(f"=== STATUTES COMPLETE: {total} ===")

    async def scrape_terms_words_maxims(self):
        logger.info("=== SCRAPE TERMS, WORDS, MAXIMS ===")
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            for page_type, col_name, url_tpl in [('terms', 'plsbeta_terms', f'{BASE_URL}/legalterms.asp?alpha={{letter}}'), ('words', 'plsbeta_words', f'{BASE_URL}/wordphrases.asp?alpha={{letter}}')]:
                url = url_tpl.format(letter=letter); r = await self._get_with_refresh(url); continue if not r or r.status_code != 200
                soup = BeautifulSoup(r.text, 'html.parser'); col = self.db[col_name]
                for item in soup.find_all(['li', 'p', 'div', 'a']):
                    text = item.get_text(strip=True); continue if not text or len(text) <= 3
                    key = 'term' if page_type == 'terms' else 'word'
                    await col.update_one({key: text}, {'$set': {key: text, 'letter': letter, 'scraped_at': datetime.now(timezone.utc).isoformat()}}, upsert=True)
            await asyncio.sleep(0.5)
        logger.info("=== TERMS/WORDS COMPLETE ===")

    def get_status(self):
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {**self.stats, 'elapsed_seconds': round(elapsed), 'last_login': self.auth.last_login.isoformat() if self.auth.last_login else None}


async def main():
    parser = argparse.ArgumentParser(description='PLSBeta Unified Scraper v2')
    parser.add_argument('--mode', choices=['ids', 'content', 'statutes', 'terms', 'all'], default='ids')
    parser.add_argument('--start-id', type=int, default=1); parser.add_argument('--end-id', type=int, default=200000)
    parser.add_argument('--limit', type=int, default=0); parser.add_argument('--concurrency', type=int, default=3)
    args = parser.parse_args()
    scraper = PLSBetaScraperV2(concurrency=args.concurrency)
    try:
        await scraper.init()
        if args.mode in ('ids', 'all'): await scraper.discover_case_ids(start_id=args.start_id, end_id=args.end_id)
        if args.mode in ('content', 'all'): await scraper.fetch_case_content(limit=args.limit)
        if args.mode in ('statutes', 'all'): await scraper.scrape_statutes()
        if args.mode in ('terms', 'all'): await scraper.scrape_terms_words_maxims()
        logger.info(f"\nFINAL: {json.dumps(scraper.get_status(), indent=2)}")
    except RuntimeError as e: logger.error(str(e))
    finally: await scraper.close()


if __name__ == "__main__": asyncio.run(main())
