import pytest


@pytest.mark.asyncio
async def test_provider_crud(app_client):
    resp = await app_client.post("/api/v1/providers", json={
        "provider_id": "p1", "name": "Test Provider", "type": "MOCK",
    })
    assert resp.status_code == 201
    assert resp.json()["provider_id"] == "p1"

    resp = await app_client.get("/api/v1/providers/p1")
    assert resp.status_code == 200

    resp = await app_client.patch("/api/v1/providers/p1", json={"enabled": False})
    assert resp.status_code == 200
    assert resp.json()["enabled"] is False

    resp = await app_client.delete("/api/v1/providers/p1")
    assert resp.status_code == 204

    resp = await app_client.get("/api/v1/providers/p1")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_model_crud(app_client):
    await app_client.post("/api/v1/providers", json={"provider_id": "p1", "name": "P", "type": "MOCK"})
    resp = await app_client.post("/api/v1/models", json={
        "model_id": "m1", "provider_id": "p1", "display_name": "Model 1",
        "capabilities": ["coding"],
    })
    assert resp.status_code == 201
    resp = await app_client.get("/api/v1/models/m1")
    assert resp.status_code == 200
    assert "coding" in resp.json()["capabilities"]


@pytest.mark.asyncio
async def test_route_endpoint_end_to_end(app_client):
    await app_client.post("/api/v1/providers", json={
        "provider_id": "mock-cloud", "name": "Mock Cloud", "type": "MOCK",
        "metadata": {"behavior": "success"},
    })
    await app_client.post("/api/v1/models", json={
        "model_id": "coder", "provider_id": "mock-cloud", "display_name": "Coder",
        "capabilities": ["coding"], "execution_type": "CLOUD",
    })
    await app_client.post("/api/v1/policies", json={"policy_id": "hybrid", "name": "Hybrid"})

    resp = await app_client.post("/api/v1/route", json={
        "task": {"user_request": "Optimize this Python algorithm.", "privacy_classification": "INTERNAL"},
        "policy_id": "hybrid",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["task"]["task_type"] == "CODING"
    assert body["decision"]["selected_model_id"] == "coder"


@pytest.mark.asyncio
async def test_route_endpoint_missing_policy_returns_404(app_client):
    resp = await app_client.post("/api/v1/route", json={
        "task": {"user_request": "hi", "privacy_classification": "INTERNAL"},
        "policy_id": "does-not-exist",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_error_handling_invalid_provider_type(app_client):
    resp = await app_client.post("/api/v1/providers", json={
        "provider_id": "p1", "name": "P", "type": "NOT_A_REAL_TYPE",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_complete_endpoint_auto_selects_model_and_answers(app_client):
    """The whole point of /api/v1/complete: caller gives a prompt and gets an
    answer back, with no task type, model, or policy required."""
    await app_client.post("/api/v1/providers", json={
        "provider_id": "mock-cloud", "name": "Mock Cloud", "type": "MOCK",
        "metadata": {"behavior": "success"},
    })
    await app_client.post("/api/v1/models", json={
        "model_id": "coder", "provider_id": "mock-cloud", "display_name": "Coder",
        "capabilities": ["coding"], "execution_type": "CLOUD",
    })
    await app_client.post("/api/v1/policies", json={
        "policy_id": "hybrid-default", "name": "Hybrid",
    })

    resp = await app_client.post("/api/v1/complete", json={
        "prompt": "Optimize this Python algorithm for speed.",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["succeeded"] is True
    assert body["answer"] is not None
    assert body["model_id"] == "coder"
    assert body["task_type"] == "CODING"
    assert len(body["attempts"]) == 1


@pytest.mark.asyncio
async def test_complete_endpoint_falls_back_on_context_exhaustion(app_client):
    """A prompt too big for the best-ranked model should transparently land
    on a larger-context model, with both attempts visible in the response."""
    await app_client.post("/api/v1/providers", json={
        "provider_id": "mock-cloud", "name": "Mock Cloud", "type": "MOCK",
        "metadata": {"behavior": "success"},
    })
    await app_client.post("/api/v1/models", json={
        "model_id": "small-fast", "provider_id": "mock-cloud", "display_name": "Small Fast",
        "context_window": 4000, "capabilities": ["coding"], "execution_type": "CLOUD",
        "latency_metadata": {"estimated_latency_ms": 100},
    })
    await app_client.post("/api/v1/models", json={
        "model_id": "big-slow", "provider_id": "mock-cloud", "display_name": "Big Slow",
        "context_window": 200_000, "capabilities": ["coding"], "execution_type": "CLOUD",
        "latency_metadata": {"estimated_latency_ms": 3000},
    })
    await app_client.post("/api/v1/policies", json={
        "policy_id": "hybrid-default", "name": "Hybrid",
    })

    resp = await app_client.post("/api/v1/complete", json={
        "prompt": "optimize this code: " + ("x" * 400_000),
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["succeeded"] is True
    assert body["model_id"] == "big-slow"
    assert len(body["attempts"]) == 2
    assert body["attempts"][0]["model_id"] == "small-fast"
    assert body["attempts"][0]["error_code"] == "CONTEXT_LENGTH_EXCEEDED"


@pytest.mark.asyncio
async def test_complete_endpoint_no_eligible_model_reports_reasons(app_client):
    await app_client.post("/api/v1/policies", json={
        "policy_id": "hybrid-default", "name": "Hybrid",
    })
    resp = await app_client.post("/api/v1/complete", json={"prompt": "hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["succeeded"] is False
    assert body["answer"] is None
    assert body["decision_reasons"]
