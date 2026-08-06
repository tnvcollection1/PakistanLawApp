from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
import os

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "pakistanlaw")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def get_db():
    return db

async def test_connection():
    try:
        await client.admin.command("ping")
        print("✅ MongoDB connected successfully")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
