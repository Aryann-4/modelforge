import pytest

from app.application.provider_service import ProviderService
from app.core.errors import NotFoundError
from app.domain.providers.models import ProviderCreate, ProviderType, ProviderUpdate
from app.infrastructure.repositories.provider_repo import ProviderRepository


@pytest.mark.asyncio
async def test_add_provider(db_session):
    svc = ProviderService(ProviderRepository(db_session))
    provider = await svc.create(ProviderCreate(provider_id="p1", name="Test", type=ProviderType.MOCK))
    assert provider.provider_id == "p1"
    assert provider.enabled is True


@pytest.mark.asyncio
async def test_get_provider(db_session):
    svc = ProviderService(ProviderRepository(db_session))
    await svc.create(ProviderCreate(provider_id="p1", name="Test", type=ProviderType.MOCK))
    fetched = await svc.get("p1")
    assert fetched.name == "Test"


@pytest.mark.asyncio
async def test_disable_provider(db_session):
    svc = ProviderService(ProviderRepository(db_session))
    await svc.create(ProviderCreate(provider_id="p1", name="Test", type=ProviderType.MOCK))
    updated = await svc.update("p1", ProviderUpdate(enabled=False))
    assert updated.enabled is False
    assert updated.is_routable() is False


@pytest.mark.asyncio
async def test_delete_provider(db_session):
    svc = ProviderService(ProviderRepository(db_session))
    await svc.create(ProviderCreate(provider_id="p1", name="Test", type=ProviderType.MOCK))
    await svc.delete("p1")
    with pytest.raises(NotFoundError):
        await svc.get("p1")


@pytest.mark.asyncio
async def test_invalid_base_url_rejected():
    with pytest.raises(ValueError):
        ProviderCreate(provider_id="p1", name="Test", type=ProviderType.OPENAI_COMPATIBLE, base_url="not-a-url")
