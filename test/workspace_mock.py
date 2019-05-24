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
        The rest are dummy, KBaseModule.SomeType-1.0.
        """
        obj_info_list = list()
        for ws_id in params.get('ids', []):
            obj_info_list.append(self._obj_info(self.user, ws_id, 1, "KBaseNarrative.Narrative-4.0"))
            obj_info_list.extend([self._obj_info(self.user, ws_id, i, "KBaseModule.SomeType-1.0") for i in range(2, 11)])
        return obj_info_list
