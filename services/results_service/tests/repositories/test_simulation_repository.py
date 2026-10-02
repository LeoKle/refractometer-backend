import uuid
from datetime import UTC, datetime

import mongomock
import pytest

from models.simulation_result import SimulationResult
from repositories.simulation_repository import SimulationResultRepository

RESULT_ID = uuid.UUID("c2789555-1d27-4fa4-a042-699b5f21fcd0")


@pytest.fixture
def collection():
    return mongomock.MongoClient().db.results


@pytest.fixture
def repository(collection):
    return SimulationResultRepository(collection)


def make_result(**overrides) -> SimulationResult:
    defaults = {
        "id": RESULT_ID,
        "parameters": {},
        "image_id": None,
        "issued_at": datetime.now(UTC),
        "completed_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return SimulationResult(**defaults)


class TestSimulationResultRepository:
    def test_get_results_returns_all_results(self, repository):
        result_1 = make_result()
        result_2 = make_result(id=uuid.uuid4(), parameters={"foo": "bar"})

        repository.collection.insert_many([
            repository._to_collection(result_1),
            repository._to_collection(result_2),
        ])

        results = repository.get_results()

        assert len(results) == 2
        assert result_1 in results
        assert result_2 in results

    def test_get_results_returns_empty_list_when_no_results(self, repository):
        results = repository.get_results()

        assert results == []

    def test_load_result_returns_result(self, repository):
        result = make_result()
        repository.collection.insert_one(repository._to_collection(result))

        loaded = repository.load_result(str(result.id))

        assert loaded == result

    def test_load_result_returns_none_when_result_does_not_exist(self, repository):
        loaded = repository.load_result(str(RESULT_ID))

        assert loaded is None

    def test_save_result_persists_result(self, repository):
        result = make_result(
            parameters={"iterations": 100, "seed": 42},
            image_id="image-123",
        )

        repository.save_result(result)

        document = repository.collection.find_one({"id": str(result.id)})

        assert document is not None
        assert document["id"] == str(result.id)
        assert document["parameters"] == result.parameters
        assert document["image_id"] == result.image_id

    def test_save_result_can_be_loaded_again(self, repository):
        result = make_result(parameters={"iterations": 100})

        repository.save_result(result)

        loaded = repository.load_result(str(result.id))

        assert loaded == result

    def test_update_result_updates_existing_result(self, repository):
        result = make_result(parameters={"iterations": 100})
        repository.save_result(result)

        updated = result.model_copy(
            update={
                "parameters": {"iterations": 200},
                "image_id": "new-image",
            }
        )

        repository.update_result(updated)

        loaded = repository.load_result(str(result.id))

        assert loaded == updated

    def test_update_result_does_not_create_new_result(self, repository):
        result = make_result(parameters={"iterations": 100})

        repository.update_result(result)

        assert repository.get_results() == []

    def test_delete_result_deletes_existing_result(self, repository):
        result = make_result()
        repository.save_result(result)

        repository.delete_result(str(result.id))

        assert repository.load_result(str(result.id)) is None
        assert repository.get_results() == []

    def test_delete_result_does_nothing_for_missing_result(self, repository):
        repository.delete_result(str(RESULT_ID))

        assert repository.get_results() == []

    def test_to_collection_serializes_result(self, repository):
        result = make_result(
            parameters={"foo": "bar"},
            image_id="image-123",
        )

        document = repository._to_collection(result)
        expected = result.model_dump(mode="json")

        assert document == expected

    def test_to_domain_creates_simulation_result(self, repository):
        result = make_result()
        document = repository._to_collection(result)

        restored = repository._to_domain(document)

        assert restored == result
