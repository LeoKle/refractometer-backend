import uuid
from unittest.mock import Mock

import pytest

from models.spectrum import Spectrum
from services.spectrum_service import SpectrumService

pytestmark = pytest.mark.unit

@pytest.fixture
def mock_repo():
    return Mock()


@pytest.fixture
def service(mock_repo):
    return SpectrumService(mock_repo)


@pytest.fixture
def spectrum():
    return Spectrum(
        id=uuid.uuid4(),
        name="Test Spectrum",
        wavelengths=[400.0, 500.0, 600.0],
        intensities=[0.1, 0.5, 0.9],
    )


def test_get_spectrums_returns_all_spectrums(service, mock_repo, spectrum):
    mock_repo.find_all.return_value = [spectrum]

    result = service.get_spectrums()

    assert result == [spectrum]
    mock_repo.find_all.assert_called_once_with()


def test_get_spectrum_returns_spectrum_when_found(service, mock_repo, spectrum):
    mock_repo.find_by_id.return_value = spectrum

    result = service.get_spectrum(spectrum.id)

    assert result == spectrum
    mock_repo.find_by_id.assert_called_once_with(spectrum.id)


def test_get_spectrum_returns_none_when_not_found(service, mock_repo):
    spectrum_id = uuid.uuid4()

    mock_repo.find_by_id.return_value = None

    result = service.get_spectrum(spectrum_id)

    assert result is None
    mock_repo.find_by_id.assert_called_once_with(spectrum_id)


def test_save_spectrum_calls_repository_insert(service, mock_repo, spectrum):
    mock_repo.insert.return_value = spectrum

    result = service.save_spectrum(spectrum)

    assert result == spectrum
    mock_repo.insert.assert_called_once_with(spectrum)


def test_update_spectrum_updates_existing_spectrum(service, mock_repo, spectrum):
    mock_repo.find_by_id.return_value = spectrum
    mock_repo.update.return_value = spectrum

    result = service.update_spectrum(spectrum)

    assert result == spectrum

    mock_repo.find_by_id.assert_called_once_with(spectrum.id)
    mock_repo.update.assert_called_once_with(spectrum)


def test_update_spectrum_raises_when_spectrum_not_found(service, mock_repo, spectrum):
    mock_repo.find_by_id.return_value = None

    with pytest.raises(ValueError) as exc:
        service.update_spectrum(spectrum)

    assert str(exc.value) == (f"Spectrum with id {spectrum.id} not found")

    mock_repo.find_by_id.assert_called_once_with(spectrum.id)
    mock_repo.update.assert_not_called()


def test_delete_spectrum_returns_true_when_deleted(service, mock_repo):
    spectrum_id = uuid.uuid4()

    mock_repo.delete.return_value = True

    result = service.delete_spectrum(spectrum_id)

    assert result is True
    mock_repo.delete.assert_called_once_with(spectrum_id)


def test_delete_spectrum_returns_false_when_not_deleted(service, mock_repo):
    spectrum_id = uuid.uuid4()

    mock_repo.delete.return_value = False

    result = service.delete_spectrum(spectrum_id)

    assert result is False
    mock_repo.delete.assert_called_once_with(spectrum_id)
