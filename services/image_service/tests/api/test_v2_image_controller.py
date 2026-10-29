import io
import uuid
from unittest.mock import MagicMock

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.v2.image_controller import image_v2_router
from containers.container import DependencyContainer
from interfaces.image_repository_interface import ImageRepositoryInterface
from models.raw_image import RawImage

CONTROLLER_MODULE = "api.controllers.v2.image_controller"


class FakeImageRepository(ImageRepositoryInterface):
    def __init__(self):
        self.store: dict[uuid.UUID, tuple[bytes, tuple[int, int], str]] = {}

    def save_raw(self, image_id, data, shape, dtype):
        expected = shape[0] * shape[1] * np.dtype(dtype).itemsize
        if len(data) != expected:
            msg = f"Expected {expected} bytes, got {len(data)}"
            raise ValueError(msg)
        self.store[image_id] = (data, shape, dtype)

    def open_raw(self, image_id):
        if image_id not in self.store:
            msg = f"Image with id {image_id} not found"
            raise FileNotFoundError(msg)
        data, shape, dtype = self.store[image_id]
        return RawImage(io.BytesIO(data), shape, dtype, len(data))

    def get_image(self, id): ...
    def save_image(self, detector_image): ...


@pytest.fixture
def repo():
    return FakeImageRepository()


def make_app(repo: MagicMock) -> FastAPI:
    """Wire a fresh FastAPI app with the mock repo injected via the container."""
    container = DependencyContainer()
    container.image_repo.override(repo)

    app = FastAPI()
    app.container = container
    app.include_router(image_v2_router)
    container.wire(modules=["api.v2.image_controller"])
    return app


@pytest.fixture
def client(repo):
    app = make_app(repo)
    return TestClient(app)


def _headers(shape, dtype):
    return {
        "Content-Type": "application/octet-stream",
        "X-Image-Shape": f"{shape[0]},{shape[1]}",
        "X-Image-Dtype": dtype,
    }


class TestPostRaw:
    def test_returns_201_and_valid_uuid(self, client):
        arr = np.ones((4, 5), dtype=np.float32)
        r = client.post(
            "/api/v2/image", content=arr.tobytes(), headers=_headers(arr.shape, "float32")
        )
        assert r.status_code == 201
        uuid.UUID(r.json()["id"])

    def test_bytes_are_stored_unchanged(self, client, repo):
        arr = np.arange(20, dtype=np.uint16).reshape(4, 5)
        r = client.post(
            "/api/v2/image", content=arr.tobytes(), headers=_headers(arr.shape, "uint16")
        )
        data, shape, dtype = repo.store[uuid.UUID(r.json()["id"])]
        assert data == arr.tobytes() and shape == (4, 5) and dtype == "uint16"

    def test_wrong_body_size_returns_422(self, client):
        r = client.post("/api/v2/image", content=b"\x00" * 7, headers=_headers((2, 2), "float32"))
        assert r.status_code == 422

    @pytest.mark.parametrize("shape", ["abc", "2560", "0,10", "-1,5", "1,2,3"])
    def test_invalid_shape_header_returns_400(self, client, shape):
        r = client.post(
            "/api/v2/image",
            content=b"",
            headers={"Content-Type": "application/octet-stream", "X-Image-Shape": shape},
        )
        assert r.status_code == 400


class TestGetRaw:
    def test_round_trip_through_api(self, client):
        arr = np.random.default_rng(0).random((6, 7)).astype(np.float32)
        image_id = client.post(
            "/api/v2/image", content=arr.tobytes(), headers=_headers(arr.shape, "float32")
        ).json()["id"]

        r = client.get(f"/api/v2/image/{image_id}")

        assert r.status_code == 200
        assert r.headers["content-type"] == "application/octet-stream"
        assert r.headers["x-image-shape"] == "6,7"
        assert r.headers["x-image-dtype"] == "float32"
        assert int(r.headers["content-length"]) == arr.nbytes
        recovered = np.frombuffer(r.content, dtype=r.headers["x-image-dtype"]).reshape(6, 7)
        np.testing.assert_array_equal(recovered, arr)

    def test_unknown_id_returns_404(self, client):
        assert client.get(f"/api/v2/image/{uuid.uuid4()}").status_code == 404

    def test_invalid_uuid_returns_400(self, client):
        assert client.get("/api/v2/image/not-a-uuid").status_code == 400
