import os
import subprocess
import time
from pathlib import Path

import pytest
from pact import Verifier

PACT_DIR = Path(__file__).parent / "pacts"
PROVIDER_URL = "http://localhost:8000"


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
            "8002",
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
    verifier = (
        Verifier("image-service")
        .add_source(PACT_DIR)
        .add_transport(url="http://localhost:8002")
        .state_handler(f"{PROVIDER_URL}/_pact/provider_states", body=True)
    )

    verifier.verify()
