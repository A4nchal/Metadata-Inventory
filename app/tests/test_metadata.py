import pytest
import httpx
from unittest.mock import AsyncMock, patch
from fastapi import BackgroundTasks

from app.main import app
from app.service.metadata_service import MetadataService


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def transport():
    return httpx.ASGITransport(app=app)


@pytest.fixture
async def async_client(transport):
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client


# ============================================================
# Controller Layer Tests
# ============================================================

@pytest.mark.asyncio
async def test_post_metadata_success(async_client):

    mock_data = {
        "url": "https://example.com",
        "headers": {},
        "cookies": {},
        "page_source": "<html>OK</html>"
    }

    with patch(
        "app.service.fetch_service.FetchService.fetch",
        new=AsyncMock(return_value=mock_data)
    ), patch(
        "app.repository.metadata_repository.MetadataRepository.save",
        new=AsyncMock()
    ):

        response = await async_client.post(
            "/metadata/",
            json={"url": "https://example.com"}
        )

    assert response.status_code == 200
    assert response.json()["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_post_invalid_url(async_client):

    response = await async_client.post(
        "/metadata/",
        json={"url": "invalid-url"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_metadata_cache_hit(async_client):

    mock_data = {
        "url": "https://cached.com",
        "headers": {},
        "cookies": {},
        "page_source": "<html>Cached</html>"
    }

    with patch(
        "app.repository.metadata_repository.MetadataRepository.find_by_url",
        new=AsyncMock(return_value=mock_data)
    ):

        response = await async_client.get(
            "/metadata/",
            params={"url": "https://cached.com"}
        )

    assert response.status_code == 200
    assert response.json()["url"] == "https://cached.com"


@pytest.mark.asyncio
async def test_get_metadata_cache_miss_returns_202(async_client):

    with patch(
        "app.repository.metadata_repository.MetadataRepository.find_by_url",
        new=AsyncMock(return_value=None)
    ), patch(
        "app.service.metadata_service.MetadataService._collect_async",
        new=AsyncMock()
    ):

        response = await async_client.get(
            "/metadata/",
            params={"url": "https://newsite.com"}
        )

    assert response.status_code == 202
    assert "initiated" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_invalid_url(async_client):

    response = await async_client.get(
        "/metadata/",
        params={"url": "invalid-url"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_external_failure(async_client):

    with patch(
        "app.service.fetch_service.FetchService.fetch",
        side_effect=Exception("External failure")
    ):

        response = await async_client.post(
            "/metadata/",
            json={"url": "https://example.com"}
        )

    # Depending on your implementation, may be 500 or 502
    assert response.status_code >= 400


# ============================================================
# Service Layer Tests (Unit Tests)
# ============================================================

@pytest.mark.asyncio
async def test_service_create_metadata():

    service = MetadataService()

    service.fetcher.fetch = AsyncMock(return_value={
        "url": "https://example.com",
        "headers": {},
        "cookies": {},
        "page_source": "<html></html>"
    })

    service.repo.save = AsyncMock()

    result = await service.create_metadata("https://example.com")

    assert result["url"] == "https://example.com"
    service.repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_service_get_metadata_cache_hit():

    service = MetadataService()

    service.repo.find_by_url = AsyncMock(return_value={
        "url": "https://cached.com",
        "headers": {},
        "cookies": {},
        "page_source": "<html></html>"
    })

    background = BackgroundTasks()

    result = await service.get_metadata("https://cached.com", background)

    assert result["url"] == "https://cached.com"


@pytest.mark.asyncio
async def test_service_get_metadata_cache_miss_schedules_background():

    service = MetadataService()

    service.repo.find_by_url = AsyncMock(return_value=None)
    service._collect_async = AsyncMock()

    background = BackgroundTasks()

    response = await service.get_metadata(
        "https://newsite.com",
        background
    )

    assert response.status_code == 202