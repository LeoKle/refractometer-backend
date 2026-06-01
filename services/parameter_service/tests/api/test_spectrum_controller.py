import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.models.spectrum_dto import SpectrumDTO
from interfaces.services.spectrum_service_interface import SpectrumServiceInterface
from models.spectrum import Spectrum

SPECTRUM_ID = uuid.uuid4()

SAMPLE_SPECTRUM = Spectrum(
    id=SPECTRUM_ID,
    name="Test Spectrum",
    wavelengths=[400.0, 500.0, 600.0],
    intensities=[0.1, 0.5, 0.9],
)

SAMPLE_DTO = SpectrumDTO(
    id=SPECTRUM_ID,
    name="Test Spectrum",
    wavelengths=[400.0, 500.0, 600.0],
    intensities=[0.1, 0.5, 0.9],
)


def make_client(mock_service: SpectrumServiceInterface) -> TestClient:
    from api.controllers.v1.spectrum_controller import router
    from containers.container import DependencyContainer

    app = FastAPI()
    app.include_router(router)

    container = DependencyContainer()
    container.spectrum_service.override(mock_service)
    container.wire(modules=["api.controllers.v1.spectrum_controller"])

    return TestClient(app)


@pytest.fixture()
def mock_service() -> MagicMock:
    svc = MagicMock(spec=SpectrumServiceInterface)
    return svc


@pytest.fixture()
def client(mock_service: MagicMock) -> TestClient:
    return make_client(mock_service)


class TestGetAllSpectrums:
    def test_returns_empty_list(self, client, mock_service):
        mock_service.get_spectrums.return_value = []

        response = client.get("/spectrums")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_list_of_spectrums(self, client, mock_service):
        mock_service.get_spectrums.return_value = [SAMPLE_SPECTRUM]

        response = client.get("/spectrums")

        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["name"] == "Test Spectrum"
        assert body[0]["id"] == str(SPECTRUM_ID)

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_spectrums.return_value = []
        client.get("/spectrums")
        mock_service.get_spectrums.assert_called_once()


class TestGetSpectrum:
    def test_returns_spectrum_when_found(self, client, mock_service):
        mock_service.get_spectrum.return_value = SAMPLE_SPECTRUM

        response = client.get(f"/spectrum/{SPECTRUM_ID}")

        assert response.status_code == 200
        assert response.json()["id"] == str(SPECTRUM_ID)
        assert response.json()["name"] == "Test Spectrum"

    def test_returns_404_when_not_found(self, client, mock_service):
        mock_service.get_spectrum.return_value = None

        response = client.get(f"/spectrum/{SPECTRUM_ID}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Spectrum not found"

    def test_calls_service_with_correct_id(self, client, mock_service):
        mock_service.get_spectrum.return_value = SAMPLE_SPECTRUM
        client.get(f"/spectrum/{SPECTRUM_ID}")
        mock_service.get_spectrum.assert_called_once_with(SPECTRUM_ID)

    def test_invalid_uuid_returns_422(self, client, mock_service):
        response = client.get("/spectrum/not-a-uuid")
        assert response.status_code == 422


class TestPostSpectrum:
    def test_creates_spectrum_successfully(self, client, mock_service):
        payload = SAMPLE_DTO.model_dump(mode="json")

        response = client.post("/spectrum", json=payload)

        assert response.status_code == 201
        assert response.json()["message"] == "Spectrum created successfully"

    def test_calls_save_spectrum(self, client, mock_service):
        payload = SAMPLE_DTO.model_dump(mode="json")
        client.post("/spectrum", json=payload)
        mock_service.save_spectrum.assert_called_once()

    def test_missing_required_fields_returns_422(self, client, mock_service):
        response = client.post("/spectrum", json={"name": "Incomplete"})
        assert response.status_code == 422


class TestPatchSpectrum:
    def test_updates_spectrum_successfully(self, client, mock_service):
        mock_service.update_spectrum.return_value = SAMPLE_SPECTRUM
        payload = SAMPLE_DTO.model_dump(mode="json")

        response = client.patch("/spectrum", json=payload)

        assert response.status_code == 200
        assert response.json()["id"] == str(SPECTRUM_ID)

    def test_returns_400_when_id_missing(self, client, mock_service):
        payload = {
            "name": "No ID",
            "wavelengths": [400.0],
            "intensities": [0.5],
        }  # id omitted → None

        response = client.patch("/spectrum", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid request data"

    def test_calls_update_with_spectrum(self, client, mock_service):
        mock_service.update_spectrum.return_value = SAMPLE_SPECTRUM
        payload = SAMPLE_DTO.model_dump(mode="json")
        client.patch("/spectrum", json=payload)
        mock_service.update_spectrum.assert_called_once()


class TestDeleteSpectrum:
    def test_deletes_spectrum_successfully(self, client, mock_service):
        mock_service.delete_spectrum.return_value = True

        response = client.delete(f"/spectrum/{SPECTRUM_ID}")

        assert response.status_code == 200
        assert response.json()["message"] == "Spectrum deleted successfully"

    def test_returns_404_when_not_found(self, client, mock_service):
        mock_service.delete_spectrum.return_value = False

        response = client.delete(f"/spectrum/{SPECTRUM_ID}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Spectrum does not exist"

    def test_calls_service_with_correct_id(self, client, mock_service):
        mock_service.delete_spectrum.return_value = True
        client.delete(f"/spectrum/{SPECTRUM_ID}")
        mock_service.delete_spectrum.assert_called_once_with(SPECTRUM_ID)

    def test_invalid_uuid_returns_422(self, client, mock_service):
        response = client.delete("/spectrum/not-a-uuid")
        assert response.status_code == 422
