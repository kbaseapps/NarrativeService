from unittest import mock
from unittest.mock import MagicMock

import pytest
from installed_clients.baseclient import ServerError
from NarrativeService.sharing.sharemanager import ShareRequester

NARRATIVE_TYPE = "KBaseNarrative.Narrative-4.0"
FAKE_ADMINS = ["some_user"]


def test_valid_params(config: dict[str, str]):
    params = {
        "user": "foo",
        "ws_id": 123,
        "share_level": "a"
    }
    requester = ShareRequester(params, config)
    assert isinstance(requester, ShareRequester)
    assert requester.ws_id == params["ws_id"]


invalid_combos = [
    ({"user": "foo", "share_level": "a"}, "ws_id"),
    ({"ws_id": 123, "share_level": "a"}, "user"),
    ({"user": "foo", "ws_id": 123}, "share_level"),
]


@pytest.mark.parametrize("params,missing", invalid_combos)
def test_invalid_params(params: dict[str, str | int], missing: str, config: dict[str, str]):
    with pytest.raises(ValueError, match=f'Missing required parameter "{missing}"'):
        ShareRequester(params, config)


def test_invalid_share_level(config: dict[str, str]):
    params = {
        "user": "foo",
        "share_level": "lol",
        "ws_id": 123
    }
    with pytest.raises(ValueError, match=f"Invalid share level: {params['share_level']}. Should be one of a, n, r."):
        ShareRequester(params, config)


@mock.patch("NarrativeService.sharing.sharemanager.feeds")
@mock.patch("NarrativeService.sharing.sharemanager.ws.get_ws_admins", return_value=FAKE_ADMINS)
def test_make_notification_ok(mock_ws, mock_post, config: dict[str, str]):  # noqa: ARG001
    config["service-token"] = "fake-service-token"
    config["ws-admin-token"] = "fake-admin-token"
    req = ShareRequester({"user": "kbasetest", "ws_id": 123, "share_level": "r"}, config)
    res = req.request_share()
    assert "ok" in res
    assert res["ok"] == 1


token_allowance = [
    ("service-token", "missing permission to find Narrative owners."),
    ("ws-admin-token", "missing authorization to make request.")
]


@pytest.mark.parametrize("token_name,expected_error", token_allowance)
def test_make_notification_token_fail(token_name: str, expected_error: str, config: dict[str, str]):
    config[token_name] = "fake-token"
    req = ShareRequester({"user": "kbasetest", "ws_id": 123, "share_level": "r"}, config)
    res = req.request_share()
    assert "ok" in res
    assert res["ok"] == 0
    assert "error" in res
    assert res["error"] == f"Unable to request share - NarrativeService is {expected_error}"


@mock.patch("NarrativeService.sharing.sharemanager.ws.get_ws_admins")
def test_make_notification_fail(mock_ws: MagicMock, config: dict[str, str]):
    mock_ws.side_effect = ServerError("error", 500, "not working")
    config["service-token"] = "fake-token"
    config["ws-admin-token"] = "fake-ws-token"
    req = ShareRequester({"user": "kbasetest", "ws_id": 123, "share_level": "r"}, config)
    res = req.request_share()
    assert res == {
        "ok": 0,
        "error": "Unable to request share - couldn't get Narrative owners!"
    }
