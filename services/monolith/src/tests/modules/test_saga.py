import pytest

from modules.app import saga as saga_module
from modules.app.saga import Saga, SagaAborted, SagaIncomplete, SagaStep

pytestmark = pytest.mark.unit


class Transient(Exception):
    pass


class Permanent(Exception):
    pass


CLEANUP_FAILED = Permanent("cleanup failed")


def is_transient(err: Exception) -> bool:
    return isinstance(err, Transient)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(saga_module.time, "sleep", sleeps.append)
    return sleeps


def failing(exc: Exception, times: int | None = None):
    """Action that raises `exc` `times` times (forever if None), then succeeds."""
    state = {"calls": 0}

    def action(log: list[str]) -> None:
        state["calls"] += 1
        if times is None or state["calls"] <= times:
            raise exc
        log.append("do:flaky")

    action.state = state
    return action


def ok(name: str):
    return lambda log: log.append(f"do:{name}")


def undo(name: str):
    return lambda log, cause: log.append(f"undo:{name}")


def steps(**overrides) -> list[SagaStep[list[str]]]:
    """claim -> simulate -> upload_image -> create_result (pivot) -> dequeue."""
    defaults = {
        "claim": SagaStep("claim", ok("claim"), undo("claim")),
        "simulate": SagaStep("simulate", ok("simulate")),
        "upload_image": SagaStep("upload_image", ok("upload_image"), undo("upload_image")),
        "create_result": SagaStep(
            "create_result", ok("create_result"), undo("create_result"), pivot=True
        ),
        "dequeue": SagaStep("dequeue", ok("dequeue")),
    }
    defaults.update(overrides)
    return list(defaults.values())


def test_happy_path_runs_all_actions_and_no_compensation():
    log: list[str] = []
    Saga(steps(), is_transient).run(log)
    assert log == ["do:claim", "do:simulate", "do:upload_image", "do:create_result", "do:dequeue"]


def test_failure_before_pivot_compensates_attempted_steps_in_reverse():
    log: list[str] = []
    upload = SagaStep("upload_image", failing(Permanent()), undo("upload_image"))

    with pytest.raises(SagaAborted, match="upload_image") as exc:
        Saga(steps(upload_image=upload), is_transient).run(log)

    # the failed step is compensated too: its outcome may be unknown
    assert log == ["do:claim", "do:simulate", "undo:upload_image", "undo:claim"]
    assert isinstance(exc.value.__cause__, Permanent)


def test_failure_at_pivot_compensates_pivot_too():
    log: list[str] = []
    pivot = SagaStep("create_result", failing(Permanent()), undo("create_result"), pivot=True)

    with pytest.raises(SagaAborted, match="create_result"):
        Saga(steps(create_result=pivot), is_transient).run(log)

    assert log[-3:] == ["undo:create_result", "undo:upload_image", "undo:claim"]


def test_failure_after_pivot_raises_incomplete_without_compensation():
    log: list[str] = []
    dequeue = SagaStep("dequeue", failing(Permanent()))

    with pytest.raises(SagaIncomplete, match="dequeue"):
        Saga(steps(dequeue=dequeue), is_transient).run(log)

    assert not any(entry.startswith("undo:") for entry in log)


def test_transient_error_is_retried_with_backoff(no_sleep):
    log: list[str] = []
    flaky = failing(Transient(), times=2)

    Saga(steps(upload_image=SagaStep("upload_image", flaky, retries=3)), is_transient, 1.0).run(log)

    assert flaky.state["calls"] == 3
    assert "do:flaky" in log
    assert no_sleep == [1.0, 2.0]


def test_transient_error_exhausting_retries_aborts():
    log: list[str] = []
    flaky = failing(Transient())
    upload = SagaStep("upload_image", flaky, undo("upload_image"), retries=2)

    with pytest.raises(SagaAborted):
        Saga(steps(upload_image=upload), is_transient).run(log)

    assert flaky.state["calls"] == 3
    assert "undo:upload_image" in log


def test_permanent_error_is_not_retried():
    flaky = failing(Permanent())

    with pytest.raises(SagaAborted):
        Saga(steps(upload_image=SagaStep("upload_image", flaky, retries=3)), is_transient).run([])

    assert flaky.state["calls"] == 1


def test_compensation_receives_the_cause():
    causes: list[Exception] = []
    error = Permanent("boom")
    claim = SagaStep("claim", ok("claim"), lambda log, cause: causes.append(cause))

    with pytest.raises(SagaAborted):
        Saga(
            steps(claim=claim, simulate=SagaStep("simulate", failing(error))), is_transient
        ).run([])

    assert causes == [error]


def test_failing_compensation_does_not_stop_the_others():
    log: list[str] = []

    def broken(log: list[str], cause: Exception) -> None:
        raise CLEANUP_FAILED

    upload = SagaStep("upload_image", ok("upload_image"), broken)
    pivot = SagaStep("create_result", failing(Permanent()), undo("create_result"), pivot=True)

    with pytest.raises(SagaAborted):
        Saga(steps(upload_image=upload, create_result=pivot), is_transient).run(log)

    assert log[-2:] == ["undo:create_result", "undo:claim"]


def test_transient_compensation_error_is_retried():
    calls = {"n": 0}

    def flaky_undo(log: list[str], cause: Exception) -> None:
        calls["n"] += 1
        if calls["n"] < 3:
            raise Transient
        log.append("undo:claim")

    log: list[str] = []
    claim = SagaStep("claim", ok("claim"), flaky_undo)

    with pytest.raises(SagaAborted):
        Saga(
            steps(claim=claim, simulate=SagaStep("simulate", failing(Permanent()))),
            is_transient,
        ).run(log)

    assert calls["n"] == 3
    assert log[-1] == "undo:claim"
