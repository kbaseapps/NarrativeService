"""
Unit tests for the NarrativeManager module.
"""
from unittest import mock

import pytest
from NarrativeService.narrativemanager import NARRATIVE_TYPE, NarrativeManager


def test_rename_narrative_ok_unit(config, mock_workspace_client, mock_user) -> None:
    # set up narrative with old name
    old_name = "An Old Narrative Name"
    new_name = "New Narrative Name"
    version = "0.4.1"
    narrative_ref = mock_workspace_client.make_fake_narrative(old_name, mock_user)

    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())

    narr_obj = mock_workspace_client.get_objects2({"objects": [{"ref": narrative_ref}]})
    # verify that we get it with the mock client
    assert narr_obj["data"][0]["data"]["metadata"]["name"] == old_name
    # run rename to a new name
    # verify that the new name is set

    nm.rename_narrative(narrative_ref, new_name, version)
    narr_obj = mock_workspace_client.get_objects2({"objects": [{"ref": narrative_ref}]})
    assert narr_obj["data"][0]["data"]["metadata"]["name"] == new_name


def test_get_narrative_doc_ok(config, mock_workspace_client, mock_user):
    # set up narrative
    narrative_ref = mock_workspace_client.make_fake_narrative("Doc Format Test", mock_user)
    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())

    # get ws_id
    ws_id = int(narrative_ref.split("/")[0])
    # add version number
    full_upa = narrative_ref + "/1"

    doc = nm.get_narrative_doc(full_upa)
    assert doc["access_group"] == ws_id
    assert doc["cells"] == []
    assert doc["total_cells"] == 0
    assert doc["is_public"] is False
    assert doc["timestamp"] == 0
    assert doc["creation_date"] == "1970-01-01T00:00:00+0000"

    # test data object format
    assert len(doc["data_objects"]) == 9  # noqa: PLR2004
    assert doc["data_objects"][0] == {
        "name": "Object_1-2",
        "obj_type": "KBaseModule.SomeType-1.0"
    }

    # ensure that there are no kbase narrative instances in data objects
    for data_obj in doc["data_objects"]:
        assert NARRATIVE_TYPE not in data_obj["obj_type"]


def test_get_narrative_doc_bad_upa(config, mock_workspace_client, mock_user):
    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())
    # test that poorly formatted upa is handled correctly
    with pytest.raises(ValueError, match="required format is <workspace_id>/<object_id>/<version>"):
        nm.get_narrative_doc("blah/blah/blah/blah")


def test_get_narrative_doc_not_found(config, mock_workspace_client, mock_user):
    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())
    # ensure that proper not found message is raised
    upa = "2000/2000/2000"
    with pytest.raises(ValueError, match=f'Item with upa "{upa}" not found in workspace'):
        nm.get_narrative_doc(upa)


def test_revert_narrative_object(config, mock_workspace_client, mock_user):
    # set up narrative
    # simulate reverting fake narrative to version #2
    # (make_object_history=True automatically makes 5 versions)
    narrative_ref = mock_workspace_client.make_fake_narrative(
        "SomeNiceName",
        mock_user,
        make_object_history=True
    )

    (ws_id, obj, ver) = narrative_ref.split("/")
    assert ver == "5"

    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())

    revert_result = nm.revert_narrative_object({
        "wsid": int(ws_id),
        "objid": int(obj),
        "ver": 2
    })

    history = mock_workspace_client.get_object_history({"wsid": int(ws_id), "objid": int(obj)})

    # check to make sure new item was added
    assert len(history) == 6  # noqa: PLR2004
    assert revert_result[4] == 6  # noqa: PLR2004
    assert history[-1] == revert_result
    # check that workspace meta was properly updated
    new_name = mock_workspace_client.internal_db[int(ws_id)]["meta"]["narrative_nice_name"]
    assert revert_result[10]["name"] == new_name


def test_revert_narrative_object_no_version(config, mock_workspace_client, mock_user):
    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())
    ws_id = 123
    obj_id = 234
    expected = f"Cannot revert object {ws_id}/{obj_id} without specifying a version to revert to"
    with pytest.raises(ValueError, match=expected):
        nm.revert_narrative_object({
            "wsid": ws_id,
            "objid": obj_id
        })


def test_revert_narrative_object_malformed_obj(config, mock_workspace_client, mock_user):
    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())
    expected = "Please choose exactly 1 object identifier and 1 workspace identifier;"
    with pytest.raises(ValueError, match=expected):
        nm.revert_narrative_object({
            "bad_field_1": 1000,
            "bad_field_2": 20,
            "objid": 123
        })


def test_revert_narrative_object_bad_version(config, mock_workspace_client, mock_user):
    nm = NarrativeManager(config, mock_user, mock_workspace_client, mock.MagicMock())
    fake_narr_upa = mock_workspace_client.make_fake_narrative(
        "some_narr", mock_user, make_object_history=True
    )
    (ws_id, obj_id, ver) = fake_narr_upa.split("/")
    ver_attempt = 5000
    expected = f"Cannot revert object at version {ver} to version {ver_attempt}"
    with pytest.raises(ValueError, match=expected):
        nm.revert_narrative_object({
            "wsid": int(ws_id),
            "objid": int(obj_id),
            "ver": ver_attempt
        })
