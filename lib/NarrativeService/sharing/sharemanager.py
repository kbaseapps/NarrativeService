import NarrativeService.util.workspace as ws
from installed_clients.baseclient import ServerError
from NarrativeService import feeds

SERVICE_TOKEN_KEY = "service-token" # noqa: S105
WS_TOKEN_KEY = "ws-admin-token" # noqa: S105


class ShareRequester:
    def __init__(self, params: dict[str, str], config: dict[str, str | int]) -> None:
        """This class handles requesting that a Narrative is shared with another
        user.

        params is a dict with keys:
        * ws_id - the (int) workspace to share with
        * share_level - the requested sharing level
        * user - the user to be shared with (not necessarily the user requesting the share)

        config is a dict with expected keys
        * SERVICE_TOKEN_KEY
        * WS_TOKEN_KEY
        * workspace-url
        """
        self.validate_request_params(params)
        self.ws_id = params["ws_id"]
        self.user = params["user"]
        self.share_level = params["share_level"]
        self.config = config

    def request_share(self) -> dict[str, str | int]:
        """
        This requests that a narrative is shared with a user, and returns a small dictionary
        with sharing request results. The request is made via the Feeds service, which notifies
        the owner(s) of the requested narrative that someone else wants to view it.
        """
        service_token = self.config.get(SERVICE_TOKEN_KEY)
        if service_token is None:
            return {
                "ok": 0,
                "error": "Unable to request share - NarrativeService is missing authorization to make request."
            }

        ws_token = self.config.get(WS_TOKEN_KEY)
        if ws_token is None:
            return {
                "ok": 0,
                "error": "Unable to request share - NarrativeService is missing permission to find Narrative owners."
            }

        ret_value = {
            "ok": 1
        }

        # Make the request by firing a notification
        try:
            requestees = ws.get_ws_admins(self.ws_id, self.config["workspace-url"], ws_token)
        except ServerError:
            return {
                "ok": 0,
                "error": "Unable to request share - couldn't get Narrative owners!"
            }
        note = {
            "actor": {
                "type": "user",
                "id": self.user
            },
            "verb": "request",
            "object": {
                "type": "narrative",
                "id": self.ws_id
            },
            "context": {
                "level": self.share_level
            },
            "level": "request",
            "users": [{"id": u, "type": "user"} for u in [*requestees, self.user]]
        }

        feeds.make_notification(note, self.config["feeds-url"], service_token)

        return ret_value

    def validate_request_params(self, params: dict[str, str]) -> None:
        """Checks the given set of parameters for missing values or, in the case of share_level,
        incorrect values.

        Expected keys should be ws_id, share_level, and user. share_level should be "a", "n", or "r".

        If value is missing, or if share_level is incorrect, this raises a ValueError.
        """
        reqd = ["ws_id", "share_level", "user"]
        for r in reqd:
            if r not in params or params[r] is None:
                raise ValueError(f'Missing required parameter "{r}"')
        level = params["share_level"]
        if level not in ["a", "w", "r"]:
            raise ValueError(f"Invalid share level: {level}. Should be one of a, n, r.")
