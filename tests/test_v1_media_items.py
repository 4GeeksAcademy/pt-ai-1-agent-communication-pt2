from httpx import AsyncClient


async def test_list_media_items_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/media-items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_create_and_get_media_item(client: AsyncClient, sample_media_item: dict) -> None:
    assert sample_media_item["title"] == "Test Item"

    response = await client.get(f"/api/v1/media-items/{sample_media_item['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Item"


async def test_update_media_item(client: AsyncClient, sample_media_item: dict) -> None:
    response = await client.put(
        f"/api/v1/media-items/{sample_media_item['id']}",
        json={
            "title": "Updated Item",
            "description": "Updated description",
            "release_year": 2021,
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Item"


async def test_delete_media_item(client: AsyncClient, sample_media_item: dict) -> None:
    response = await client.delete(f"/api/v1/media-items/{sample_media_item['id']}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/media-items/{sample_media_item['id']}")
    assert response.status_code == 404


async def test_get_missing_media_item_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/media-items/99999")
    assert response.status_code == 404
