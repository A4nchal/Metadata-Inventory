import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def transport():
    return httpx.ASGITransport(app=app)


@pytest.mark.asyncio
async def test_post_metadata_success(transport):

    mock_response = {
        "url": "https://example.com",
        "headers": {"content-type": "text/html"},
        "cookies": {},
        "page_source": "<html>Test</html>"
    }

    with patch(
        "app.service.fetchService.FetchService.fetch",
        new=AsyncMock(return_value=mock_response)
    ), patch(
        "app.repository.metadataRepository.MetadataRepository.save",
        new=AsyncMock()
    ):

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as ac:

            response = await ac.post(
                "/metadata/",
                json={"url": "https://example.com"}
            )

    assert response.status_code == 200
    assert response.json()["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_get_metadata_cache_hit(transport):

    mock_data = {
        "url": "https://cached.com",
        "headers": {},
        "cookies": {},
        "page_source": "<html>Cached</html>"
    }

    with patch(
        "app.repository.metadataRepository.MetadataRepository.find_by_url",
        new=AsyncMock(return_value=mock_data)
    ):

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as ac:

            response = await ac.get(
                "/metadata/",
                params={"url": "https://cached.com"}
            )

    assert response.status_code == 200
    assert response.json()["url"] == "https://cached.com"


@pytest.mark.asyncio
async def test_get_metadata_cache_miss_returns_202(transport):

    with patch(
        "app.repository.metadataRepository.MetadataRepository.find_by_url",
        new=AsyncMock(return_value=None)
    ):

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as ac:

            response = await ac.get(
                "/metadata/",
                params={"url": "https://newsite.com"}
            )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_get_invalid_url(transport):

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:

        response = await ac.get(
            "/metadata/",
            params={"url": "invalid-url"}
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_invalid_url(transport):

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:

        response = await ac.post(
            "/metadata/",
            json={"url": "invalid-url"}
        )

    assert response.status_code == 422