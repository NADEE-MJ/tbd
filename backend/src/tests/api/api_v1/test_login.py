import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from src import crud
from src.core.config import settings
from src.models.user import User
from src.tests.utils.user import TEST_USER_EMAIL, TEST_USER_PASSWORD, get_auth_header
from src.utils import generate_magic_link_token


@pytest.mark.asyncio
async def test_get_access_token(db: AsyncSession, client: TestClient, test_user: User) -> None:
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    response = client.post(
        f"{settings.API_VERSION_STR}/login/access-token",
        data=login_data,
    )

    token = response.json()
    await crud.user.remove(db, id=test_user.id)
    assert response.status_code == 200
    assert "access_token" in token
    assert token["access_token"]


@pytest.mark.asyncio
async def test_use_access_token(db: AsyncSession, client: TestClient, test_user: User) -> None:
    headers = get_auth_header(client)
    response = client.post(f"{settings.API_VERSION_STR}/login/test-token", headers=headers)
    result = response.json()
    await crud.user.remove(db, id=test_user.id)
    assert response.status_code == 200
    assert "email" in result


@pytest.mark.asyncio
async def test_send_magic_link(db: AsyncSession, client: TestClient, test_user: User) -> None:
    response = client.post(f"{settings.API_VERSION_STR}/send-magic-link?email={TEST_USER_EMAIL}")
    await crud.user.remove(db, id=test_user.id)
    result = response.json()
    assert result["message"] == "Magic Link Sent"
    assert result["success"] is True


@pytest.mark.asyncio
async def test_magic_link(db: AsyncSession, client: TestClient, test_user: User) -> None:
    token = generate_magic_link_token(email=TEST_USER_EMAIL)
    response = client.post(f"{settings.API_VERSION_STR}/magic-link?token={token}")
    result = response.json()
    headers = {"Authorization": f"Bearer {result['access_token']}"}
    response = client.post(f"{settings.API_VERSION_STR}/login/test-token", headers=headers)
    result = response.json()
    await crud.user.remove(db, id=test_user.id)

    assert result["id"] == test_user.id
