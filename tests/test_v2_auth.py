from httpx import AsyncClient


async def test_v2_requires_api_key(client: AsyncClient) -> None:
    response = await client.get("/api/v2/media-items")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"


async def test_v2_rejects_invalid_api_key(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v2/media-items",
        headers={"X-API-Key": "not-a-real-key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"
