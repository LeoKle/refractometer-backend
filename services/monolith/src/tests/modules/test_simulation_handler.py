import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, call

import pytest
from refractometer_common.image import (
    ImageClientConnectionException,
    ImageClientException,
    ImageClientInterface,
    ImageNotFoundException,
)
from refractometer_common.queue import (
    QueueClientConnectionException,
    QueueClientElementNotFoundException,
    QueueClientInterface,
    SimulationQueueElement,
)
from refractometer_common.result import (
    SimulationResult,
    SimulationResultClientConnectionException,
    SimulationResultClientException,
    SimulationResultClientInterface,
)

from custom_types.detector_image import DetectorImage
from interfaces.app.simulation_interface import ISimulation
from modules.app import saga as saga_module
from modules.app import simulation_handler as handler_module
from modules.app.simulation_handler import SimulationHandler, is_transient

pytestmark = pytest.mark.unit

ELEMENT_ID = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
IMAGE_ID = "6f1c2f8e-2b5c-4d0e-9a57-0d6f3a1d9c11"
RESULT_ID = uuid.UUID("0b9c5f4a-7d3e-4a8b-8f21-5c1e9d2a7b33")
IMAGE_KEY = f"{ELEMENT_ID}:upload_image"
RESULT_KEY = f"{ELEMENT_ID}:create_result"
EMPTY_QUEUE = QueueClientElementNotFoundException("No queued simulations available", 404)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(saga_module.time, "sleep", lambda _: None)
    monkeypatch.setattr(handler_module.time, "sleep", lambda _: None)


@pytest.fixture
def element() -> SimulationQueueElement:
    return SimulationQueueElement(
        id=ELEMENT_ID,
        parameters={"foo": "bar"},
        issued_at=datetime(2026, 11, 1, tzinfo=UTC),
        attempts=1,
    )


@pytest.fixture
def simulation() -> MagicMock:
    sim = MagicMock(spec=ISimulation)
    sim.get_detector_image.return_value = DetectorImage(values=[[1.0, 2.0]], shape=(1, 2))
    return sim


@pytest.fixture
def queue() -> MagicMock:
    return MagicMock(spec=QueueClientInterface)


@pytest.fixture
def images() -> MagicMock:
    client = MagicMock(spec=ImageClientInterface)
    client.create_image.return_value = IMAGE_ID
    return client


@pytest.fixture
def results() -> MagicMock:
    client = MagicMock(spec=SimulationResultClientInterface)
    client.create_result.return_value = SimulationResult(
        id=RESULT_ID,
        parameters={"foo": "bar"},
        image_id=IMAGE_ID,
        issued_at=datetime(2026, 11, 1, tzinfo=UTC),
        completed_at=datetime(2026, 11, 1, 0, 5, tzinfo=UTC),
    )
    return client


@pytest.fixture
def handler(simulation, queue, images, results) -> SimulationHandler:
    return SimulationHandler(simulation, queue, images, results, retries=2, backoff_seconds=0)


def released_error(queue: MagicMock) -> str:
    queue.release_element.assert_called_once()
    assert queue.release_element.call_args.args == (ELEMENT_ID,)
    return queue.release_element.call_args.kwargs["error"]


class TestIsTransient:
    @pytest.mark.parametrize(
        "err",
        [
            ImageClientConnectionException("down"),
            QueueClientConnectionException("down"),
            SimulationResultClientConnectionException("down"),
            ImageClientException("bad gateway", 502),
            SimulationResultClientException("unavailable", 503),
        ],
    )
    def test_transient(self, err):
        assert is_transient(err)

    @pytest.mark.parametrize(
        "err",
        [
            ImageClientException("unprocessable", 422),
            ImageNotFoundException("gone", 404),
            SimulationResultClientException("no status"),
            ValueError("simulation failed"),
        ],
    )
    def test_permanent(self, err):
        assert not is_transient(err)


class TestHappyPath:
    def test_runs_all_steps_with_idempotency_keys(self, handler, element, queue, images, results):
        handler.run_saga(element)

        assert images.create_image.call_args.kwargs["idempotency_key"] == IMAGE_KEY
        assert results.create_result.call_args.kwargs["idempotency_key"] == RESULT_KEY
        assert results.create_result.call_args.args[1] == IMAGE_ID
        queue.delete_queued_element.assert_called_once_with(ELEMENT_ID)

    def test_nothing_is_compensated(self, handler, element, queue, images, results):
        handler.run_saga(element)

        queue.release_element.assert_not_called()
        images.delete_image.assert_not_called()
        results.delete_result.assert_not_called()

    def test_simulation_gets_element_parameters(self, handler, element, simulation):
        handler.run_saga(element)

        simulation.set_parameters.assert_called_once_with({"foo": "bar"})
        simulation.simulate.assert_called_once()


