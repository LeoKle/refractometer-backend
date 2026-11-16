import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.controllers.v1 import simulation_controller
from containers.container import DependencyContainer
from models.simulation_result import SimulationResult

pytestmark = pytest.mark.unit

STORED_ID = uuid.UUID("c2789555-1d27-4fa4-a042-699b5f21fcd0")


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    # by default save_result returns the result it was given (no replay)
    repo.save_result.side_effect = lambda result, idempotency_key=None: result
    return repo


@pytest.fixture
def client(mock_repo):
    container = DependencyContainer()
    container.sim_result_repository.override(mock_repo)

    app = FastAPI()
    app.container = container
    app.include_router(simulation_controller.router, prefix="/api")
    container.wire(modules=[simulation_controller])
    yield TestClient(app)
    container.unwire()


def payload() -> dict:
    now = datetime.now(UTC).isoformat()
    return {"parameters": {}, "image_id": "image-1", "issued_at": now, "completed_at": now}


class TestPostResult:
    def test_returns_200(self, client):
        assert client.post("/api/result", json=payload()).status_code == 200

    def test_idempotency_key_defaults_to_none(self, client, mock_repo):
        client.post("/api/result", json=payload())
        assert mock_repo.save_result.call_args.kwargs["idempotency_key"] is None

    def test_idempotency_key_passed_from_header(self, client, mock_repo):
        client.post(
            "/api/result", json=payload(), headers={"Idempotency-Key": "sim-1:create_result"}
        )
        assert mock_repo.save_result.call_args.kwargs["idempotency_key"] == "sim-1:create_result"

    def test_returns_stored_result_for_repeated_key(self, client, mock_repo):
        # replay: the repository hands back the result stored first
        now = datetime.now(UTC)
        mock_repo.save_result.side_effect = None
        mock_repo.save_result.return_value = SimulationResult(
            id=STORED_ID, parameters={}, image_id="image-0", issued_at=now, completed_at=now
        )

        response = client.post(
            "/api/result", json=payload(), headers={"Idempotency-Key": "sim-1:create_result"}
        )

        saved: SimulationResult = mock_repo.save_result.call_args.args[0]
        assert saved.id != STORED_ID
        assert response.json()["id"] == str(STORED_ID)
        assert response.json()["image_id"] == "image-0"
