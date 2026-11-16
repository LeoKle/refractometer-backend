import uuid
from datetime import UTC, datetime

import mongomock
import pytest
from pymongo.errors import DuplicateKeyError

from models.simulation_result import SimulationResult
from repositories.simulation_repository import SimulationResultRepository

RESULT_ID = uuid.UUID("c2789555-1d27-4fa4-a042-699b5f21fcd0")

pytestmark = pytest.mark.pact


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


class TestSaveResultIdempotency:
    KEY = "sim-1:create_result"

    def test_save_returns_result(self, repository):
        result = make_result(image_id="image-1")
        assert repository.save_result(result, idempotency_key=self.KEY) == result

    def test_key_stored_on_document(self, repository, collection):
        repository.save_result(make_result(), idempotency_key=self.KEY)
        assert collection.find_one({"id": str(RESULT_ID)})["idempotency_key"] == self.KEY

    def test_replay_returns_first_result(self, repository):
        first = make_result(image_id="image-1")
        repository.save_result(first, idempotency_key=self.KEY)

        replay = make_result(id=uuid.uuid4(), image_id="image-2")
        assert repository.save_result(replay, idempotency_key=self.KEY) == first

    def test_replay_does_not_store_second_document(self, repository, collection):
        repository.save_result(make_result(), idempotency_key=self.KEY)
        repository.save_result(make_result(id=uuid.uuid4()), idempotency_key=self.KEY)
        assert collection.count_documents({}) == 1

    def test_different_keys_store_separately(self, repository, collection):
        repository.save_result(make_result(), idempotency_key="sim-1:create_result")
        repository.save_result(make_result(id=uuid.uuid4()), idempotency_key="sim-2:create_result")
        assert collection.count_documents({}) == 2

    def test_saves_without_key_are_not_deduplicated(self, repository, collection):
        repository.save_result(make_result())
        repository.save_result(make_result(id=uuid.uuid4()))
        assert collection.count_documents({}) == 2

    def test_key_not_part_of_domain_model(self, repository):
        repository.save_result(make_result(), idempotency_key=self.KEY)
        assert "idempotency_key" not in repository.load_result(str(RESULT_ID)).model_dump()

    def test_update_keeps_key(self, repository, collection):
        repository.save_result(make_result(image_id="image-1"), idempotency_key=self.KEY)
        repository.update_result(make_result(image_id="image-2"))
        assert collection.find_one({"id": str(RESULT_ID)})["idempotency_key"] == self.KEY

    def test_delete_frees_key_for_new_result(self, repository):
        # backward recovery: after compensation a retry must store a new result
        repository.save_result(make_result(), idempotency_key=self.KEY)
        repository.delete_result(str(RESULT_ID))

        retry = make_result(id=uuid.uuid4())
        assert repository.save_result(retry, idempotency_key=self.KEY) == retry

    def test_lost_race_returns_winner(self, repository, collection, monkeypatch):
        winner = make_result(image_id="winner")
        real_find = repository._find_by_idempotency_key
        calls = {"n": 0}

        def miss_first(key):
            # first lookup misses, then the concurrent writer inserts the winner
            calls["n"] += 1
            if calls["n"] == 1:
                document = repository._to_collection(winner)
                document["idempotency_key"] = key
                collection.insert_one(document)
                return None
            return real_find(key)

        monkeypatch.setattr(repository, "_find_by_idempotency_key", miss_first)

        loser = make_result(id=uuid.uuid4(), image_id="loser")
        assert repository.save_result(loser, idempotency_key=self.KEY) == winner
        assert collection.count_documents({}) == 1

    def test_unique_index_rejects_duplicate_key(self, repository, collection):
        collection.insert_one({"id": "a", "idempotency_key": "same"})
        with pytest.raises(DuplicateKeyError):
            collection.insert_one({"id": "b", "idempotency_key": "same"})

    def test_index_creation_is_repeatable(self, collection):
        SimulationResultRepository(collection)
        SimulationResultRepository(collection)  # must not raise