class TestBackwardRecovery:
    def test_simulation_error_releases_claim(self, handler, element, simulation, queue, images):
        simulation.simulate.side_effect = ValueError("bad parameters")

        handler.run_saga(element)

        assert "bad parameters" in released_error(queue)
        images.create_image.assert_not_called()
        queue.delete_queued_element.assert_not_called()

    def test_permanent_image_error_releases_without_retry(self, handler, element, queue, images):
        images.create_image.side_effect = ImageClientException("unprocessable", 422)

        handler.run_saga(element)

        assert images.create_image.call_count == 1
        images.delete_image.assert_not_called()  # image id unknown
        assert "unprocessable" in released_error(queue)

    def test_image_down_after_retries_releases(self, handler, element, queue, images):
        images.create_image.side_effect = ImageClientConnectionException("down")

        handler.run_saga(element)

        assert images.create_image.call_count == 3  # 1 + 2 retries
        assert "down" in released_error(queue)

    def test_permanent_result_error_deletes_image_and_releases(
        self, handler, element, queue, images, results
    ):
        results.create_result.side_effect = SimulationResultClientException("unprocessable", 422)

        handler.run_saga(element)

        assert results.create_result.call_count == 1
        results.delete_result.assert_not_called()  # rejected -> nothing stored
        images.delete_image.assert_called_once_with(IMAGE_ID)
        released_error(queue)
        queue.delete_queued_element.assert_not_called()

    def test_lost_result_response_replays_key_then_deletes(
        self, handler, element, queue, images, results
    ):
        stored = results.create_result.return_value
        results.create_result.side_effect = [
            SimulationResultClientConnectionException("timeout"),
            SimulationResultClientConnectionException("timeout"),
            SimulationResultClientConnectionException("timeout"),
            stored,  # replay during compensation returns the stored result
        ]

        handler.run_saga(element)

        replay = results.create_result.call_args_list[-1]
        assert replay.kwargs["idempotency_key"] == RESULT_KEY
        results.delete_result.assert_called_once_with(str(RESULT_ID))
        images.delete_image.assert_called_once_with(IMAGE_ID)
        released_error(queue)

    def test_compensations_run_in_reverse_order(self, handler, element, queue, images, results):
        order = MagicMock()
        order.attach_mock(results.delete_result, "delete_result")
        order.attach_mock(images.delete_image, "delete_image")
        order.attach_mock(queue.release_element, "release_element")
        results.create_result.side_effect = [
            SimulationResultClientConnectionException("timeout"),
        ] * 3 + [results.create_result.return_value]

        handler.run_saga(element)

        names = [c[0] for c in order.mock_calls]
        assert names == ["delete_result", "delete_image", "release_element"]

    def test_already_deleted_image_and_element_are_fine(
        self, handler, element, queue, images, results
    ):
        results.create_result.side_effect = SimulationResultClientException("bad", 400)
        images.delete_image.side_effect = ImageNotFoundException("gone", 404)
        queue.release_element.side_effect = QueueClientElementNotFoundException("gone", 404)

        handler.run_saga(element)  # must not raise

        images.delete_image.assert_called_once()
        queue.release_element.assert_called_once()

    def test_failing_compensation_continues_with_release(
        self, handler, element, queue, images, results
    ):
        results.create_result.side_effect = SimulationResultClientException("bad", 400)
        images.delete_image.side_effect = ImageClientConnectionException("down")

        handler.run_saga(element)

        assert images.delete_image.call_count == 4  # 1 + 3 compensation retries
        released_error(queue)


class TestForwardRecovery:
    def test_transient_image_error_is_retried(self, handler, element, queue, images):
        images.create_image.side_effect = [ImageClientConnectionException("blip"), IMAGE_ID]

        handler.run_saga(element)

        assert images.create_image.call_count == 2
        assert {c.kwargs["idempotency_key"] for c in images.create_image.call_args_list} == {
            IMAGE_KEY
        }
        queue.delete_queued_element.assert_called_once()
        queue.release_element.assert_not_called()

    def test_dequeue_is_retried_after_pivot(self, handler, element, queue, images, results):
        queue.delete_queued_element.side_effect = [
            QueueClientConnectionException("blip"),
            True,
        ]

        handler.run_saga(element)

        assert queue.delete_queued_element.call_count == 2
        queue.release_element.assert_not_called()

    def test_dequeue_of_missing_element_counts_as_done(self, handler, element, queue):
        queue.delete_queued_element.side_effect = QueueClientElementNotFoundException("gone", 404)

        handler.run_saga(element)

        queue.release_element.assert_not_called()

    def test_dequeue_failing_after_pivot_is_not_rolled_back(
        self, handler, element, queue, images, results
    ):
        queue.delete_queued_element.side_effect = QueueClientConnectionException("down")

        handler.run_saga(element)  # logs SagaIncomplete, does not raise

        assert queue.delete_queued_element.call_count == 3
        results.delete_result.assert_not_called()
        images.delete_image.assert_not_called()
        queue.release_element.assert_not_called()


class TestProcessQueue:
    def test_empty_queue_sleeps_and_continues(self, handler, queue):
        def claim():
            if queue.claim_element.call_count >= 2:
                handler.is_running = False
            raise EMPTY_QUEUE

        queue.claim_element.side_effect = claim
        handler.is_running = True

        handler.process_queue()

        assert queue.claim_element.call_count == 2

    def test_worker_survives_failing_sagas(self, handler, element, queue, simulation):
        elements = [element, element.model_copy(update={"id": uuid.uuid4()})]

        def claim():
            if not elements:
                handler.is_running = False
                raise EMPTY_QUEUE
            return elements.pop(0)

        queue.claim_element.side_effect = claim
        simulation.simulate.side_effect = [ValueError("boom"), None]
        handler.is_running = True

        handler.process_queue()

        assert queue.release_element.call_count == 1
        assert queue.delete_queued_element.call_count == 1

    def test_unexpected_error_does_not_escape(self, handler, element, monkeypatch):
        monkeypatch.setattr(handler, "_steps", MagicMock(side_effect=RuntimeError("bug")))

        handler.run_saga(element)  # must not raise


def test_release_error_names_the_cause(handler, element, queue, simulation):
    simulation.simulate.side_effect = ValueError("bad parameters")

    handler.run_saga(element)

    assert queue.release_element.call_args == call(
        ELEMENT_ID, error=repr(ValueError("bad parameters"))
    )
