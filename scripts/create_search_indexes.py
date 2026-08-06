"""
Create weighted text indexes for improved full-text search relevance.
Run once — safe to re-run (drops and recreates).

Field weights:
  citation: 10  (highest — exact citation matches dominate)
  parties: 8    (party name searches)
  headnotes_text: 5  (legal headnotes)
  judge: 3
  petitioner: 3
  respondent: 3
  court: 2
  full_content: 1  (lowest — avoids noise from incidental mentions)
"""

import asyncio
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


async def main():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'pakistanlawsite')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    col = db.pls_caselaws

    # Drop existing text index (MongoDB only allows one text index per collection)
    logger.info("Dropping existing text indexes...")
    indexes = await col.index_information()
    for name, info in indexes.items():
        if any(v == 'text' for _, v in info.get('key', [])):
            logger.info(f"  Dropping text index: {name}")
            await col.drop_index(name)

    # Create weighted compound text index
    logger.info("Creating weighted text index...")
    await col.create_index(
        [
            ("citation", "text"),
            ("parties", "text"),
            ("headnotes_text", "text"),
            ("judge", "text"),
            ("petitioner", "text"),
            ("respondent", "text"),
            ("court", "text"),
            ("full_content", "text"),
        ],
        weights={
            "citation": 10,
            "parties": 8,
            "headnotes_text": 5,
            "judge": 3,
            "petitioner": 3,
            "respondent": 3,
            "court": 2,
            "full_content": 1,
        },
        name="weighted_search_index",
        default_language="english",
        background=True,
    )
    logger.info("Weighted text index created!")

    # Also create standard field indexes for filter performance
    logger.info("Creating supporting indexes...")
    for field in ["year", "court", "journal", "judge", "case_id", "citation"]:
        try:
            await col.create_index(field, background=True)
        except Exception:
            pass  # Already exists

    # Compound index for filtered searches
    await col.create_index([("year", -1), ("court", 1)], background=True)
    await col.create_index([("court", 1), ("year", -1)], background=True)

    # Citation links indexes
    links = db.citation_links
    await links.create_index("citing_case_id", background=True)
    await links.create_index("cited_case_id", background=True)

    logger.info("All indexes created successfully!")

    # Verify
    indexes = await col.index_information()
    for name, info in indexes.items():
        if 'text' in str(info.get('key', '')):
            logger.info(f"  Text index: {name}")
            weights = info.get('weights', {})
            for field, weight in sorted(weights.items(), key=lambda x: -x[1]):
                logger.info(f"    {field}: {weight}")


if __name__ == "__main__":
    asyncio.run(main())
