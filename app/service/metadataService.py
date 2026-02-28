from fastapi import BackgroundTasks, status, HTTPException
from fastapi.responses import JSONResponse
from app.repository.metadataRepository import MetadataRepository
from app.service.fetchService import FetchService
import httpx

class MetadataService:

    def __init__(self):
        self.repo = MetadataRepository()
        self.fetcher = FetchService()

    async def create_metadata(self, url: str):
        data = await self.fetcher.fetch(url)
        await self.repo.save(data)
        return data

    async def get_metadata(self, url: str, background_tasks: BackgroundTasks):
        record = await self.repo.find_by_url(url)

        if record:
            return record

        # Validate that domain is reachable BEFORE scheduling background job
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.head(url)

        except httpx.ConnectTimeout:
            raise HTTPException(
                status_code=504,
                detail="Connection timeout while validating URL"
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Failed to reach the requested URL"
            )

        # Schedule async background collection
        background_tasks.add_task(self._collect_async, url)

        return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Request accepted. Metadata collection initiated."
        }
        )

    async def _collect_async(self, url: str):
        try:
            data = await self.fetcher.fetch(url)
            await self.repo.save(data)

        except Exception as e:
            print(f"Background metadata collection failed for {url}: {e}")