"""Extract citations from case content and populate the citation field."""
import asyncio
import re
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Spaced journal patterns -> normalized name
JOURNAL_PATTERNS = [
    (r'P\s*L\s*D', 'PLD'),
    (r'S\s*C\s*M\s*R', 'SCMR'),
    (r'C\s*L\s*C', 'CLC'),
    (r'Y\s*L\s*R', 'YLR'),
    (r'M\s*L\s*D', 'MLD'),
    (r'P\s*C\s*r\s*L\s*J', 'PCrLJ'),
    (r'P\s*L\s*C\s*\(\s*C\s*S\s*\)', 'PLC(CS)'),
    (r'P\s*L\s*C', 'PLC'),
    (r'P\s*T\s*D', 'PTD'),
    (r'C\s*L\s*D', 'CLD'),
    (r'G\s*B\s*L\s*R', 'GBLR'),
]

COURT_NORMALIZE = {
    'supreme court': 'SC', 'supreme-court': 'SC', 'sc': 'SC',
    'lahore': 'Lahore', 'lhr': 'Lahore',
    'sindh': 'Sindh', 'karachi': 'Karachi', 'kar': 'Karachi',
    'peshawar': 'Peshawar', 'pesh': 'Peshawar',
    'quetta': 'Quetta', 'balochistan': 'Balochistan', 'bal': 'Balochistan',
    'islamabad': 'Islamabad', 'isb': 'Islamabad',
    'federal shariat court': 'FSC', 'fsc': 'FSC',
    'ajk': 'AJK', 'gilgit': 'GB', 'gilgit-baltistan': 'GB',
}


def extract_citation(content):
    """Extract citation from the first 500 chars of case content."""
    if not content:
        return None
    
    head = content[:500].strip().strip('"').strip()
    # Normalize whitespace
    head = re.sub(r'\s+', ' ', head)
    
    for pattern, journal in JOURNAL_PATTERNS:
        # Pattern 1: "JOURNAL YEAR COURT PAGE" - e.g., "P L D 2025 Supreme Court 36"
        # Court name is one or two words (no greedy consuming across lines)
        regex1 = rf'{pattern}\s+(\d{{4}})\s+((?:Supreme\s+Court|[A-Za-z][\w\-]*(?:\s+[A-Za-z][\w\-]*)?))\s*\.?\s+(\d+)'
        m = re.search(regex1, head, re.IGNORECASE)
        if m:
            year = m.group(1)
            page = m.group(3)
            return f"{year} {journal} {page}"
        
        # Pattern 2: "YEAR JOURNAL PAGE" - e.g., "2025 C L C 107"
        regex2 = rf'(\d{{4}})\s+{pattern}\s+(\d+)'
        m = re.search(regex2, head, re.IGNORECASE)
        if m:
            year = m.group(1)
            page = m.group(2)
            return f"{year} {journal} {page}"
    
    return None


async def main():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    # Count cases without citation
    total = await db.pls_caselaws.count_documents({
        'full_content': {'$exists': True, '$ne': ''},
        '$or': [{'citation': {'$exists': False}}, {'citation': ''}]
    })
    print(f"Cases without citation: {total:,}")
    
    updated = 0
    failed = 0
    batch_size = 500
    
    cursor = db.pls_caselaws.find(
        {
            'full_content': {'$exists': True, '$ne': ''},
            '$or': [{'citation': {'$exists': False}}, {'citation': ''}]
        },
        {'_id': 1, 'case_id': 1, 'full_content': 1}
    ).batch_size(batch_size)
    
    async for doc in cursor:
        citation = extract_citation(doc.get('full_content', ''))
        if citation:
            await db.pls_caselaws.update_one(
                {'_id': doc['_id']},
                {'$set': {'citation': citation}}
            )
            updated += 1
        else:
            failed += 1
        
        if (updated + failed) % 5000 == 0:
            print(f"Progress: {updated + failed:,} processed, {updated:,} citations extracted, {failed:,} no citation found")
    
    print(f"\nDone! Updated {updated:,} cases with citations. {failed:,} cases had no extractable citation.")
    
    # Verify
    total_with = await db.pls_caselaws.count_documents({'citation': {'$exists': True, '$ne': ''}})
    print(f"Total cases with citation field now: {total_with:,}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
