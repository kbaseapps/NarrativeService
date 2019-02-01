import os
import unittest
from configparser import ConfigParser
from unittest import mock

import NarrativeService.sharing.sharemanager as sharemanager


class WsMock:
    def __init__(self, *args, **kwargs):
        pass

    def administer(self, *args, **kwargs):
        return {"foo": "a", "bar": "w"}

def mock_feed_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status():
            if status_code != 200:
                raise requests.HTTPError()
    return MockResponse({"id": "foo"}, 200)

class ShareRequesterTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.NARRATIVE_TYPE = "KBaseNarrative.Narrative-4.0"
        cls.config = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('NarrativeService'):
            cls.config[nameval[0]] = nameval[1]
        authServiceUrl = cls.config.get('auth-service-url',
                "https://kbase.us/services/authorization/Sessions/Login")

    def test_valid_params(self):
        p = {
            "user": "foo",
            "ws_id": 123,
            "share_level": "a"
        }
        sharemanager.ShareRequester(p, self.config)

    def test_invalid_params(self):
        with self.assertRaises(ValueError) as e:
            sharemanager.ShareRequester({"user": "foo", "share_level": "a"}, self.config)
        self.assertIn('Missing required parameter "ws_id"', str(e.exception))

        with self.assertRaises(ValueError) as e:
            sharemanager.ShareRequester({"ws_id": 123, "share_level": "a"}, self.config)
        self.assertIn('Missing required parameter "user"', str(e.exception))

        with self.assertRaises(ValueError) as e:
            sharemanager.ShareRequester({"user": "foo", "ws_id": 123}, self.config)
        self.assertIn('Missing required parameter "share_level"', str(e.exception))

        with self.assertRaises(ValueError) as e:
            sharemanager.ShareRequester({"user": "foo", "share_level": "x", "ws_id": 123}, self.config)
        self.assertIn('Invalid share level: x. Should be one of a, n, r.', str(e.exception))

    @mock.patch('NarrativeService.sharing.sharemanager.feeds.requests.post', side_effect=mock_feed_post)
    @mock.patch('NarrativeService.sharing.sharemanager.ws.Workspace', side_effect=WsMock)
    def test_make_notification(self, mock_ws, mock_post):
        req = sharemanager.ShareRequester({"user": "kbasetest", "ws_id": 123, "share_level": "r"}, self.config)
        res = req.request_share()
        self.assertIn("ok", res)
        self.assertEqual(res['ok'], 1)
