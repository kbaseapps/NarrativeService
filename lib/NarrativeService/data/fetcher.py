from biokbase.workspace.client import Workspace
from ..authclient import KBaseAuth
from ..WorkspaceListObjectsIterator import WorkspaceListObjectsIterator
from collections import defaultdict


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
        (ws_info_list, ws_display) = self._get_workspaces(params)
        data_objects = self._fetch_all_objects(ws_info_list, include_metadata=params.get("include_metadata", 0))
        # now, post-process the data objects.
        return_objects = list()
        ignore_narratives = params.get("ignore_narratives", 1) == 1
        simple_types = params.get("simple_types", 0) == 1
        for obj in data_objects:
            if ignore_narratives and obj[2].startswith("KBaseNarrative"):
                continue
            obj_type = self._parse_type(obj[2], simple_types)
            ws_id = obj[6]
            return_objects.append({
                "ws_id": ws_id,
                "obj_id": obj[0],
                "ver": obj[4],
                "saved_by": obj[5],
                "name": obj[1],
                "type": obj_type,
                "timestamp": obj[3]
            })
            ws_display[ws_id]["count"] += 1  # gets initialized back in _get_non_temporary_workspaces
        return_val = {
            "workspace_display": ws_display,
            "objects": return_objects,
            "ws_info": ws_info_list
        }
        if params.get("include_type_counts", 0) == 1:
            type_counts = defaultdict(lambda: 0)
            for obj in return_objects:
                type_counts[obj["type"]] += 1
            return_val["type_counts"] = type_counts
        return return_val

    def _parse_type(self, obj_type, simple_types=False):
        """
        Parses a type name, optionally.
        If simple_types = True, returns just the central subtype (KBaseNarrative.Narrative-4.0 -> Narrative)
        """
        if not simple_types:
            return obj_type
        else:
            return obj_type.split('-')[0].split('.')[1]

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

    def _get_workspaces(self, params):
        """
        Gets the workspaces and workspace info for this run, based on the parameters. So, all of the user's
        workspaces or all workspaces explicitly shared with the user, or all global workspaces(?)
        """
        which_set = params["data_set"].lower()
        if which_set == "mine":
            get_info_params = {"owners": [self._user]}
        else:
            get_info_params = {"excludeGlobal": 1}
        (all_ws_list, workspace_dict) = self._get_non_temporary_workspaces(get_info_params, params.get("ignore_workspaces", []))
        if which_set == "shared":
            shared_ws_list = list(filter(lambda w: w[2] != self._user, all_ws_list))
            workspace_dict = {w[0]: workspace_dict[w[0]] for w in shared_ws_list}
            all_ws_list = shared_ws_list
        return (all_ws_list, workspace_dict)

    def _fetch_all_objects(self, ws_info_list, include_metadata=0):
        items = list()
        for info in WorkspaceListObjectsIterator(
            self._ws,
            ws_info_list=ws_info_list,
            list_objects_params={"includeMetadata": include_metadata}
        ):
            items.append(info)
        return items

    def _get_non_temporary_workspaces(self, get_info_params, ignore_workspaces):
        """
        Given a set of workspaces.list_workspace_info parameters, this runs the
        list_workspace_info function and mucks with the results. It only returns workspaces
        that are NOT marked "is_temporary"=="true" in their metadata, and adds a display
        name for them based on either the Narrative name, or some legacy / data only state
        "Legacy" is given for those old workspaces that pre-date the "is_temporary" stuff
        and haven't been updated.
        "Data only" is given for workspaces that have a special flag set by JGI imports.

        get_info_params - parameters that pass to the list_workspace_info function
            (See workspace docs)
        ignore_workspaces - list of workspace ids that will get auto-filtered out

        This is returned as a 2-tuple.
        first element = list of workspace info
        second element = dict where keys are the numerical workspace ids, and
            values are the display name for the workspace (later augmented with
            data object counts)
        """
        ws_list = self._ws.list_workspace_info(get_info_params)
        return_list = list()
        workspaces = dict()
        for ws in ws_list:
            if ws[0] in ignore_workspaces or ws[8].get("is_temporary", "false") == "true":
                continue
            ws_name = ws[1]
            display_name = ws[8].get("narrative_nice_name")
            if not display_name and ws[8].get("show_in_narrative_data_panel"):
                display_name = "(data only) " + ws_name
            elif not display_name:
                display_name = "Legacy (" + ws_name + ")"
            workspaces[ws[0]] = {
                "display": display_name,
                "count": 0  # initial object count - this gets filled out later.
            }
            return_list.append(ws)
        return (return_list, workspaces)
