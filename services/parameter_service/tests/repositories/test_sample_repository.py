import uuid

import mongomock
import pytest

from models.sample import Sample, SellmeierCoefficients
from repositories.sample_repository import SampleRepository

pytestmark = pytest.mark.unit


def make_coefficients(
    B: list[float] | None = None,
    C: list[float] | None = None,
) -> SellmeierCoefficients:
    return SellmeierCoefficients(
        B=B if B is not None else [1.03961212, 0.23179234, 1.01046945],
        C=C if C is not None else [0.00600069867, 0.0200179144, 103.560653],
    )


def make_sample(name: str = "BK7", **kwargs) -> Sample:
    return Sample(name=name, sellmeier_coefficients=make_coefficients(), **kwargs)


@pytest.fixture
def repository():
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["spectrums"]
    return SampleRepository(collection)


def test_find_all_returns_empty_list_when_no_samples(repository):
    repo = repository
    result = repo.find_all()
    assert result == []


def test_find_all_returns_all_inserted_samples(repository):
    repo = repository
    s1 = make_sample("BK7")
    s2 = make_sample("N-SF11")
    repo.insert(s1)
    repo.insert(s2)

    result = repo.find_all()

    assert len(result) == 2
    ids = {s.id for s in result}
    assert s1.id in ids
    assert s2.id in ids


def test_find_all_returns_list_of_sample_instances(repository):
    repo = repository
    repo.insert(make_sample())

    result = repo.find_all()

    assert all(isinstance(s, Sample) for s in result)


def test_find_all_does_not_return_deleted_samples(repository):
    repo = repository
    s = make_sample()
    repo.insert(s)
    repo.delete(str(s.id))

    result = repo.find_all()

    assert result == []


def test_find_by_id_returns_correct_sample(repository):
    repo = repository
    sample = make_sample("N-BK7")
    repo.insert(sample)

    result = repo.find_by_id(str(sample.id))

    assert result is not None
    assert result.id == sample.id
    assert result.name == "N-BK7"


def test_find_by_id_returns_none_for_unknown_id(repository):
    repo = repository

    result = repo.find_by_id(str(uuid.uuid4()))

    assert result is None


def test_find_by_id_returns_none_after_deletion(repository):
    repo = repository
    sample = make_sample()
    repo.insert(sample)
    repo.delete(str(sample.id))

    result = repo.find_by_id(str(sample.id))

    assert result is None


def test_find_by_id_returns_correct_sample_when_multiple_exist(repository):
    repo = repository
    s1 = make_sample("BK7")
    s2 = make_sample("SF10")
    s3 = make_sample("F2")
    for s in (s1, s2, s3):
        repo.insert(s)

    result = repo.find_by_id(str(s2.id))

    assert result is not None
    assert result.id == s2.id
    assert result.name == "SF10"


def test_find_by_id_preserves_sellmeier_coefficients(repository):
    repo = repository
    coeffs = make_coefficients(B=[0.1, 0.2, 0.3], C=[0.4, 0.5, 0.6])
    sample = Sample(name="Custom", sellmeier_coefficients=coeffs)
    repo.insert(sample)

    result = repo.find_by_id(str(sample.id))

    assert result is not None
    assert result.sellmeier_coefficients.B == [0.1, 0.2, 0.3]
    assert result.sellmeier_coefficients.C == [0.4, 0.5, 0.6]


def test_insert_persists_sample(repository):
    repo = repository
    sample = make_sample()
    repo.insert(sample)

    assert repo.find_by_id(str(sample.id)) is not None


def test_insert_multiple_samples_independently(repository):
    repo = repository
    samples = [make_sample(f"Glass{i}") for i in range(5)]
    for s in samples:
        repo.insert(s)

    assert len(repo.find_all()) == 5


def test_insert_preserves_provided_id(repository):
    repo = repository
    fixed_id = uuid.uuid4()
    sample = Sample(
        id=fixed_id,
        name="FixedID",
        sellmeier_coefficients=make_coefficients(),
    )
    repo.insert(sample)

    result = repo.find_by_id(str(fixed_id))
    assert result is not None
    assert result.id == fixed_id


