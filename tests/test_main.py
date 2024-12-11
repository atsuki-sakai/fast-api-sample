import pytest
from httpx import AsyncClient
from app.main import create_app

app = create_app()

@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items", json={"name": "Test Item", "description": "A test description"})
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_item_not_found():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/nonexistent_id")
        assert response.status_code == 404