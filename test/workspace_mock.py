class EmptyWorkspaceMock:
    def __init__(self, *args, **kwargs):
        self.user = "some_user"
        self.shared_user = "some_other_user"

    def list_workspace_info(self, params):
        return []


class WorkspaceMock:
    ws_info_meta = {
        1: {},
        2: {"narrative": 1, "narrative_nice_name": "Some Narrative", "is_temporary": "false"},
        3: {"narrative": 1, "narrative_nice_name": "Some Other Narrative", "is_temporary": "false"},
        4: {"narrative": 1, "narrative_nice_name": "Untitled", "is_temporary": "true"},
        5: {"narrative": 1, "is_temporary": "false", "show_in_narrative_data_panel": "true"}
    }

    def __init__(self, *args, **kwargs):
        self.user = "wjriehl"
        self.shared_user = "some_random_user"
        self.internal_db = dict()
        # format:
        # wsid: {
        #   info: { info },
        #   meta: { metadata },
        #   perms: { userid: perm },
        #   objects: { objid: {data: {}, info: []} }
        # }
        self.ws_db_counter = 1

    def administer(self, *args, **kwargs):
        return {"perms": [{"foo": "a", "bar": "w"}]}

    def _ws_info(self, user, ws_id, num_objects, metadata):
        return [
            ws_id,
            self._ws_name(ws_id),
            user,
            "2019-01-01-T20:10:10+0000",
            num_objects,
            "n",
            "r",
            "unlocked",
            metadata
        ]

    def _obj_info(self, user, ws_id, obj_id, obj_type):
        return [
            obj_id,
            "Object_{}-{}".format(ws_id, obj_id),
            obj_type,
            "2019-01-01-T22:10:10+0000",
            1,
            user,
            ws_id,
            self._ws_name(ws_id),
            "some_md5_hash",
            12345,
            None
        ]

    def _ws_name(self, ws_id):
        return "TestWs_{}".format(ws_id)

    def make_fake_narrative(self, name: str, owner: str) -> str:
        """
        Only in the Mocked object!
        This creates a fake narrative and adds it to the internal "database"
        Returns the narrative_ref
        (really this was just made for the NarrativeManager.rename_narrative unit tests.
        But it might be helpful elsewhere?)
        """
        ws_id = self.make_fake_workspace(owner)
        fake_narr = {
            "cells": [],
            "metadata": {
                "name": name,
                "creator": owner,
                "data_dependencies": [],
                "description": "",
                "format": "ipynb",
                "job_ids": {
                    "apps": [],
                    "methods": [],
                    "job_usage": {"queue_time": 0, "run_time": 0}
                },
                "type": "KBaseNarrative.Narrative",
                "ws_name": ws_id
            },
            "nbformat": 4,
            "nbformat_minor": 0
        }
        obj_id = self.make_fake_object(ws_id, fake_narr, "SomeNarrative", "KBaseNarrative.Narrative", owner, {
            "narrative_nice_name": name,
            "is_temporary": False,
            "searchtags": "narrative"
        })
        return f"{ws_id}/{obj_id}"

    def make_fake_object(self, ws_id: int, obj: dict, name: str, obj_type: str, user_id: str, meta: dict, obj_id: int=None) -> str:
        if ws_id not in self.internal_db:
            raise ValueError("invalid fake workspace")
        ver = 1
        if obj_id is None:
            obj_id = self.internal_db[ws_id]["oid_counter"]
            self.internal_db[ws_id]["oid_counter"] += 1
        else:
            ver = self.internal_db[ws_id]["objects"][obj_id]["info"][4] + 1
        obj_data = {
            "data": obj,
            "info": [obj_id, name, obj_type, "", ver, user_id, ws_id, self.internal_db[ws_id]["info"]["name"], "", 0, meta]
        }
        self.internal_db[ws_id]["objects"][obj_id] = obj_data
        return obj_id

    def make_fake_workspace(self, owner: str) -> int:
        ws_id = self.ws_db_counter
        self.internal_db[ws_id] = {
            "info": {
                "id": ws_id,
                "name": f"workspace-{ws_id}",
            },
            "perms": {owner: "a"},
            "meta": {},
            "objects": {},
            "oid_counter": 1
        }
        self.ws_db_counter += 1
        return ws_id

    def get_workspace_info(self, params):
        """
        Only used with params[id] right now (5/24/19), so return based on that.
        """
        return self._ws_info(self.user, params["id"], 10, self.ws_info_meta[params["id"]])

    def list_workspace_info(self, params):
        """
        Always returns the same list of ws infos, regardless of parameters.
        There's 5:
        1. no narrative associated
        2 and 3. Both have a Narrative, not is_temporary
        4. Has a Narrative in metadata, but is_temporary=true
        5. Has a narrative, is_temporary=false, show_in_narrative_data_panel=true
        """
        user = self.shared_user
        if "owner" in params:
            user = params["owner"][0]
        return [
            self._ws_info(user, 1, 10, self.ws_info_meta[1]),
            self._ws_info(user, 2, 10, self.ws_info_meta[2]),
            self._ws_info(user, 3, 10, self.ws_info_meta[3]),
            self._ws_info(user, 4, 10, self.ws_info_meta[4]),
            self._ws_info(user, 5, 10, self.ws_info_meta[5]),
        ]

    def list_objects(self, params):
        """
        Returns the same list of objects, with info adjusted to match the requesting workspace.
        Based on params["ids"], it returns 10 objects for each workspace.
        The first (id 1) will always be a Narrative
        The rest are dummy, KBaseModule.SomeType-N.0. where N ranges from 1 - 10 (for each id. so we can test version collapsing.)
        """
        obj_info_list = list()
        for ws_id in params.get('ids', []):
            obj_info_list.append(self._obj_info(self.user, ws_id, 1, "KBaseNarrative.Narrative-4.0"))
            obj_info_list.extend([self._obj_info(self.user, ws_id, i, f"KBaseModule.SomeType-{i-1}.0") for i in range(2, 11)])
        return obj_info_list

    def save_objects(self, params):
        ws_id = int(params.get("id"))
        saved_infos = list()
        for obj in params.get("objects", []):
            obj_id = int(obj.get("objid"))
            self.make_fake_object(ws_id, obj["data"], "SomeObject", obj["type"], self.user, obj["meta"], obj_id=obj_id)
            saved_infos.append(self.internal_db[ws_id]["objects"][obj_id]["info"])
        return saved_infos

    def get_objects2(self, params):
        obj_refs = params.get("objects", [])
        return_data = {"data": [], "paths": []}
        for obj_ref in obj_refs:
            ref = obj_ref.get("ref")  # all we use in this repo
            split_ref = ref.split("/")
            (ws_id, obj_id) = split_ref[0:2]
            ws_id = int(ws_id)
            obj_id = int(obj_id)
            if ws_id in self.internal_db and obj_id in self.internal_db[ws_id]["objects"]:
                return_data["data"].append(self.internal_db[ws_id]["objects"][obj_id])
                return_data["paths"].append(ref)
        return return_data

    def get_permissions_mass(self, params):
        ws_list = params.get("workspaces")
        perms_list = list()
        for ws_ref in ws_list:
            ws_id = int(ws_ref.get("id"))
            if ws_id not in self.internal_db:
                raise ValueError(f"WS {ws_id} not found.")
            perms_list.append(self.internal_db[ws_id]["perms"])
        return {"perms": perms_list}

    def alter_workspace_metadata(self, params):
        ws_id = int(params["wsi"]["id"])
        if ws_id not in self.internal_db:
            raise ValueError(f"Workspace {ws_id} not found")
        meta = params["new"]
        self.internal_db[ws_id]["meta"].update(meta)
