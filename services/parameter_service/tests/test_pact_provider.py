import os
import subprocess
import time
from pathlib import Path

import pytest
from pact import Verifier

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
    verifier = (
        Verifier("parameter-service")
        .add_source(PACT_DIR)
        .add_transport(url=PROVIDER_URL)
        .state_handler(f"{PROVIDER_URL}/_pact/provider_states", body=True)
    )

    # files = []
    # for file in PACT_DIR.iterdir():
    #     files.append(file)
    # raise ValueError(str(files))

    verifier.verify()
