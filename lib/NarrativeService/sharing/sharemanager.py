from feeds import make_notification
from util.workspace import get_ws_admins
from uuid import uuid4
from storage.mongo import (
    save_share_request,
    find_existing_share_request
)


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
        ret_value = {"ok": True}
        # Check if request has been made
        existing = find_existing_share_request(self.ws_id, self.user, self.level)
        if existing is not None:
            ret_value = {
                "ok": False,
                "error": "A request has already been made"
            }
            return ret_value
        # Make the request by firing a notification
        requestees = get_ws_admins(self.ws_id, self.config['workspace-url'])
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
        note_id = make_notification(note, self.config['feeds-url'], self.config['auth-token'])

        # Store that we made the request, uh, somewhere
        save_share_request(self.ws_id, self.user, self.level, note_id)

    def validate_request_params(self, params):
        reqd = ['ws_id', 'share_level', 'user']
        for r in reqd:
            if r not in params or params[r] is not None:
                raise ValueError('Missing required parameter "{}"'.format(r))
