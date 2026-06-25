import uuid

import mongomock
import pytest

from models.spectrum import Spectrum
from repositories.spectrum_repository import SpectrumRepository

pytestmark = pytest.mark.unit

SPECTRUM_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")

SAMPLE_DOC = {
    "id": str(SPECTRUM_ID),
    "name": "Test Spectrum",
    "wavelengths": [400.0, 500.0, 600.0],
    "intensities": [0.1, 0.5, 0.9],
}

SAMPLE_SPECTRUM = Spectrum(
    id=SPECTRUM_ID,
    name="Test Spectrum",
    wavelengths=[400.0, 500.0, 600.0],
    intensities=[0.1, 0.5, 0.9],
)


@pytest.fixture
def repo():
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["spectrums"]
    return SpectrumRepository(collection)


class TestDocToDomain:
    def test_converts_valid_doc(self, repo):
        result = repo._doc_to_domain(SAMPLE_DOC)
        assert result.id == SAMPLE_SPECTRUM.id
        assert result.name == SAMPLE_SPECTRUM.name
        assert result.wavelengths == SAMPLE_SPECTRUM.wavelengths
        assert result.intensities == SAMPLE_SPECTRUM.intensities

    def test_returns_spectrum_instance(self, repo):
        assert isinstance(repo._doc_to_domain(SAMPLE_DOC), Spectrum)


class TestDomainToDoc:
    def test_id_is_string(self, repo):
        doc = repo._domain_to_doc(SAMPLE_SPECTRUM)
        assert isinstance(doc["id"], str)

    def test_round_trips_all_fields(self, repo):
        doc = repo._domain_to_doc(SAMPLE_SPECTRUM)
        assert doc["id"] == str(SAMPLE_SPECTRUM.id)
        assert doc["name"] == SAMPLE_SPECTRUM.name
        assert doc["wavelengths"] == SAMPLE_SPECTRUM.wavelengths
        assert doc["intensities"] == SAMPLE_SPECTRUM.intensities


class TestFindAll:
    def test_empty_collection(self, repo):
        assert repo.find_all() == []

    def test_returns_spectrums(self, repo):
        repo.collection.insert_one(SAMPLE_DOC.copy())
        result = repo.find_all()
        assert len(result) == 1
        assert result[0].id == SPECTRUM_ID

    def test_returns_multiple(self, repo):
        second_doc = {**SAMPLE_DOC, "id": str(uuid.uuid4()), "name": "Second"}
        repo.collection.insert_one(SAMPLE_DOC.copy())
        repo.collection.insert_one(second_doc)
        assert len(repo.find_all()) == 2


class TestFindById:
    def test_returns_spectrum_when_found(self, repo):
        repo.collection.insert_one(SAMPLE_DOC.copy())
        result = repo.find_by_id(SPECTRUM_ID)
        assert result is not None
        assert result.id == SPECTRUM_ID

    def test_returns_none_when_missing(self, repo):
        assert repo.find_by_id(uuid.uuid4()) is None

    def test_returns_correct_spectrum_among_many(self, repo):
        other_doc = {**SAMPLE_DOC, "id": str(uuid.uuid4()), "name": "Other"}
        repo.collection.insert_one(SAMPLE_DOC.copy())
        repo.collection.insert_one(other_doc)
        result = repo.find_by_id(SPECTRUM_ID)
        assert result.name == SAMPLE_SPECTRUM.name


class TestInsert:
    def test_returns_same_spectrum(self, repo):
        result = repo.insert(SAMPLE_SPECTRUM)
        assert result.id == SAMPLE_SPECTRUM.id

    def test_persists_to_collection(self, repo):
        repo.insert(SAMPLE_SPECTRUM)
        doc = repo.collection.find_one({"id": str(SPECTRUM_ID)})
        assert doc is not None
        assert doc["name"] == SAMPLE_SPECTRUM.name

    def test_document_has_correct_fields(self, repo):
        repo.insert(SAMPLE_SPECTRUM)
        doc = repo.collection.find_one({"id": str(SPECTRUM_ID)})
        assert doc["wavelengths"] == SAMPLE_SPECTRUM.wavelengths
        assert doc["intensities"] == SAMPLE_SPECTRUM.intensities


class TestUpdate:
    def test_returns_updated_spectrum(self, repo):
        repo.collection.insert_one(SAMPLE_DOC.copy())
        updated = Spectrum(id=SPECTRUM_ID, name="Updated", wavelengths=[700.0], intensities=[1.0])
        result = repo.update(updated)
        assert result.name == "Updated"

    def test_persists_changes(self, repo):
        repo.collection.insert_one(SAMPLE_DOC.copy())
        updated = Spectrum(id=SPECTRUM_ID, name="Updated", wavelengths=[700.0], intensities=[1.0])
        repo.update(updated)
        doc = repo.collection.find_one({"id": str(SPECTRUM_ID)})
        assert doc["name"] == "Updated"
        assert doc["wavelengths"] == [700.0]

    def test_does_not_affect_other_documents(self, repo):
        other_id = uuid.uuid4()
        other_doc = {**SAMPLE_DOC, "id": str(other_id), "name": "Other"}
        repo.collection.insert_one(SAMPLE_DOC.copy())
        repo.collection.insert_one(other_doc)
        updated = Spectrum(id=SPECTRUM_ID, name="Updated", wavelengths=[700.0], intensities=[1.0])
        repo.update(updated)
        other = repo.collection.find_one({"id": str(other_id)})
        assert other["name"] == "Other"


class TestDelete:
    def test_returns_true_when_deleted(self, repo):
        repo.collection.insert_one(SAMPLE_DOC.copy())
        assert repo.delete(SPECTRUM_ID) is True

    def test_returns_false_when_not_found(self, repo):
        assert repo.delete(uuid.uuid4()) is False

    def test_removes_document_from_collection(self, repo):
        repo.collection.insert_one(SAMPLE_DOC.copy())
        repo.delete(SPECTRUM_ID)
        assert repo.collection.find_one({"id": str(SPECTRUM_ID)}) is None

    def test_does_not_remove_other_documents(self, repo):
        other_id = uuid.uuid4()
        other_doc = {**SAMPLE_DOC, "id": str(other_id), "name": "Other"}
        repo.collection.insert_one(SAMPLE_DOC.copy())
        repo.collection.insert_one(other_doc)
        repo.delete(SPECTRUM_ID)
        assert repo.collection.find_one({"id": str(other_id)}) is not None
