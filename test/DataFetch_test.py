import unittest
from unittest import mock
from NarrativeService.data.fetcher import DataFetcher
import os
from configparser import ConfigParser
from installed_clients.authclient import KBaseAuth
from installed_clients.WorkspaceClient import Workspace
from NarrativeService.NarrativeServiceServer import MethodContext
from NarrativeService.NarrativeServiceImpl import NarrativeService
from workspace_mock import WorkspaceMock


class WsMock:
    def __init__(self, *args, **kwargs):
        pass

    def administer(self, *args, **kwargs):
        return {"perms": [{"foo": "a", "bar": "w"}]}


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
        cls.service_impl = NarrativeService(cls.cfg)

    def get_context(self):
        return self.__class__.ctx

    def test_fetch_accessible_bad_params(self):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )
        with self.assertRaises(ValueError) as err:
            df.fetch_accessible_data({"data_set": "foo"})
        self.assertIn("Parameter 'data_set' must be either 'mine' or 'shared', not 'foo'", str(err.exception))

        optional_params = ["include_type_counts", "simple_types", "ignore_narratives"]
        for opt in optional_params:
            with self.assertRaises(ValueError) as err:
                df.fetch_accessible_data({"data_set": "mine", opt: "wat"})
            self.assertIn("Parameter '{}' must be 0 or 1, not 'wat'".format(opt), str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_accessible_data({"data_set": "mine", "ignore_workspaces": "wat"})
        self.assertIn("Parameter 'ignore_workspaces' must be a list if present", str(err.exception))

        bad_limits = [0, -5, "a", "foo", ["foo", "bar"], {"no": "wai"}]
        for bad in bad_limits:
            with self.assertRaises(ValueError) as err:
                df.fetch_accessible_data({"data_set": "mine", "limit": bad})
            self.assertIn("Parameter 'limit' must be an integer > 0", str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_accessible_data({"data_set": "mine", "types": "wat"})
        self.assertIn("Parameter 'types' must be a list if present.", str(err.exception))

    def test_fetch_specific_bad_params(self):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )
        with self.assertRaises(ValueError) as err:
            df.fetch_specific_workspace_data({"workspace_ids": "foo"})
        self.assertIn("Parameter 'workspace_ids' must be a list of integers.", str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_specific_workspace_data({"workspace_ids": []})
        self.assertIn("Parameter 'workspace_ids' must be a list of integers.", str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_specific_workspace_data({"workspace_ids": ["foo"]})
        self.assertIn("Parameter 'workspace_ids' must be a list of integers.", str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_specific_workspace_data({"workspace_ids": [1, 2, 3, "foo", 5]})
        self.assertIn("Parameter 'workspace_ids' must be a list of integers.", str(err.exception))

        optional_params = ["include_type_counts", "simple_types", "ignore_narratives"]
        for opt in optional_params:
            with self.assertRaises(ValueError) as err:
                df.fetch_specific_workspace_data({"workspace_ids": [1, 2], opt: "wat"})
            self.assertIn("Parameter '{}' must be 0 or 1, not 'wat'".format(opt), str(err.exception))

        bad_limits = [0, -5, "a", "foo", ["foo", "bar"], {"no": "wai"}]
        for bad in bad_limits:
            with self.assertRaises(ValueError) as err:
                df.fetch_specific_workspace_data({"workspace_ids": [1], "limit": bad})
            self.assertIn("Parameter 'limit' must be an integer > 0", str(err.exception))

        with self.assertRaises(ValueError) as err:
            df.fetch_specific_workspace_data({"workspace_ids": [1], "types": "wat"})
        self.assertIn("Parameter 'types' must be a list if present.", str(err.exception))

    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_list_all_data_impl(self, mock_ws):
        my_data = self.service_impl.list_all_data(self.ctx, {"data_set": "mine"})[0]
        self.assertEqual(len(my_data["objects"]), 36)
        for obj in my_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(my_data["workspace_display"], 9)
        self.assertNotIn("type_counts", my_data)

    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_list_specific_data_impl(self, mock_ws):
        my_data = self.service_impl.list_workspace_data(self.ctx, {"workspace_ids": [1, 2, 3, 5]})[0]
        self.assertEqual(len(my_data["objects"]), 36)
        for obj in my_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(my_data["workspace_display"], 9)
        self.assertNotIn("type_counts", my_data)

    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_data_fetcher_mine(self, mock_ws):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )

        # 1. my data, default options
        my_data = df.fetch_accessible_data({"data_set": "mine"})
        self.assertEqual(len(my_data["objects"]), 36)
        for obj in my_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(my_data["workspace_display"], 9)
        self.assertNotIn("type_counts", my_data)

        # 2. my data, with type counts
        my_data = df.fetch_accessible_data({"data_set": "mine", "include_type_counts": 1})
        self.assertEqual(len(my_data["objects"]), 36)
        for obj in my_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(my_data["workspace_display"], 9)
        self.assertIn("type_counts", my_data)
        self.assertEqual(len(my_data["type_counts"]), 9)  # one for each version of SomeType
        self.assertIn("KBaseModule.SomeType-1.0", my_data["type_counts"])
        self.assertEqual(my_data["type_counts"]["KBaseModule.SomeType-1.0"], 4)

        # 3. my data, with simple types, with type counts
        my_data = df.fetch_accessible_data({"data_set": "mine", "include_type_counts": 1, "simple_types": 1})
        self.assertEqual(len(my_data["objects"]), 36)
        for obj in my_data["objects"]:
            self._validate_obj(obj, "SomeType")
        self._validate_ws_display(my_data["workspace_display"], 9)
        self.assertIn("type_counts", my_data)
        self.assertEqual(len(my_data["type_counts"]), 1)
        self.assertIn("SomeType", my_data["type_counts"])
        self.assertEqual(my_data["type_counts"]["SomeType"], 36)

        # 4. my data, with simple types, and type counts, don't ignore narratives
        my_data = df.fetch_accessible_data({
            "data_set": "mine",
            "include_type_counts": 1,
            "simple_types": 1,
            "ignore_narratives": 0
        })
        self.assertEqual(len(my_data["objects"]), 40)
        for obj in my_data["objects"]:
            if obj["obj_id"] == 1:
                self._validate_obj(obj, "Narrative")
            else:
                self._validate_obj(obj, "SomeType")
        self._validate_ws_display(my_data["workspace_display"], 10)
        self.assertIn("type_counts", my_data)
        self.assertEqual(len(my_data["type_counts"]), 2)
        self.assertIn("SomeType", my_data["type_counts"])
        self.assertEqual(my_data["type_counts"]["SomeType"], 36)
        self.assertIn("Narrative", my_data["type_counts"])
        self.assertEqual(my_data["type_counts"]["Narrative"], 4)

    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_data_fetcher_shared(self, mock_ws):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )

        # 1. shared data, default options
        shared_data = df.fetch_accessible_data({"data_set": "shared"})
        self.assertEqual(len(shared_data["objects"]), 36)
        for obj in shared_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(shared_data["workspace_display"], 9)
        self.assertNotIn("type_counts", shared_data)

        # 2. shared data, with type counts
        shared_data = df.fetch_accessible_data({"data_set": "shared", "include_type_counts": 1})
        self.assertEqual(len(shared_data["objects"]), 36)
        for obj in shared_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(shared_data["workspace_display"], 9)
        self.assertIn("type_counts", shared_data)
        self.assertEqual(len(shared_data["type_counts"]), 9)  # one for each version of SomeType
        self.assertIn("KBaseModule.SomeType-1.0", shared_data["type_counts"])
        self.assertEqual(shared_data["type_counts"]["KBaseModule.SomeType-1.0"], 4)

        # 3. shared data, with simple types, with type counts
        shared_data = df.fetch_accessible_data({"data_set": "shared", "include_type_counts": 1, "simple_types": 1})
        self.assertEqual(len(shared_data["objects"]), 36)
        for obj in shared_data["objects"]:
            self._validate_obj(obj, "SomeType")
        self._validate_ws_display(shared_data["workspace_display"], 9)
        self.assertIn("type_counts", shared_data)
        self.assertEqual(len(shared_data["type_counts"]), 1)
        self.assertIn("SomeType", shared_data["type_counts"])
        self.assertEqual(shared_data["type_counts"]["SomeType"], 36)

        # 4. shared data, with simple types, and type counts, don't ignore narratives
        shared_data = df.fetch_accessible_data({
            "data_set": "shared",
            "include_type_counts": 1,
            "simple_types": 1,
            "ignore_narratives": 0
        })
        self.assertEqual(len(shared_data["objects"]), 40)
        for obj in shared_data["objects"]:
            if obj["obj_id"] == 1:
                self._validate_obj(obj, "Narrative")
            else:
                self._validate_obj(obj, "SomeType")
        self._validate_ws_display(shared_data["workspace_display"], 10)
        self.assertIn("type_counts", shared_data)
        self.assertEqual(len(shared_data["type_counts"]), 2)
        self.assertIn("SomeType", shared_data["type_counts"])
        self.assertEqual(shared_data["type_counts"]["SomeType"], 36)
        self.assertIn("Narrative", shared_data["type_counts"])
        self.assertEqual(shared_data["type_counts"]["Narrative"], 4)

    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_data_fetcher_specific_types(self, mock_ws):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )

        # 1. ws 1,2,3,5, default options, include Narratives, but only return KBaseModule.SomeType
        data = df.fetch_specific_workspace_data({
            "workspace_ids": [1, 2, 3, 5],
            "ignore_narratives": 0,
            "types": ["KBaseModule.SomeType"]
        })
        self.assertEqual(len(data["objects"]), 36)
        for obj in data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(data["workspace_display"], 9)
        self.assertNotIn("type_counts", data)

        # 2. ws 1,2,3,5, default options, include Narratives, but only return KBaseNarrative.Narrative
        data = df.fetch_specific_workspace_data({
            "workspace_ids": [1, 2, 3, 5],
            "ignore_narratives": 0,
            "types": ["KBaseNarrative.Narrative"]
        })
        self.assertEqual(len(data["objects"]), 4)
        for obj in data["objects"]:
            self._validate_obj(obj, "KBaseNarrative.Narrative-4.0")
        self._validate_ws_display(data["workspace_display"], 1)
        self.assertNotIn("type_counts", data)

        # 3. ws 1,2,3,5, default options, include Narratives and SomeType, so return everything
        data = df.fetch_specific_workspace_data({
            "workspace_ids": [1, 2, 3, 5],
            "ignore_narratives": 0,
            "types": ["KBaseNarrative.Narrative", "KBaseModule.SomeType"]
        })
        self.assertEqual(len(data["objects"]), 40)
        for obj in data["objects"]:
            if obj["obj_id"] == 1:
                self._validate_obj(obj, "KBaseNarrative.Narrative-4.0")
            else:
                self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(data["workspace_display"], 10)
        self.assertNotIn("type_counts", data)


    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_data_fetcher_shared_types(self, mock_ws):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )

        # 1. shared data, default options, include Narratives, but only return KBaseModule.SomeType
        shared_data = df.fetch_accessible_data({
            "data_set": "shared",
            "ignore_narratives": 0,
            "types": ["KBaseModule.SomeType"]
        })
        self.assertEqual(len(shared_data["objects"]), 36)
        for obj in shared_data["objects"]:
            self._validate_obj(obj, "KBaseModule.SomeType")
        self._validate_ws_display(shared_data["workspace_display"], 9)
        self.assertNotIn("type_counts", shared_data)

        # 2. shared data, default options, include Narratives, but only return KBaseNarrative.Narrative
        shared_data = df.fetch_accessible_data({
            "data_set": "shared",
            "ignore_narratives": 0,
            "types": ["KBaseNarrative.Narrative"]
        })
        self.assertEqual(len(shared_data["objects"]), 4)
        for obj in shared_data["objects"]:
            self._validate_obj(obj, "KBaseNarrative.Narrative-4.0")
        self._validate_ws_display(shared_data["workspace_display"], 1)
        self.assertNotIn("type_counts", shared_data)

    @mock.patch("NarrativeService.data.fetcher.Workspace", side_effect=WorkspaceMock)
    def test_data_fetcher_limit(self, mock_ws):
        df = DataFetcher(
            self.cfg["workspace-url"],
            self.cfg["auth-service-url"],
            self.get_context()["token"]
        )

        # Get my data, but limit it to 5 objects total.
        data = df.fetch_accessible_data({
            "data_set": "mine",
            "limit": 5
        })
        self.assertEqual(len(shared_data["objects"]), 5)
        self.assertEqual(data["limit_reached"], 1)

    def _validate_ws_display(self, ws_disp, count):
        self.assertEqual(len(ws_disp), 4)
        for ws_id in ws_disp:
            self.assertEqual(ws_disp[ws_id]["count"], count)
        self.assertEqual(ws_disp[1]["display"], "Legacy (TestWs_1)")
        self.assertEqual(ws_disp[2]["display"], "Some Narrative")
        self.assertEqual(ws_disp[3]["display"], "Some Other Narrative")
        self.assertEqual(ws_disp[5]["display"], "(data only) TestWs_5")

    def _validate_obj(self, obj, obj_type):
        self.assertIn("ws_id", obj)
        self.assertTrue(isinstance(obj["ws_id"], int))
        self.assertIn("obj_id", obj)
        self.assertTrue(isinstance(obj["obj_id"], int))
        self.assertIn("ver", obj)
        self.assertTrue(isinstance(obj["ver"], int))
        self.assertIn("saved_by", obj)
        self.assertIn("name", obj)
        self.assertEqual(obj["name"], "Object_{}-{}".format(obj["ws_id"], obj["obj_id"]))
        self.assertIn("type", obj)
        self.assertIn(obj_type, obj["type"])
        self.assertIn("timestamp", obj)
