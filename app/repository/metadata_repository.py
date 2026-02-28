from app.config.database import mongo

class MetadataRepository:

    async def save(self, data: dict):
        collection = mongo.db.metadata

        await collection.update_one(
            {"url": data["url"]},
            {"$set": data},
            upsert=True
        )

    async def find_by_url(self, url: str):
        collection = mongo.db.metadata

        return await collection.find_one(
            {"url": url},
            {"_id": 0}
        )