import pytest

from app.application.model_service import ModelService
from app.core.errors import ConflictError
from app.domain.models.models import Capability, ModelCreate
from app.infrastructure.repositories.model_repo import ModelRepository


@pytest.mark.asyncio
async def test_register_model(db_session):
    svc = ModelService(ModelRepository(db_session))
    model = await svc.create(ModelCreate(
        model_id="m1", provider_id="p1", display_name="Model One",
        capabilities={Capability.CODING},
    ))
    assert model.has_capability(Capability.CODING)
    assert not model.has_capability(Capability.VISION)


@pytest.mark.asyncio
async def test_duplicate_model_raises(db_session):
    svc = ModelService(ModelRepository(db_session))
    await svc.create(ModelCreate(model_id="m1", provider_id="p1", display_name="Model One"))
    with pytest.raises(Exception):
        await svc.create(ModelCreate(model_id="m1", provider_id="p1", display_name="Duplicate"))


@pytest.mark.asyncio
async def test_capability_metadata_roundtrip(db_session):
    svc = ModelService(ModelRepository(db_session))
    model = await svc.create(ModelCreate(
        model_id="m1", provider_id="p1", display_name="Model One",
        capabilities={Capability.CODING, Capability.VISION},
        context_window=50_000,
    ))
    fetched = await svc.get("m1")
    assert fetched.capabilities == {Capability.CODING, Capability.VISION}
    assert fetched.context_window == 50_000


@pytest.mark.asyncio
async def test_model_provider_relationship(db_session):
    svc = ModelService(ModelRepository(db_session))
    await svc.create(ModelCreate(model_id="m1", provider_id="p1", display_name="A"))
    await svc.create(ModelCreate(model_id="m2", provider_id="p2", display_name="B"))
    p1_models = await svc.list(provider_id="p1")
    assert len(p1_models) == 1
    assert p1_models[0].model_id == "m1"
