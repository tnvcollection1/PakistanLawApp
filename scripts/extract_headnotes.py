"""Extract headnotes from full_content and store in headnotes_text field.
Headnotes in PLS content appear at the top, before the actual judgment.
They follow patterns like:
- "S.3---Constitution of Pakistan, Art. 199---Jurisdiction..."
- Lines with "---" separators containing legal points
"""
import asyncio
import re
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')


def extract_headnotes(content):
    """Extract headnotes section from full_content."""
    if not content:
        return ""

    lines = content.split('\n')
    headnote_lines = []
    judgment_started = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Judgment typically starts with phrases like:
        # "ORDER", "JUDGMENT", "Per ", "The petitioner", "The appellant", "The facts"
        # Or after a long section of headnote-style "---" lines
        lower = stripped.lower()
        if any(lower.startswith(s) for s in [
            'order', 'judgment', 'per ', 'the petitioner', 'the appellant',
            'the respondent', 'the facts', 'this is', 'brief facts',
            'the prosecution', 'the complainant', 'this petition',
            'this appeal', 'through this', 'the case',
        ]):
            # Check if we've already accumulated some headnote content
            if len(headnote_lines) > 3:
                judgment_started = True
                break

        headnote_lines.append(stripped)

        # Safety limit - headnotes rarely exceed 2000 chars
        if sum(len(l) for l in headnote_lines) > 3000:
            break

    if not headnote_lines:
        return ""

    # If judgment never started, take the first portion as headnotes
    headnotes_text = '\n'.join(headnote_lines)

    # Clean up - remove the citation header (first 2-3 lines that are just the citation)
    # Keep the legal points (lines with "---" or statute references)
    return headnotes_text.strip()


async def main():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME', 'test_database')]

    # Count cases without headnotes_text
    total = await db.pls_caselaws.count_documents({
        'full_content': {'$exists': True, '$ne': ''},
        '$or': [{'headnotes_text': {'$exists': False}}, {'headnotes_text': ''}]
    })
    print(f"Cases without headnotes_text: {total:,}")

    updated = 0
    skipped = 0

    cursor = db.pls_caselaws.find(
        {
            'full_content': {'$exists': True, '$ne': ''},
            '$or': [{'headnotes_text': {'$exists': False}}, {'headnotes_text': ''}]
        },
        {'_id': 1, 'case_id': 1, 'full_content': 1}
    ).batch_size(500)

    async for doc in cursor:
        headnotes = extract_headnotes(doc.get('full_content', ''))
        if headnotes and len(headnotes) > 50:
            await db.pls_caselaws.update_one(
                {'_id': doc['_id']},
                {'$set': {'headnotes_text': headnotes}}
            )
            updated += 1
        else:
            skipped += 1

        if (updated + skipped) % 10000 == 0:
            print(f"Progress: {updated + skipped:,} / {total:,} | Extracted: {updated:,} | Skipped: {skipped:,}")

    print(f"\nDone! Extracted headnotes for {updated:,} cases. Skipped {skipped:,}.")

    total_with = await db.pls_caselaws.count_documents({'headnotes_text': {'$exists': True, '$ne': ''}})
    print(f"Total cases with headnotes_text: {total_with:,}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
