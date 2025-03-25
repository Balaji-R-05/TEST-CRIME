from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import GEOSPHERE
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        # Get MongoDB URI from environment variable or use default
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "crimespot")

        cls.client = AsyncIOMotorClient(mongodb_uri)
        cls.db = cls.client[database_name]

        try:
            # Create indexes
            await cls.db.users.create_index("username", unique=True)
            await cls.db.users.create_index("email", unique=True)
            await cls.db.crime_reports.create_index([("location", GEOSPHERE)])
            await cls.db.crime_reports.create_index("dateTime")
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise e

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            print("Database connection closed")

# Create global database instance
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["crimespot"]


