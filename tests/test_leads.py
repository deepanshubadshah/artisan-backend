import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from jose import jwt
from typing import AsyncGenerator

def create_test_token():
    payload = {"sub": "testuser", "id": 1, "name": "Test User"}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_duplicate_lead(async_client):
    """
    Test that creating a lead with an email that already exists returns a 400 error
    with a proper message.
    """
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    lead_data = {
        "name": "Test Lead",
        "email": "duplicate@example.com",
        "company": "Test Co",
        "phone": "1234567890",
        "stage": "New",
        "engaged": False,
    }
    # First creation should succeed.
    response = await async_client.post("/leads/", json=lead_data, headers=headers)
    assert response.status_code == 201

    # Second creation with the same email should fail.
    response_dup = await async_client.post("/leads/", json=lead_data, headers=headers)
    assert response_dup.status_code == 400
    json_resp = response_dup.json()
    assert json_resp["detail"] == "Lead with this email already exists"

@pytest.mark.asyncio
async def test_get_nonexistent_lead(async_client):
    """
    Test that fetching a non-existent lead returns a 404 error.
    """
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(
        "/leads/id/00000000-0000-0000-0000-000000000000", headers=headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_lead(async_client):
    """
    Test that updating a non-existent lead returns a 404 error.
    """
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"name": "Updated Name"}
    response = await async_client.put(
        "/leads/id/00000000-0000-0000-0000-000000000000", json=update_data, headers=headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_lead(async_client):
    """
    Test that deleting a non-existent lead returns a 404 error.
    """
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.delete(
        "/leads/id/00000000-0000-0000-0000-000000000000", headers=headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_leads(async_client):
    """
    Test that fetching leads with skip and limit returns a list of leads.
    """
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/leads/leads", params={"skip": 0, "limit": 10}, headers=headers)
    assert response.status_code == 200
    json_resp = response.json()
    assert isinstance(json_resp, list) or "items" in json_resp