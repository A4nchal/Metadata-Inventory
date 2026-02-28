import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config.settings import settings

class MongoConnection:

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    async def connect(self):
        retries = 5
        delay = 3

        for attempt in range(retries):
            try:
                self.client = AsyncIOMotorClient(
                    settings.mongo_uri,
                    serverSelectionTimeoutMS=5000
                )

                await self.client.server_info()

                self.db = self.client[settings.db_name]
                print("MongoDB connected")
                return

            except ServerSelectionTimeoutError:
                print(f"MongoDB not ready. Retry {attempt + 1}/{retries}")
                await asyncio.sleep(delay)

        raise RuntimeError("Could not connect to MongoDB after retries")

    async def create_indexes(self):
        await self.db.metadata.create_index("url", unique=True)

    async def close(self):
        if self.client:
            self.client.close()

mongo = MongoConnection()

async def get_metadata_collection():
    return mongo.db.metadata