from biokbase.workspace.client import Workspace
from ..authclient import KBaseAuth
from ..WorkspaceListObjectsIterator import WorkspaceListObjectsIterator


class DataFetcher(object):
    def __init__(self, ws_url, auth_url, token):
        self._ws = Workspace(url=ws_url, token=token)
        auth = KBaseAuth(auth_url=auth_url)
        self._user = auth.get_user(token)

    def fetch_data(self, params):
        """
        params is a dict with (expected) keys:
        data_set - string, should be one of "mine" or "shared", anything else will throw an error
        include_type_counts - boolean, default 0
        simple_types - boolean, default 0
        ignore_narratives - boolean, default 1
        """
        self._validate_params(params)
        which = params.get("data_set").lower()
        if which == "mine":
            return self._fetch_my_data(params)
        else:
            return self._fetch_shared_data(params)

    def _validate_params(self, params):
        if params.get("data_set", "").lower() not in ["mine", "shared"]:
            raise ValueError("Parameter 'data_set' must be either 'mine' or 'shared', not '{}'".format(params.get("data_set")))

        for p in ["include_type_counts", "simple_types", "ignore_narratives"]:
            self._validate_boolean(params, p)

        if not isinstance(params.get("ignore_workspaces", []), list):
            raise ValueError("Parameter 'ignore_workspaces' must be a list if present")

    def _validate_boolean(self, params, param_name):
        if params.get(param_name, 0) not in [0, 1]:
            raise ValueError("Parameter '{}' must be 0 or 1, not '{}'".format(param_name, params.get(param_name)))

    def _fetch_my_data(self, params):
        get_info_params = {
            "owners": [self._user]
        }
        workspaces = self._get_non_temporary_workspaces(get_info_params)
        objects = self._fetch_all_objects([workspaces[w]["info"] for w in workspaces])
        return objects

    def _fetch_shared_data(self, params):
        pass

    def _fetch_all_objects(self, ws_info_list, include_metadata=0):
        items = list()
        for info in WorkspaceListObjectsIterator(
            self._ws,
            ws_info_list=ws_info_list,
            list_objects_params={"includeMetadata": include_metadata}
        ):
            items.append(info)
        return items

    def _get_non_temporary_workspaces(self, get_info_params):
        """
        Given a set of workspaces.list_workspace_info parameters, this runs the
        list_workspace_info function and mucks with the results. It only returns workspaces
        that are NOT marked "is_temporary"=="true" in their metadata, and adds a display
        name for them based on either the Narrative name, or some legacy / data only state
        "Legacy" is given for those old workspaces that pre-date the "is_temporary" stuff
        and haven't been updated.
        "Data only" is given for workspaces that have a special flag set by JGI imports.

        This is returned as a dictionary.
        keys = numerical workspace ids
        values = dict with keys "display" (for the display name) and "info" for the
            workspace info tuple
        """
        ws_list = self._ws.list_workspace_info(get_info_params)
        workspaces = dict()
        for ws in ws_list:
            if ws[8].get("is_temporary", "false") == "true":
                continue
            ws_name = ws[1]
            display_name = ws[8].get("narrative_nice_name")
            if not display_name and ws[8].get("show_in_narrative_data_panel"):
                display_name = "(data only) " + ws_name
            elif not display_name:
                display_name = "Legacy (" + ws_name + ")"
            workspaces[ws[0]] = {
                "info": ws,
                "display": display_name
            }
        return workspaces
