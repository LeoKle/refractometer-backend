import os
import subprocess
import time
from pathlib import Path

import pytest
from pact import Verifier

# Copies of the consumer contracts. The common layer contract is generated in
# refractometer-api-gateway (tests/contract/pacts) and copied here when it changes.
PACT_DIR = Path(__file__).parent / "pacts"
PROVIDER_URL = "http://localhost:8001"


pytestmark = pytest.mark.pact


@pytest.fixture(scope="module")
def provider_server():
    env = os.environ.copy()
    env["ENABLE_PACT_STATES"] = "true"

    proc = subprocess.Popen(
        [
            "uvicorn",
            "api.app:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8001",
            "--app-dir",
            "src",
        ],
        env=env,
    )
    time.sleep(2)
    yield
    proc.terminate()
    proc.wait()


def test_provider_against_pacts(provider_server):
    # The verifier passes silently without sources, so fail loudly instead.
    assert any(PACT_DIR.glob("*.json")), f"No pact files in {PACT_DIR}"

    verifier = (
        Verifier("parameter-service")
        .add_source(PACT_DIR)
        .add_transport(url=PROVIDER_URL)
        .state_handler(f"{PROVIDER_URL}/_pact/provider_states", teardown=True, body=True)
    )

    verifier.verify()
