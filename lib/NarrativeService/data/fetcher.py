from biokbase.workspace.client import Workspace
from ..authclient import KBaseAuth
from ..WorkspaceListObjectsIterator import WorkspaceListObjectsIterator
from collections import defaultdict

DEFAULT_DATA_LIMIT = 30000

class DataFetcher(object):
    def __init__(self, ws_url, auth_url, token):
        """
        The data fetcher needs a workspace client and auth client.
        It needs Auth to get the current user id out of the token, so we know what workspaces
        are actually shared as opposed to just visible.

        Args:
            ws_url (str): Workspace service URL
            auth_url (str): Auth service URL
            token (str): auth token
        """
        self._ws = Workspace(url=ws_url, token=token)
        auth = KBaseAuth(auth_url=auth_url)
        self._user = auth.get_user(token)

    def fetch_accessible_data(self, params):
        """
        Returns all data accessible to the user.

        params (dict):
            data_set (str): one of "mine" or "shared" - which data set to return. "mine" comes from
                            workspaces owned by the user, shared are only those shared with the
                            user, and NOT those that are public
            ignore_workspaces (list<int>, optional): list of workspace ids to not fetch data from
            include_type_counts (boolean (0, 1), def 0): if 1, return a dict of type counts
            simple_types (boolean (0, 1), def 0): if 1, "simplify" all type strings to just the
                                                  type (cut the module)
            ignore_narratives (boolean (0, 1), def 1): if 1, don't return any Narrative objects
            types (list<str>, optional): if present, only return these types. These are expected
                                         to be type strings with the format "Module.Type"
            limit (int, optional): maximum number of objects to return

        Returns a dict with keys:
            workspace_display (dict): each key is a workspace id, values are smaller dicts
                                      with a "display" key (for how the workspace should be shown
                                      in the browser) and "count" key (number of objects returned)
            objects (list<dict>): list of dicts that describe an object. Each dict has keys:
                ws_id (int): the workspace id
                obj_id (int): the object id
                ver (int): the object version
                saved_by (str): the user id who saved that object
                name (str): the object name
                type (str): the object data type (Module.Type-Major_version.Minor_version, or just
                            Type if simple_types==1. E.g. KBaseGenomes.Genome-1.0 or Genome)
                timestamp (str): the ISO 8601 timestamp when the object was saved
            ws_info (list<list>): list of workspace info tuples for all workspaces returned. See
                                  the Workspace docs for details.
            type_counts (dict): dict where each type is a key and each value is the number of
                                instances of that type returned
        """
        if 'limit' not in params:
            params['limit'] = DEFAULT_DATA_LIMIT
        self._validate_list_all_params(params)
        (ws_info_list, ws_display) = self._get_accessible_workspaces(params)
        # do same stuff as other function
        return self._fetch_data(ws_info_list, ws_display, params)

    def fetch_specific_workspace_data(self, params):
        """
        Returns all data from a list of workspaces.
        If the user doesn't have access to any of those workspaces, then a Workspace error will
        get raised.

        params (dict):
            workspace_ids (list<int>): a list of workspace ids to search for data. Must be present
                                       with at least one element.
            ignore_workspaces (list<int>, optional): list of workspace ids to not fetch data from
            include_type_counts (boolean (0, 1), def 0): if 1, return a dict of type counts
            simple_types (boolean (0, 1), def 0): if 1, "simplify" all type strings to just the
                                                  type (cut the module)
            ignore_narratives (boolean (0, 1), def 1): if 1, don't return any Narrative objects
            types (list<str>, optional): if present, only return these types. These are expected
                                         to be type strings with the format "Module.Type"
            limit (int, optional): maximum number of objects to return

        Returns a dict with keys:
            workspace_display (dict): each key is a workspace id, values are smaller dicts
                                      with a "display" key (for how the workspace should be shown
                                      in the browser) and "count" key (number of objects returned)
            objects (list<dict>): list of dicts that describe an object. Each dict has keys:
                ws_id (int): the workspace id
                obj_id (int): the object id
                ver (int): the object version
                saved_by (str): the user id who saved that object
                name (str): the object name
                type (str): the object data type (Module.Type-Major_version.Minor_version, or just
                            Type if simple_types==1. E.g. KBaseGenomes.Genome-1.0 or Genome)
                timestamp (str): the ISO 8601 timestamp when the object was saved
            ws_info (list<list>): list of workspace info tuples for all workspaces returned. See
                                  the Workspace docs for details.
            type_counts (dict): dict where each type is a key and each value is the number of
                                instances of that type returned
        """
        if 'limit' not in params:
            params['limit'] = DEFAULT_DATA_LIMIT
        self._validate_list_workspace_params(params)
        (ws_info_list, ws_display) = self._get_workspace_infos(params["workspace_ids"])
        return self._fetch_data(ws_info_list, ws_display, params)

    def _fetch_data(self, ws_info_list, ws_display, params):
        """
        Fetches and returns all data from the workspaces in ws_info_list, collates it, and arranges
        it into a helpful structure.

        Args:
            ws_info_list (list<list>): list of Workspace info tuples (see the workspace docs). This
                                       is the list of workspaces to comb for data to return.
            ws_display (dict): the pre-made dictionary for workspace display info. Should contain
                               a "display" key and a "count" key (that would be 0). This updates
                               the "count" key with the number of objects found in that workspace
                               that match the other parameters.
            params (dict):
                ignore_narratives (boolean (0, 1) def 1): if 1, ignores any KBaseNarrative.Narrative
                                                          objects found
                simple_types (boolean (0, 1) def 0): if 1, transforms all type strings to just get
                                                     the type (e.g. KBaseGenomes.Genome -> Genome)
                types (list<str>, optional): if present, only returns the types that are present in
                                             the list. They should be of format "Module.Type"
                include_type_counts (boolean (0, 1) def 0): if 1, return the counts of each type in
                                                            a dictionary keyed on the type.

        Returns a dict with keys:
            workspace_display (dict): each key is a workspace id, values are smaller dicts
                                      with a "display" key (for how the workspace should be shown
                                      in the browser) and "count" key (number of objects returned)
            objects (list<dict>): list of dicts that describe an object. Each dict has keys:
                ws_id (int): the workspace id
                obj_id (int): the object id
                ver (int): the object version
                saved_by (str): the user id who saved that object
                name (str): the object name
                type (str): the object data type (Module.Type-Major_version.Minor_version, or just
                            Type if simple_types==1. E.g. KBaseGenomes.Genome-1.0 or Genome)
                timestamp (str): the ISO 8601 timestamp when the object was saved
            ws_info (list<list>): list of workspace info tuples for all workspaces returned. See
                                  the Workspace docs for details.
            type_counts (dict): dict where each type is a key and each value is the number of
                                instances of that type returned
        """
        data_objects = self._fetch_all_objects(ws_info_list, include_metadata=params.get("include_metadata", 0))
        # now, post-process the data objects.
        return_objects = list()
        ignore_narratives = params.get("ignore_narratives", 1) == 1
        simple_types = params.get("simple_types", 0) == 1
        type_set = None
        if 'types' in params:
            type_set = set(params['types'])
        for obj in data_objects:
            if ignore_narratives and obj[2].startswith("KBaseNarrative"):
                continue
            if type_set and not obj[2].split('-')[0] in type_set:
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
        return_objects.sort(key=lambda obj: obj['timestamp'], reverse=True)
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
        If simple_types = True, returns just the central subtype (e.g. KBaseNarrative.Narrative-4.0
        becomes Narrative)

        Args:
            obj_type (str): the original type string
            simple_types (boolean): if True, do the parsing
        Returns:
            a parsed (or not) type string
        """
        if not simple_types:
            return obj_type
        else:
            return obj_type.split('-')[0].split('.')[1]

    def _validate_common_params(self, params):
        """
        Validates all parameters common to the two forms of data lookup. These are all optional,
        so we only raise errors if they're present. But if they are present, but malformatted,
        this raises a ValueError.

        include_type_counts, simple_types, and ignore_narratives should be "boolean"
        (KBase SDK style - ints with 0 or 1)

        limit should be an int > 0

        types should be a list

        The rest are optional "common" params.
        """
        for p in ["include_type_counts", "simple_types", "ignore_narratives"]:
            self._validate_boolean(params, p)

        limit = params['limit']
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("Parameter 'limit' must be an integer > 0.")

        if not isinstance(params.get("types", []), list):
            raise ValueError("Parameter 'types' must be a list if present.")

    def _validate_list_all_params(self, params):
        """
        Validates the parameters intended to be sent to the fetch_accessible_data function /
        NarrativeService.list_all_data.

        data_set must be present and "mine" or "shared"

        ignore_workspaces must be a list, if present
        """
        if params.get("data_set", "").lower() not in ["mine", "shared"]:
            raise ValueError("Parameter 'data_set' must be either 'mine' or 'shared', not '{}'.".format(params.get("data_set")))

        if not isinstance(params.get("ignore_workspaces", []), list):
            raise ValueError("Parameter 'ignore_workspaces' must be a list if present.")

        self._validate_common_params(params)

    def _validate_list_workspace_params(self, params):
        """
        Validates the parameters intended to be sent to the fetch_specific_workspace_data /
        NarrativeService.list_workspace_data function.

        workspace_ids must be present and a list of integers

        The rest are optional common params.
        """
        ws_ids_err = "Parameter 'workspace_ids' must be a list of integers."
        if "workspace_ids" not in params or \
           not isinstance(params["workspace_ids"], list) or \
           len(params["workspace_ids"]) == 0:
            raise ValueError(ws_ids_err)

        for ws_id in params["workspace_ids"]:
            if not isinstance(ws_id, int):
                raise ValueError(ws_ids_err)

        self._validate_common_params(params)

    def _validate_boolean(self, params, param_name):
        """
        Validates a KBase SDK-style boolean in a params dict. The value has to be 0 or 1 if present
        or it raises a ValueError.

        Args:
            params (dict): dict of params to skim
            param_name (str): the name of the parameter to investigate
        Returns:
            None if all is well, raises a ValueError otherwise.
        """
        if params.get(param_name, 0) not in [0, 1]:
            raise ValueError("Parameter '{}' must be 0 or 1, not '{}'".format(param_name, params.get(param_name)))

    def _get_accessible_workspaces(self, params):
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

    def _get_workspace_infos(self, ws_ids):
        """
        From a set of workspace ids, return a set of workspace info. These workspaces
        are given a display name based on either the Narrative name, or some legacy / data only
        state.
        "Legacy" is given for thsoe old workspaces that pre-date the "is_temporary" stuff
        and haven't been updated.
        "Data only" is given for workspaces that have a special flag set by JGI imports.

        This returns a 2-tuple.
        first element = list of workspace info
        second element = dict where keys are the numerical workspace ids, and
            values are the display name for the workspace (later augmented with
            data object counts)
        """
        ws_info_list = [self._ws.get_workspace_info({"id": ws_id}) for ws_id in ws_ids]
        ws_display = self._get_ws_display(ws_info_list)
        return (ws_info_list, ws_display)

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
        for ws in ws_list:
            if ws[0] in ignore_workspaces or ws[8].get("is_temporary", "false") == "true":
                continue
            return_list.append(ws)
        return (return_list, self._get_ws_display(return_list))

    def _get_ws_display(self, ws_info_list):
        """
        Creates and returns a dict of workspace display info from the list
        of workspace infos.
        This dict has the workspace ids for keys and a dictionary with a key "display"
        and value of the display name as values, and a "count" key that's initialized to 0.
        This is intended to pre-process the workspace info results.
        So:
        {
            384: {
                "display": "Some Narrative",
                "count": 0
            },
            456: {
                "display": "Legacy (some_ws_name)",
                "count": 0
            },
            ...etc...
        }
        """
        ws_display_info = dict()
        for ws_info in ws_info_list:
            display_name = self._get_display_name(ws_info)
            ws_display_info[ws_info[0]] = {
                "display": display_name,
                "count": 0
            }
        return ws_display_info

    def _get_display_name(self, ws_info):
        """
        From a workspace info tuple, figure out the proper display name for a workspace with
        these rules:
        1. If there's a "narrative_nice_name" in the metadata, use that.
        2. If there's "show_in_narrative_data_panel" in the metadata, use that with "(data only)"
            in the front
        3. If there's still no result, use the name "Legacy (workspace name)"
        """
        meta = ws_info[8]

        display_name = meta.get("narrative_nice_name")
        if not display_name and meta.get("show_in_narrative_data_panel"):
            display_name = "(data only) " + ws_info[1]
        elif not display_name:
            display_name = "Legacy (" + ws_info[1] + ")"
        return display_name
