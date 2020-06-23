"""
Unit and integration tests for the Narrative Manager
"""
from NarrativeService.NarrativeManager import NarrativeManager
import unittest
from unittest import mock
from workspace_mock import WorkspaceMock


class NarrativeManagerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "narrative-method-store": "",
            "intro-markdown-file": ""
        }
        cls.user_id = "some_user"
        cls.set_api_client = mock.MagicMock()
        cls.data_palette_client = mock.MagicMock()
        cls.workspace_client = WorkspaceMock()

    def test_rename_narrative_ok_unit(self):
        # set up narrative with old name
        old_name = "An Old Narrative Name"
        new_name = "New Narrative Name"
        version = "0.4.1"
        narrative_ref = self.workspace_client.make_fake_narrative(old_name, self.user_id)

        nm = NarrativeManager(self.config, self.user_id, self.set_api_client, self.data_palette_client, self.workspace_client)

        narr_obj = self.workspace_client.get_objects2({"objects": [{"ref": narrative_ref}]})
        # verify that we get it with the mock client
        self.assertEqual(narr_obj["data"][0]["data"]["metadata"]["name"], old_name)
        # run rename to a new name
        # verify that the new name is set

        nm.rename_narrative(narrative_ref, new_name, version)

        self.assertEqual(self.workspace_client.get_objects2({"objects": [{"ref": narrative_ref}]})["data"][0]["data"]["metadata"]["name"], new_name)
