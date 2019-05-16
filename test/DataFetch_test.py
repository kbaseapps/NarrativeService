import unittest
from NarrativeService.data.fetcher import DataFetcher
import os
from configparser import ConfigParser
from installed_clients.authclient import KBaseAuth
from installed_clients.WorkspaceClient import Workspace
from NarrativeService.NarrativeServiceServer import MethodContext


class DataFetcherTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get("KB_AUTH_TOKEN")
        config_file = os.environ.get("KB_DEPLOYMENT_CONFIG")
        cls.cfg = dict()
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items("NarrativeService"):
            cls.cfg[nameval[0]] = nameval[1]
        if "auth-service-url" not in cls.cfg:
            raise RuntimeError("Missing auth-service-url from config")
        auth_client = KBaseAuth(cls.cfg["auth-service-url"])
        user_id = auth_client.get_user(token)
        cls.ctx = MethodContext(None)
        cls.ctx.update({
            "token": token,
            "user_id": user_id,
            "provenance": [{
                "service": "NarrativeService",
                "method": "please_never_use_it_in_producation",
                "method_params": []
            }],
            "authenticated": 1
        })

    def get_context(self):
        return self.__class__.ctx

    def test_data_fetcher(self):
        pass

    def test_bad_params(self):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )
        with self.assertRaises(ValueError) as err:
            df.fetch_data({"data_set": "foo"})
        self.assertIn("Parameter 'data_set' must be either 'mine' or 'shared', not 'foo'", str(err.exception))

        optional_params = ["include_type_counts", "simple_types", "ignore_narratives"]
        for opt in optional_params:
            with self.assertRaises(ValueError) as err:
                df.fetch_data({"data_set": "mine", opt: "wat"})
            self.assertIn("Parameter '{}' must be 0 or 1, not 'wat'".format(opt), str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_data({"data_set": "mine", "ignore_workspaces": "wat"})
        self.assertIn("Parameter 'ignore_workspaces' must be a list if present", str(err.exception))
