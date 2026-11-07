from unittest.mock import Mock

import pytest

from models.sample import Sample, SellmeierCoefficients
from services.sample_service import SampleService

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_repo():
    return Mock()


@pytest.fixture
def service(mock_repo):
    return SampleService(mock_repo)


@pytest.fixture
def sample():
    return Sample(
        name="BK7",
        sellmeier_coefficients=SellmeierCoefficients(B=[1.0, 2.0, 3.0], C=[4.0, 5.0, 6.0]),
    )


def test_save_sample_returns_inserted_sample(service, mock_repo, sample):
    mock_repo.insert.return_value = sample

    result = service.save_sample(sample)

    assert result == sample
    mock_repo.insert.assert_called_once_with(sample)


def test_update_sample_returns_updated_sample(service, mock_repo, sample):
    mock_repo.update.return_value = sample

    result = service.update_sample(sample)

    assert result == sample
    mock_repo.update.assert_called_once_with(sample)
