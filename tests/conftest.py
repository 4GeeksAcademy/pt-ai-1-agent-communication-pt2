import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def sample_media_item(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/media-items",
        json={
            "title": "Test Item",
            "description": "A test media item",
            "release_year": 2020,
        },
    )
    assert response.status_code == 201
    return response.json()
