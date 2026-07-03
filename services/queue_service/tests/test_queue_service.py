import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import mongomock
import pytest

from models.queue_element import QueueElement
from services.queue_service import QueueService


@pytest.fixture
def collection():
    return mongomock.MongoClient().db.queue


@pytest.fixture
def service(collection):
    return QueueService(collection)


def make_element(**overrides) -> QueueElement:
    defaults = {
        "parameters": {"foo": "bar"},
        "issued_at": datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        "issuer": "tester",
        "callback_url": "https://example.com/callback",
    }
    defaults.update(overrides)
    return QueueElement(**defaults)


class TestSaveAndLoad:
    def test_save_then_load_round_trips_fields(self, service):
        element = make_element(name="sim-1", image_id="img-1")

        service.save_queued_simulation(element)
        loaded = service.load_queued_simulation(str(element.id))

        assert loaded is not None
        assert loaded.id == element.id
        assert loaded.parameters == element.parameters
        assert loaded.issued_at == element.issued_at
        assert loaded.issuer == element.issuer
        assert loaded.callback_url == element.callback_url
        assert loaded.name == "sim-1"
        assert loaded.image_id == "img-1"
        assert loaded.being_processed is False
        assert loaded.completed_at is None

    def test_load_missing_returns_none(self, service):
        assert service.load_queued_simulation("does-not-exist") is None

    def test_load_tolerates_missing_optional_fields(self, service, collection):
        # Simulate an older document written without name/image_id.
        legacy_id = str(uuid.uuid4())
        collection.insert_one({
            "id": legacy_id,
            "issued_at": datetime(2024, 1, 1, tzinfo=UTC),
            "completed_at": None,
            "parameters": {},
            "issuer": None,
            "being_processed": False,
            "callback_url": None,
        })

        loaded = service.load_queued_simulation(legacy_id)

        assert loaded is not None
        assert loaded.name is None
        assert loaded.image_id is None

    def test_index_is_not_persisted(self, service, collection):
        element = make_element(index=999)

        service.save_queued_simulation(element)
        stored = collection.find_one({"id": str(element.id)})

        assert "index" not in stored


class TestGetQueuedSimulations:
    def test_empty_collection_returns_empty_list(self, service):
        assert service.get_queued_simulations() == []

    def test_returns_all_in_insertion_order(self, service):
        elements = [make_element(name=f"sim-{i}") for i in range(5)]
        for element in elements:
            service.save_queued_simulation(element)

        results = service.get_queued_simulations()

        assert [r.name for r in results] == [f"sim-{i}" for i in range(5)]


class TestUpdateDeleteComplete:
    def test_update_persists_changes(self, service):
        element = make_element()
        service.save_queued_simulation(element)

        element.being_processed = True
        element.completed_at = datetime(2024, 1, 2, tzinfo=UTC)
        service.update_queued_simulation(element)

        loaded = service.load_queued_simulation(str(element.id))
        assert loaded.being_processed is True
        assert loaded.completed_at == datetime(2024, 1, 2, tzinfo=UTC)

    def test_update_nonexistent_is_a_noop(self, service):
        element = make_element()
        # Never saved; update should not raise or create anything.
        service.update_queued_simulation(element)
        assert service.get_queued_simulations() == []

    def test_delete_removes_element(self, service):
        element = make_element()
        service.save_queued_simulation(element)

        service.delete_queued_simulation(str(element.id))

        assert service.load_queued_simulation(str(element.id)) is None

    def test_delete_does_not_disturb_other_elements(self, service):
        first = make_element(name="first")
        second = make_element(name="second")
        service.save_queued_simulation(first)
        service.save_queued_simulation(second)

        service.delete_queued_simulation(str(first.id))

        remaining = service.get_queued_simulations()
        assert [r.name for r in remaining] == ["second"]

    def test_complete_simulation_removes_element(self, service):
        element = make_element()
        service.save_queued_simulation(element)

        service.complete_simulation(str(element.id))

        assert service.load_queued_simulation(str(element.id)) is None


class TestClaimNextSimulation:
    def test_claim_on_empty_queue_returns_none(self, service):
        assert service.claim_next_simulation() is None

    def test_claim_returns_earliest_unclaimed_and_marks_it(self, service):
        first = make_element(name="first")
        second = make_element(name="second")
        service.save_queued_simulation(first)
        service.save_queued_simulation(second)

        claimed = service.claim_next_simulation()

        assert claimed.name == "first"
        assert claimed.being_processed is True

        stored = service.load_queued_simulation(str(first.id))
        assert stored.being_processed is True

    def test_claim_skips_already_processed(self, service):
        first = make_element(name="first")
        second = make_element(name="second")
        service.save_queued_simulation(first)
        service.save_queued_simulation(second)

        first_claim = service.claim_next_simulation()
        second_claim = service.claim_next_simulation()

        assert first_claim.name == "first"
        assert second_claim.name == "second"

    def test_claim_returns_none_when_all_claimed(self, service):
        element = make_element()
        service.save_queued_simulation(element)

        service.claim_next_simulation()
        result = service.claim_next_simulation()

        assert result is None

    def test_concurrent_claims_never_return_duplicate(self, service):
        """
        Guards against double-claiming: even under concurrent callers,
        find_one_and_update is atomic per-document, so each queued
        element must be claimed by exactly one caller.
        """
        elements = [make_element(name=f"sim-{i}") for i in range(20)]
        for element in elements:
            service.save_queued_simulation(element)

        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(lambda _: service.claim_next_simulation(), range(25)))

        claimed = [r for r in results if r is not None]
        claimed_ids = [c.id for c in claimed]

        # Exactly as many successful claims as elements existed, no duplicates.
        assert len(claimed) == len(elements)
        assert len(set(claimed_ids)) == len(claimed_ids)

        # The 5 extra callers (25 - 20) should have gotten None.
        assert results.count(None) == 5
