import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.controllers.image_controller import router
from containers.container import DependencyContainer
from models.detector_image import DetectorImage

SHAPE = (2, 2)
VALUES = [[1.0, 2.0], [3.0, 4.0]]
FIXED_ID = uuid.uuid4()


def make_detector_image(id: uuid.UUID = FIXED_ID) -> DetectorImage:
    return DetectorImage(id=id, values=VALUES, shape=SHAPE)


def make_app(mock_repo: MagicMock) -> FastAPI:
    """Wire a fresh FastAPI app with the mock repo injected via the container."""
    container = DependencyContainer()
    container.image_repo.override(mock_repo)

    app = FastAPI()
    app.container = container
    app.include_router(router)
    container.wire(modules=["api.controllers.image_controller"])
    return app


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def client(mock_repo):
    app = make_app(mock_repo)
    return TestClient(app)


class TestGetImage:
    def test_returns_200_for_existing_image(self, client, mock_repo):
        mock_repo.get_image.return_value = make_detector_image()
        response = client.get(f"/image/{FIXED_ID}")
        assert response.status_code == 200

    def test_response_contains_values(self, client, mock_repo):
        mock_repo.get_image.return_value = make_detector_image()
        response = client.get(f"/image/{FIXED_ID}")
        assert response.json()["values"] == VALUES

    def test_response_contains_shape(self, client, mock_repo):
        mock_repo.get_image.return_value = make_detector_image()
        response = client.get(f"/image/{FIXED_ID}")
        assert tuple(response.json()["shape"]) == SHAPE

    def test_calls_repo_with_correct_uuid(self, client, mock_repo):
        mock_repo.get_image.return_value = make_detector_image()
        client.get(f"/image/{FIXED_ID}")
        mock_repo.get_image.assert_called_once_with(FIXED_ID)

    def test_returns_404_when_image_not_found(self, client, mock_repo):
        mock_repo.get_image.side_effect = FileNotFoundError("not found")
        response = client.get(f"/image/{FIXED_ID}")
        assert response.status_code == 404

    def test_404_detail_contains_image_id(self, client, mock_repo):
        mock_repo.get_image.side_effect = FileNotFoundError("not found")
        response = client.get(f"/image/{FIXED_ID}")
        assert str(FIXED_ID) in response.json()["detail"]

    def test_returns_400_for_malformed_uuid(self, client, mock_repo):
        response = client.get("/image/not-a-uuid")
        assert response.status_code == 400

    def test_400_detail_contains_bad_value(self, client, mock_repo):
        response = client.get("/image/not-a-uuid")
        assert "not-a-uuid" in response.json()["detail"]

    def test_repo_not_called_for_malformed_uuid(self, client, mock_repo):
        client.get("/image/not-a-uuid")
        mock_repo.get_image.assert_not_called()


class TestPostImage:
    def _payload(self):
        return {"values": VALUES, "shape": list(SHAPE)}

    def test_returns_201_on_success(self, client, mock_repo):
        response = client.post("/image", json=self._payload())
        assert response.status_code == 201

    def test_response_contains_generated_id_string(self, client, mock_repo):
        response = client.post("/image", json=self._payload())

        saved_image: DetectorImage = mock_repo.save_image.call_args[0][0]

        assert response.json()["id"] == str(saved_image.id)

    def test_repo_called_once(self, client, mock_repo):
        client.post("/image", json=self._payload())
        mock_repo.save_image.assert_called_once()

    def test_repo_receives_detector_image(self, client, mock_repo):
        client.post("/image", json=self._payload())

        arg: DetectorImage = mock_repo.save_image.call_args[0][0]
        assert isinstance(arg, DetectorImage)

    def test_repo_receives_generated_uuid(self, client, mock_repo):
        client.post("/image", json=self._payload())

        arg: DetectorImage = mock_repo.save_image.call_args[0][0]
        assert isinstance(arg.id, uuid.UUID)

    def test_repo_receives_correct_values(self, client, mock_repo):
        client.post("/image", json=self._payload())

        arg: DetectorImage = mock_repo.save_image.call_args[0][0]
        assert arg.values == VALUES

    def test_repo_receives_correct_shape(self, client, mock_repo):
        client.post("/image", json=self._payload())

        arg: DetectorImage = mock_repo.save_image.call_args[0][0]
        assert arg.shape == SHAPE

    def test_returns_422_when_values_missing(self, client, mock_repo):
        response = client.post("/image", json={"shape": [2, 2]})
        assert response.status_code == 422

    def test_returns_422_when_body_empty(self, client, mock_repo):
        response = client.post("/image", json={})
        assert response.status_code == 422

    def test_id_in_response_is_valid_uuid(self, client, mock_repo):
        response = client.post("/image", json=self._payload())

        uuid.UUID(response.json()["id"])  # raises if invalid
