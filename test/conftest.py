import os
from collections.abc import Generator
from configparser import ConfigParser
from time import time

import pytest
from installed_clients.authclient import KBaseAuth
from NarrativeService.NarrativeServiceImpl import NarrativeService
from NarrativeService.NarrativeServiceServer import MethodContext

from lib.installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from lib.installed_clients.WorkspaceClient import Workspace


@pytest.fixture(scope="session")
def config() -> Generator[dict[str, str | int], None, None]:
    """Load and return the test config as a dictionary."""
    config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
    config = ConfigParser()
    config.read(config_file)
    yield dict(config.items("NarrativeService"))

@pytest.fixture(scope="session")
def auth_token() -> Generator[str, None, None]:
    token = os.environ.get("KB_AUTH_TOKEN")
    yield token

@pytest.fixture(scope="session")
def workspace(workspace_client: Workspace) -> Generator[list[any], None, None]:
    ws_name = f"test_NarrativeService_{int(time()*1000)}"
    ws_info = workspace_client.create_workspace({"workspace": ws_name})
    yield ws_info
    workspace_client.delete_workspace({"id": ws_info[0]})

@pytest.fixture(scope="session")
def workspace_client(config: dict[str, str | int], auth_token: str):
    if auth_token is None:
        raise RuntimeError("A valid auth token is needed to make a real workspace client for integration tests")
    client = Workspace(config["workspace-url"], token=auth_token)
    yield client

@pytest.fixture(scope="session")
def fake_obj_for_tests_client(auth_token: str):
    if auth_token is None:
        raise RuntimeError("A valid auth token is needed to make a FOFT client for integration tests")
    client = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"], token=auth_token)
    yield client

@pytest.fixture(scope="session")
def auth_client(config: dict[str, str | int]):
    client = KBaseAuth(config["auth-service-url"])
    yield client

@pytest.fixture(scope="session")
def context(auth_token: str, auth_client: KBaseAuth):
    ctx = MethodContext(None)
    user_id = auth_client.get_user(auth_token)
    ctx.update({
        "token": auth_token,
        "user_id": user_id,
        "provenance": [{
            "service": "NarrativeService",
            "method": "please_never_use_it_in_production",
            "method_params": []
        }],
        "authenticated": 1
    })
    yield ctx

@pytest.fixture(scope="session")
def service_impl(config: dict[str, str | int]) -> Generator[NarrativeService, None, None]:
    impl = NarrativeService(config)
    yield impl

MOCK_AUTH_TOKEN: str = "mock_auth_token"
MOCK_USER_ID: str = "mock_user"
MOCK_WS_ID: int = 123
MOCK_WS_INFO: list[str | int | dict[str, str]] = [
    MOCK_WS_ID,
    "mock_workspace",
    MOCK_USER_ID,
    "2024-05-30T15:22:20+0000",
    1,
    "a",
    "n",
    "unlocked",
    {
        "cell_count": "0",
        "narrative_nice_name": "A New Narrative",
        "searchtags": "narrative",
        "is_temporary": "false",
        "narrative": "1"
    }
]

@pytest.fixture
def mock_workspace():
    return MOCK_WS_INFO.copy()

@pytest.fixture
def mock_token():
    return MOCK_AUTH_TOKEN

@pytest.fixture
def mock_user():
    return MOCK_USER_ID
