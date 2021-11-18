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
            "intro-cell-file": ""
        }
        cls.user_id = "some_user"
        cls.set_api_client = mock.MagicMock()
        cls.data_palette_client = mock.MagicMock()
        cls.workspace_client = WorkspaceMock()
        cls.search_client = mock.MagicMock()

    def test_rename_narrative_ok_unit(self):
        # set up narrative with old name
        old_name = "An Old Narrative Name"
        new_name = "New Narrative Name"
        version = "0.4.1"
        narrative_ref = self.workspace_client.make_fake_narrative(old_name, self.user_id)

        nm = NarrativeManager(self.config, self.user_id, self.set_api_client, self.data_palette_client, self.workspace_client, self.search_client)

        narr_obj = self.workspace_client.get_objects2({"objects": [{"ref": narrative_ref}]})
        # verify that we get it with the mock client
        self.assertEqual(narr_obj["data"][0]["data"]["metadata"]["name"], old_name)
        # run rename to a new name
        # verify that the new name is set

        nm.rename_narrative(narrative_ref, new_name, version)

        self.assertEqual(self.workspace_client.get_objects2({"objects": [{"ref": narrative_ref}]})["data"][0]["data"]["metadata"]["name"], new_name)


    def test_get_narrative_doc(self):
        # set up narrative
        narrative_ref = self.workspace_client.make_fake_narrative("Doc Format Test", self.user_id)
        nm = NarrativeManager(self.config, self.user_id, self.set_api_client, self.data_palette_client, self.workspace_client, self.search_client)

        # get ws_id
        ws_id = int(narrative_ref.split('/')[0])
        # add version number
        full_upa = narrative_ref + '/1'

        doc = nm.get_narrative_doc(full_upa)

        self.assertEqual(doc['access_group'], ws_id)
        self.assertEqual(doc['cells'], [])
        self.assertEqual(doc['total_cells'], 0)
        self.assertFalse(doc['is_public'])

        # test data object format
        self.assertEqual(len(doc['data_objects']), 10)
        self.assertEqual(doc['data_objects'][0], {'name': 'Object_1-1', 'obj_type': 'KBaseNarrative.Narrative-4.0'})

        self.assertEqual(doc['timestamp'], 0)
        self.assertEqual(doc['creation_date'], '1970-01-01T00:00:00+0000')

        # test that poorly formatted upa is handled correctly
        with self.assertRaises(ValueError) as err:
            nm.get_narrative_doc(narrative_ref)
        self.assertIn('Incorrect upa format: required format is <workspace_id>/<object_id>/<version>', str(err.exception))

        # ensure that proper not found message is raised
        with self.assertRaises(ValueError) as err:
            nm.get_narrative_doc('2000/2000/2000')
        self.assertIn('Item with upa "2000/2000/2000" not found in workspace database.', str(err.exception))

    def test_revert_narrative_object(self):
        # set up narrative
        narrative_ref = self.workspace_client.make_fake_narrative("SomeNiceName", self.user_id, make_object_history=True)

        ws_id, obj, ver = narrative_ref.split('/')

        nm = NarrativeManager(self.config,
                              self.user_id,
                              self.set_api_client,
                              self.data_palette_client,
                              self.workspace_client,
                              self.search_client)

        # simulate reverting fake narrative to version #2 (make_object_history=True automatically makes 5 versions)
        revert_result = nm.revert_narrative_object({
            'wsid': int(ws_id),
            'objid': int(obj),
            'ver': 2
        })

        history = self.workspace_client.get_object_history({'wsid': int(ws_id), 'objid': int(obj)})

        # check to make sure new item was added
        self.assertEqual(len(history), 6)
        self.assertEqual(revert_result[4], 6)
        self.assertEqual(history[-1], revert_result)
        # check that workspace meta was properly updated
        self.assertEqual(self.workspace_client.internal_db[int(ws_id)]['meta']['narrative_nice_name'], revert_result[10]['name'])

        # test that ObjectIdentities without specified versions will throw an error
        with self.assertRaises(ValueError) as err:
            nm.revert_narrative_object({
                'wsid': int(ws_id),
                'objid': int(obj)
            })
        self.assertIn("Cannot revert object %s/%s without specifying a version to revert to" % (ws_id, obj),
                      str(err.exception))

        # test that method won't accept malformed ObjectIdentities (missing wsid or objid)
        with self.assertRaises(ValueError) as err:
            nm.revert_narrative_object({
                'bad_field_1': 1000,
                'bad_field_2': 20,
                'objid': int(obj)
            })
        self.assertIn('Please choose exactly 1 workspace specifier;', str(err.exception))

        # test that you can't have more than one specifier in ObjectIdentity
        with self.assertRaises(ValueError) as err:
            nm.revert_narrative_object({
                'wsid': int(ws_id),
                'objid': int(obj),
                'name': 'This_Field_Should_Fail'
            })
        self.assertIn('Please choose exactly 1 object identifier;', str(err.exception))

        # make sure that you can't revert an object with a version greater than current version
        with self.assertRaises(ValueError) as err:
            nm.revert_narrative_object({
                'wsid': int(ws_id),
                'objid': int(obj),
                'ver': 5000
            })
        self.assertIn('Cannot revert object at version 6 to version 5000', str(err.exception))

