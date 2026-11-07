import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from interfaces.services.sample_service_interface import ISampleService
from models.sample import Sample, SellmeierCoefficients

pytestmark = pytest.mark.unit

SAMPLE_ID = uuid.uuid4()

SAMPLE = Sample(
    id=SAMPLE_ID,
    name="BK7",
    sellmeier_coefficients=SellmeierCoefficients(B=[1.0, 2.0, 3.0], C=[4.0, 5.0, 6.0]),
)

SAMPLE_JSON = {
    "id": str(SAMPLE_ID),
    "name": "BK7",
    "sellmeier_coefficients": {"B": [1.0, 2.0, 3.0], "C": [4.0, 5.0, 6.0]},
}


@pytest.fixture()
def mock_service() -> MagicMock:
    return MagicMock(spec=ISampleService)


@pytest.fixture()
def client(mock_service: MagicMock) -> TestClient:
    from api.controllers.v1.sample_controller import router
    from containers.container import DependencyContainer

    app = FastAPI()
    app.include_router(router)

    container = DependencyContainer()
    container.sample_service.override(mock_service)
    container.wire(modules=["api.controllers.v1.sample_controller"])

    return TestClient(app)


class TestPostSample:
    def test_returns_created_sample(self, client, mock_service):
        mock_service.save_sample.side_effect = lambda sample: sample

        response = client.post("/sample", json=SAMPLE_JSON)

        assert response.status_code == 200
        assert response.json() == SAMPLE_JSON

    def test_returns_generated_id_when_none_given(self, client, mock_service):
        mock_service.save_sample.side_effect = lambda sample: sample
        payload = {k: v for k, v in SAMPLE_JSON.items() if k != "id"}

        response = client.post("/sample", json=payload)

        assert response.status_code == 200
        body = response.json()
        saved: Sample = mock_service.save_sample.call_args.args[0]
        assert body["id"] == str(saved.id)
        uuid.UUID(body["id"])  # valid uuid
        assert body["name"] == "BK7"

    def test_missing_required_fields_returns_422(self, client, mock_service):
        response = client.post("/sample", json={"name": "Incomplete"})
        assert response.status_code == 422
        mock_service.save_sample.assert_not_called()


class TestPatchSample:
    def test_returns_updated_sample(self, client, mock_service):
        mock_service.update_sample.return_value = SAMPLE

        response = client.patch("/sample", json=SAMPLE_JSON)

        assert response.status_code == 200
        assert response.json() == SAMPLE_JSON
        updated: Sample = mock_service.update_sample.call_args.args[0]
        assert updated.id == SAMPLE_ID

    def test_returns_400_when_id_missing(self, client, mock_service):
        payload = {k: v for k, v in SAMPLE_JSON.items() if k != "id"}

        response = client.patch("/sample", json=payload)

        assert response.status_code == 400
        mock_service.update_sample.assert_not_called()
