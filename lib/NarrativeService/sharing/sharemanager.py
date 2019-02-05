import NarrativeService.feeds as feeds
import NarrativeService.util.workspace as ws

# from storage.mongo import (
#     save_share_request,
#     find_existing_share_request
# )
SERVICE_TOKEN_KEY = "service-token"
WS_TOKEN_KEY = "ws-admin-token"


class ShareRequester(object):
    def __init__(self, params, config):
        self.validate_request_params(params)
        self.ws_id = params['ws_id']
        self.user = params['user']
        self.share_level = params['share_level']
        self.config = config

    def request_share(self):
        """
        params is a dict with keys:
        ws_id - the (int) workspace to share with
        share_level - the requested sharing level
        user - the user to be shared with (not necessarily the user requesting the share)
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
                "error": "Unable to request share - NarrativeService is missing permission to find Workspace owners."
            }

        ret_value = {
            "ok": 1
        }
        # Check if request has been made

        # existing = find_existing_share_request(self.ws_id, self.user, self.level)
        # if existing is not None:
        #     ret_value = {
        #         "ok": 0,
        #         "error": "A request has already been made"
        #     }
        #     return ret_value

        # Make the request by firing a notification
        requestees = ws.get_ws_admins(self.ws_id, self.config['workspace-url'], ws_token)
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
            "users": [{"id": u, "type": "user"} for u in requestees + [self.user]]
        }

        note_id = feeds.make_notification(note, self.config['feeds-url'], service_token)

        # Store that we made the request, uh, somewhere
        # save_share_request(self.ws_id, self.user, self.level, note_id)
        return ret_value

    def validate_request_params(self, params):
        reqd = ['ws_id', 'share_level', 'user']
        for r in reqd:
            if r not in params or params[r] is None:
                raise ValueError('Missing required parameter "{}"'.format(r))
        level = params["share_level"]
        if level not in ["a", "w", "r"]:
            raise ValueError("Invalid share level: {}. Should be one of a, n, r.".format(level))