def test_insert_same_id_twice_raises_or_overwrites(repository):
    """
    Inserting a duplicate ID must either raise an exception or silently
    overwrite — undefined by the interface, but must not silently create
    a duplicate entry visible in find_all.
    """
    repo = repository
    fixed_id = uuid.uuid4()
    s1 = Sample(id=fixed_id, name="First", sellmeier_coefficients=make_coefficients())
    s2 = Sample(id=fixed_id, name="Second", sellmeier_coefficients=make_coefficients())

    repo.insert(s1)
    try:  # noqa: SIM105
        repo.insert(s2)
    except Exception:  # noqa: BLE001
        # Raising is acceptable
        pass

    # Either way, there must be at most one entry for this ID
    all_samples = repo.find_all()
    matching = [s for s in all_samples if s.id == fixed_id]
    assert len(matching) <= 1


def test_update_changes_name(repository):
    repo = repository
    sample = make_sample("OldName")
    repo.insert(sample)

    updated = sample.model_copy(update={"name": "NewName"})
    repo.update(updated)

    result = repo.find_by_id(str(sample.id))
    assert result is not None
    assert result.name == "NewName"


def test_update_changes_sellmeier_coefficients(repository):
    repo = repository
    sample = make_sample()
    repo.insert(sample)

    new_coeffs = make_coefficients(B=[9.9, 8.8, 7.7], C=[6.6, 5.5, 4.4])
    updated = sample.model_copy(update={"sellmeier_coefficients": new_coeffs})
    repo.update(updated)

    result = repo.find_by_id(str(sample.id))
    assert result is not None
    assert result.sellmeier_coefficients.B == [9.9, 8.8, 7.7]
    assert result.sellmeier_coefficients.C == [6.6, 5.5, 4.4]


def test_update_does_not_affect_other_samples(repository):
    repo = repository
    s1 = make_sample("Alpha")
    s2 = make_sample("Beta")
    repo.insert(s1)
    repo.insert(s2)

    updated_s1 = s1.model_copy(update={"name": "Alpha Updated"})
    repo.update(updated_s1)

    s2_result = repo.find_by_id(str(s2.id))
    assert s2_result is not None
    assert s2_result.name == "Beta"


def test_update_nonexistent_sample_raises_or_is_noop(repository):
    """
    Updating an ID that was never inserted must either raise an exception
    or be a silent no-op. It must NOT insert a new record.
    """
    repo = repository
    ghost = make_sample("Ghost")

    try:  # noqa: SIM105
        repo.update(ghost)
    except Exception:  # noqa: BLE001
        pass  # Raising is acceptable

    assert repo.find_by_id(str(ghost.id)) is None
    assert repo.find_all() == []


def test_delete_removes_sample(repository):
    repo = repository
    sample = make_sample()
    repo.insert(sample)

    repo.delete(str(sample.id))

    assert repo.find_by_id(str(sample.id)) is None


def test_delete_reduces_find_all_count(repository):
    repo = repository
    s1 = make_sample("A")
    s2 = make_sample("B")
    repo.insert(s1)
    repo.insert(s2)

    repo.delete(str(s1.id))

    remaining = repo.find_all()
    assert len(remaining) == 1
    assert remaining[0].id == s2.id


def test_delete_only_removes_targeted_sample(repository):
    repo = repository
    samples = [make_sample(f"S{i}") for i in range(3)]
    for s in samples:
        repo.insert(s)

    repo.delete(str(samples[1].id))

    ids = {s.id for s in repo.find_all()}
    assert samples[0].id in ids
    assert samples[1].id not in ids
    assert samples[2].id in ids


def test_delete_nonexistent_id_raises_or_is_noop(repository):
    """
    Deleting an unknown ID must either raise or be a no-op.
    It must not corrupt the existing data.
    """
    repo = repository
    sample = make_sample()
    repo.insert(sample)

    try:  # noqa: SIM105
        repo.delete(str(uuid.uuid4()))
    except Exception:  # noqa: BLE001
        pass  # Raising is acceptable

    # Existing data must be intact
    assert repo.find_by_id(str(sample.id)) is not None


def test_delete_is_idempotent_or_raises_on_second_call(repository):
    """
    Deleting the same ID twice must not crash the repository or corrupt state.
    """
    repo = repository
    sample = make_sample()
    repo.insert(sample)
    repo.delete(str(sample.id))

    try:  # noqa: SIM105
        repo.delete(str(sample.id))
    except Exception:  # noqa: BLE001
        pass  # Raising on second delete is acceptable

    # Repository must still be usable
    assert repo.find_all() == []
