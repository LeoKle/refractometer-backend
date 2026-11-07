import uuid
from datetime import datetime

import mongomock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from services.queue_service import QueueService

pytestmark = pytest.mark.unit

CREATE_PAYLOAD = {
    "parameters": {"foo": "bar"},
    "issuer": "tester",
    "callback_url": "https://example.com/callback",
    "name": "sim-1",
}


@pytest.fixture
def service() -> QueueService:
    return QueueService(mongomock.MongoClient().db.queue)


@pytest.fixture
def client(service: QueueService) -> TestClient:
    from api import queue_controller
    from container import DependencyContainer

    app = FastAPI()
    app.include_router(queue_controller.router)

    container = DependencyContainer()
    container.queue_service.override(service)
    container.wire(modules=[queue_controller])

    return TestClient(app)


class TestPostQueue:
    def test_returns_created_element(self, client):
        response = client.post("/api/queue", json=CREATE_PAYLOAD)

        assert response.status_code == 201
        body = response.json()
        uuid.UUID(body["id"])  # server-generated, valid uuid
        datetime.fromisoformat(body["issued_at"])
        assert body["parameters"] == CREATE_PAYLOAD["parameters"]
        assert body["issuer"] == CREATE_PAYLOAD["issuer"]
        assert body["callback_url"] == CREATE_PAYLOAD["callback_url"]
        assert body["name"] == CREATE_PAYLOAD["name"]
        assert body["being_processed"] is False

    def test_returned_element_matches_stored_element(self, client):
        created = client.post("/api/queue", json=CREATE_PAYLOAD).json()

        fetched = client.get(f"/api/queue/{created['id']}")

        assert fetched.status_code == 200
        assert fetched.json() == created

    def test_minimal_payload_returns_defaults(self, client):
        response = client.post("/api/queue", json={"parameters": {"a": 1}})

        assert response.status_code == 201
        body = response.json()
        assert body["parameters"] == {"a": 1}
        assert body["issuer"] is None
        assert body["callback_url"] is None
        assert body["name"] is None

    def test_missing_parameters_returns_422(self, client, service):
        response = client.post("/api/queue", json={"name": "no-params"})

        assert response.status_code == 422
        assert service.get_queued_simulations() == []


class TestPatchQueue:
    def test_returns_updated_element(self, client):
        created = client.post("/api/queue", json=CREATE_PAYLOAD).json()

        response = client.patch(
            f"/api/queue/{created['id']}",
            json={**CREATE_PAYLOAD, "parameters": {"updated": True}, "name": "renamed"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == created["id"]
        assert body["parameters"] == {"updated": True}
        assert body["name"] == "renamed"

    def test_returns_404_for_unknown_id(self, client):
        response = client.patch(f"/api/queue/{uuid.uuid4()}", json=CREATE_PAYLOAD)

        assert response.status_code == 404
