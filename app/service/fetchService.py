import httpx
from fastapi import HTTPException
from app.config.settings import settings

class FetchService:

    def __init__(self):
        self.timeout = settings.request_timeout

    async def fetch(self, url: str) -> dict:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            ) as client:

                response = await client.get(url)

                response.raise_for_status()

                return {
                    "url": url,
                    "headers": dict(response.headers),
                    "cookies": dict(response.cookies),
                    "page_source": response.text
                }

        except httpx.ConnectTimeout:
            raise HTTPException(
                status_code=504,
                detail="Connection timeout while fetching URL"
            )

        except httpx.ReadTimeout:
            raise HTTPException(
                status_code=504,
                detail="Read timeout while fetching URL"
            )

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Upstream returned error {exc.response.status_code}"
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch metadata from upstream service"
            )