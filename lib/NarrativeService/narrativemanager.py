import contextlib
import json
import time
import uuid
from typing import Any

from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from installed_clients.WorkspaceClient import Workspace
from jsonrpcbase import ServerError
from NarrativeService.SearchServiceClient import SearchServiceClient
from NarrativeService.ServiceUtils import ServiceUtils

MAX_WS_METADATA_VALUE_SIZE = 900
NARRATIVE_TYPE = "KBaseNarrative.Narrative"


class NarrativeManager:

    KB_CELL = "kb-cell"
    KB_TYPE = "type"
    KB_APP_CELL = "kb_app"
    KB_FUNCTION_CELL = "function_input"
    KB_OUTPUT_CELL = "function_output"
    KB_ERROR_CELL = "kb_error"
    KB_CODE_CELL = "kb_code"
    KB_STATE = "widget_state"

    def __init__(
        self: "NarrativeManager",
        config: dict[str, Any],
        user_id: str,
        workspace_client: Workspace,
        search_service_client: SearchServiceClient
    ) -> None:
        self.narrativeMethodStoreURL = config["narrative-method-store"]
        self.user_id = user_id
        self.ws = workspace_client
        self.search_client = search_service_client
        self.intro_cell_file = config["intro-cell-file"]

    def get_narrative_doc(self: "NarrativeManager", narrative_upa: str) -> dict[str, Any]:
        try:
            # ensure correct upa format and get numerical ws_id
            ws_id, _, _, = (int(i) for i in narrative_upa.split("/"))
            obj_data = self.ws.get_objects2({"objects": [{"ref": narrative_upa}]})["data"][0]
        except ValueError as err:
            raise ValueError(
                "Incorrect upa format: required format is <workspace_id>/<object_id>/<version>"
            ) from err
        except ServerError as err:
            raise ValueError(
                f'Item with upa "{narrative_upa}" not found in workspace database.'
            ) from err

        data_objects = self.ws.list_objects({"ids": [ws_id]})
        permissions = self.ws.get_permissions_mass({"workspaces": [{"id": ws_id}]})["perms"]
        shared_users, is_public = self._fmt_doc_permissions(permissions)

        # get cells (checking for older narratives)
        if "worksheets" in obj_data["data"]:
            cells = obj_data["data"]["worksheets"][0]["cells"]
        else:
            cells = obj_data["data"]["cells"]

        return {
            "access_group": obj_data.get("orig_wsid", ws_id),
            "cells": [self._get_doc_cell(c) for c in cells],
            "total_cells": len(obj_data["data"]["cells"]),
            "data_objects": [{"name": o[1], "obj_type": o[2]}
                                for o in data_objects if "KBaseNarrative.Narrative" not in o[2]],
            "creator": obj_data["data"]["metadata"].get("kbase", {}).get("creator", ""),
            "shared_users": shared_users,
            "is_public": is_public,
            "timestamp": obj_data.get("epoch", 0),
            "creation_date": obj_data.get("created", ""),
            "narrative_title": obj_data["data"]["metadata"].get("name", ""),
            "version": obj_data["info"][4]
        }

    def _fmt_doc_permissions(
        self: "NarrativeManager",
        permissions: dict[str, str]
    ) -> tuple[list[str], bool]:
        # get list of users and whether a narrative is public
        is_public = False
        shared_users = []
        for permission in permissions:
            k, v = permission.popitem()
            if k == "*":
                is_public = (v != "n")
            elif v != "n":
                shared_users.append(k)
        return shared_users, is_public

    def _get_doc_cell(self: "NarrativeManager", cell: dict[str, Any]) -> dict[str, Any]:
        # get the appropriate cell format for search result doc
        meta = cell.get("metadata", {}).get("kbase", {})
        if cell["cell_type"] == "markdown":
            # type markdown
            return {
                "cell_type": "markdown",
                "desc": meta.get("attributes", {})
                            .get("title", "Markdown Cell")
            }
        if meta["type"] == "output":
            # type widget
            return {
                "cell_type": "widget",
                "desc": meta.get("outputCell", {})
                            .get("widget", {})
                            .get("name", "Widget")
            }
        if meta["type"] == "data":
            # type data
            return {
                "cell_type": "data",
                "desc": meta.get("dataCell", {})
                            .get("objectInfo", {})
                            .get("name", "Data Cell")
            }
        if meta["type"] == "app":
            # type kbase_app
            return {
                "cell_type": "kbase_app",
                "desc": meta.get("appCell")
                            .get("app", {})
                            .get("spec", {})
                            .get("info", {})
                            .get("name", "KBase App")
            }
        if meta["type"] == "code":
            # type code_cell
            return {
                "cell_type": "code_cell",
                "desc": cell.get("source", "Code Cell")
            }
        return {
            "cell_type": "",
            "desc": ""
        }

    def revert_narrative_object(self: "NarrativeManager", obj: dict[str, Any]) -> list[Any]:
        # check that there is a proper workspace id and object id
        if ("wsid" not in obj or "objid" not in obj):
            raise ValueError(
                "Please choose exactly 1 object identifier and 1 workspace identifier; "
                f"cannot select workspace based on criteria: {','.join(obj.keys())}"
            )

        # ensure version is specified
        if "ver" not in obj:
            raise ValueError(
                f"Cannot revert object {obj['wsid']}/{obj['objid']} without specifying "
                "a version to revert to"
            )

        # get most recent version number
        current_version = self.ws.get_object_history(obj)[-1][4]

        # make sure we're not reverting into the future
        if current_version < obj["ver"]:
            raise ValueError(
                f"Cannot revert object at version {current_version} to version {obj['ver']}"
            )

        # call to revert object
        revert_result = self.ws.revert_object(obj)

        # call to update metadata
        self.ws.alter_workspace_metadata({
            "wsi": {
                "id": obj["wsid"]
            },
            "new": {
                "narrative_nice_name": revert_result[10]["name"]
            }
        })

        # wait until new version number is indexed in search so that UI can load new result
        self._check_new_version_indexed(obj, revert_result[4])

        return revert_result

    def _check_new_version_indexed(
        self: "NarrativeManager",
        obj: dict[str, int | str],
        new_version: int
    ) -> dict[str, Any]:
        tries = 0
        max_tries: int = 60
        data = None
        while tries < max_tries and data is None:
            try:
                tries += 1
                time.sleep(1)
                data = self.search_client.search_workspace_by_id(
                    obj["wsid"], obj["objid"], version=new_version
                )
            except Exception:  # noqa: S112, BLE001
                # try again, the connection may be faulty
                continue

        if data is None:
            raise TimeoutError(
                f"Max tries for workspace {obj['wsid']}/{obj['objid']}/{new_version} exceeded; "
                "please try searching for new version later"
            )
        return data

    def copy_narrative(
        self: "NarrativeManager",
        new_name: str,
        workspace_ref: str,
        workspace_id: int
    ) -> dict[str, str]:
        time_ms = int(round(time.time() * 1000))
        new_ws_name = self.user_id + ":narrative_" + str(time_ms)
        # add the 'narrative' field to newWsMeta later.
        new_ws_meta = {
            "narrative_nice_name": new_name,
            "searchtags": "narrative"
        }

        # start with getting the existing narrative object.
        current_narrative = self.ws.get_objects([{"ref": workspace_ref}])[0]
        if not workspace_id:
            workspace_id = current_narrative["info"][6]
        # Let's prepare exceptions for clone the workspace.
        # 1) currentNarrative object:
        excluded_list = [{"objid": current_narrative["info"][0]}]
        # 2) let's exclude objects of types under DataPalette handling:

        # clone the workspace EXCEPT for currentNarrative object
        new_ws_id = self.ws.clone_workspace({
            "wsi": {"id": workspace_id},
            "workspace": new_ws_name,
            "meta": new_ws_meta,
            "exclude": excluded_list
        })[0]
        try:
            # update the ref inside the narrative object and the new workspace metadata.
            new_nar_metadata = current_narrative["info"][10]
            new_nar_metadata["name"] = new_name
            new_nar_metadata["ws_name"] = new_ws_name
            new_nar_metadata["job_info"] = json.dumps({"queue_time": 0, "running": 0,
                                                     "completed": 0, "run_time": 0, "error": 0})

            is_temporary = new_nar_metadata.get("is_temporary", "false")
            if "is_temporary" not in new_nar_metadata:
                if new_nar_metadata["name"] == "Untitled" or new_nar_metadata["name"] is None:
                    is_temporary = "true"
                new_nar_metadata["is_temporary"] = is_temporary

            current_narrative["data"]["metadata"]["name"] = new_name
            current_narrative["data"]["metadata"]["ws_name"] = new_ws_name
            current_narrative["data"]["metadata"]["job_ids"] = {"apps": [], "methods": [],
                                                               "job_usage": {"queue_time": 0,
                                                                             "run_time": 0}}
            # save the shiny new Narrative so it's at version 1
            new_nar_info = self.ws.save_objects({"id": new_ws_id, "objects":
                                               [{"type": current_narrative["info"][2],
                                                 "data": current_narrative["data"],
                                                 "provenance": current_narrative["provenance"],
                                                 "name": current_narrative["info"][1],
                                                 "meta": new_nar_metadata}]})
            # now, just update the workspace metadata to point
            # to the new narrative object

            if "worksheets" in current_narrative["data"]:  # handle legacy.
                num_cells = len(current_narrative["data"]["worksheets"][0]["cells"])
            else:
                num_cells = len(current_narrative["data"]["cells"])
            new_nar_id = new_nar_info[0][0]
            self.ws.alter_workspace_metadata({
                "wsi": {
                    "id": new_ws_id
                },
                "new": {
                    "narrative": str(new_nar_id),
                    "is_temporary": is_temporary,
                    "cell_count": str(num_cells)
                }
            })
            return {"newWsId": new_ws_id, "newNarId": new_nar_id}
        except Exception:
            # let's delete copy of workspace so it's out of the way - it's broken
            self.ws.delete_workspace({"id": new_ws_id})
            raise

    def create_new_narrative(
        self: "NarrativeManager",
        app: str,
        method: str,
        app_param: str,
        app_data: list[Any],
        markdown: str,
        copydata: str,
        import_data: list[str],
        include_intro_cell: bool,
        title: str
    ):
        if app and method:
            raise ValueError("Must provide no more than one of the app or method params")

        if not import_data and copydata:
            import_data = copydata.split(";")

        if not app_data and app_param:
            app_data = []
            for tmp_item in app_param.split(";"):
                tmp_tuple = tmp_item.split(",")
                step_pos = None
                if tmp_tuple[0]:
                    with contextlib.suppress(ValueError):
                        step_pos = int(tmp_tuple[0])
                app_data.append([step_pos, tmp_tuple[1], tmp_tuple[2]])
        cells = None
        if app:
            cells = [{"app": app}]
        elif method:
            cells = [{"method": method}]
        elif markdown:
            cells = [{"markdown": markdown}]
        narr_info = self._create_temp_narrative(
            cells, app_data, import_data, include_intro_cell, title
        )
        if title is not None:
            # update workspace info so it's not temporary
            pass
        return narr_info

    def _get_intro_cell(self: "NarrativeManager") -> dict[str, Any]:
        """
        Loads intro cell JSON from file
        """
        with open(self.intro_cell_file) as intro_cell:
            return json.load(intro_cell)

    def _create_temp_narrative(
        self: "NarrativeManager",
        cells: list[dict[str, Any]],
        parameters: list[list[Any]],
        import_data: list[str],
        include_intro_cell: bool,
        title: str
    ) -> dict[str, Any]:
        narr_id = int(round(time.time() * 1000))
        ws_name = self.user_id + ":narrative_" + str(narr_id)
        narrative_name = "Narrative." + str(narr_id)

        ws = self.ws
        ws_info = ws.create_workspace({"workspace": ws_name, "description": ""})
        [narrative_object, metadata_external] = self._fetch_narrative_objects(
            ws_name, cells, parameters, include_intro_cell, title
        )
        is_temporary = "true"
        if title is not None and title != "Untitled":
            is_temporary = "false"

        metadata_external["is_temporary"] = is_temporary
        object_info = ws.save_objects({
            "workspace": ws_name,
            "objects": [{
                "type": "KBaseNarrative.Narrative",
                "data": narrative_object,
                "name": narrative_name,
                "meta": metadata_external,
                "provenance": [{
                    "script": "NarrativeManager.py",
                    "description": "Created new Workspace/Narrative bundle."
                }],
                "hidden": 0
            }]
        })[0]
        object_info = ServiceUtils.object_info_to_object(object_info)
        ws_info = self._complete_new_narrative(ws_info[0], object_info["id"],
                                             import_data, is_temporary, title,
                                             len(narrative_object["cells"]))
        return {
            "workspaceInfo": ServiceUtils.workspace_info_to_object(ws_info),
            "narrativeInfo": object_info
        }

    def _fetch_narrative_objects(
        self: "NarrativeManager",
        ws_name: str,
        cells: list[dict[str, Any]],
        parameters: list[list[Any]],
        include_intro_cell: bool,
        title: str
    ) -> list[dict[str, Any]]:
        if not cells:
            cells = []
        if not title:
            title = "Untitled"

        # fetchSpecs
        app_spec_ids = []
        method_spec_ids = []
        spec_mapping = {"apps": {}, "methods": {}}
        for cell in cells:
            if "app" in cell:
                app_spec_ids.append(cell["app"])
            elif "method" in cell:
                method_spec_ids.append(cell["method"])
        nms = NarrativeMethodStore(self.narrativeMethodStoreURL)
        if len(app_spec_ids) > 0:
            app_specs = nms.get_app_spec({"ids": app_spec_ids})
            for spec in app_specs:
                spec_id = spec["info"]["id"]
                spec_mapping["apps"][spec_id] = spec
        if len(method_spec_ids) > 0:
            method_specs = nms.get_method_spec({"ids": method_spec_ids})
            for spec in method_specs:
                spec_id = spec["info"]["id"]
                spec_mapping["methods"][spec_id] = spec
        # end of fetchSpecs

        metadata = {
            "job_ids": {
                "methods": [],
                "apps": [],
                "job_usage": {"queue_time": 0, "run_time": 0}
            },
            "format": "ipynb",
            "creator": self.user_id,
            "ws_name": ws_name,
            "name": title,
            "type": "KBaseNarrative.Narrative",
            "description": "",
            "data_dependencies": []
        }
        cell_data = self._gather_cell_data(cells, spec_mapping, parameters, include_intro_cell)
        narrative_object = {
            "nbformat_minor": 0,
            "cells": cell_data,
            "metadata": metadata,
            "nbformat": 4
        }
        metadata_external = {}
        for key in metadata:
            value = metadata[key]
            if isinstance(value, str):
                metadata_external[key] = value
            else:
                metadata_external[key] = json.dumps(value)
        return [narrative_object, metadata_external]

    def _gather_cell_data(
        self: "NarrativeManager",
        cells: list[dict[str, Any]],
        spec_mapping: dict[str, Any],
        parameters: list[list[Any]],
        include_intro_cell: bool) -> list[dict[str, Any]]:
        cell_data = []
        if include_intro_cell == 1:
            cell_data.append(
                self._get_intro_cell()
            )
        for cell_pos, cell in enumerate(cells):
            if "app" in cell:
                cell_data.append(self._build_app_cell(len(cell_data),
                                                    spec_mapping["apps"][cell["app"]],
                                                    parameters))
            elif "method" in cell:
                cell_data.append(self._build_method_cell(len(cell_data),
                                                       spec_mapping["methods"][cell["method"]],
                                                       parameters))
            elif "markdown" in cell:
                cell_data.append({
                    "cell_type": "markdown",
                    "source": cell["markdown"],
                    "metadata": {}
                })
            else:
                raise ValueError(f"cannot add cell #{cell_pos}, unrecognized cell content")
        return cell_data

    def _build_app_cell(
        self: "NarrativeManager",
        pos: int,
        spec: dict[str, Any],
        params: list[list[Any]]
    ) -> dict[str, Any]:
        cell_id = "kb-cell-" + str(pos) + "-" + str(uuid.uuid4())
        cell = {
            "cell_type": "markdown",
            "source": "<div id='" + cell_id + "'></div>" +
                      "\n<script>" +
                      "$('#" + cell_id + "').kbaseNarrativeAppCell({'appSpec' : '" +
                      self._safe_json_stringify(spec) + "', 'cellId' : '" + cell_id + "'});" +
                      "</script>",
            "metadata": {}
        }
        cell_info = {}
        widget_state = []
        cell_info[self.KB_TYPE] = self.KB_APP_CELL
        cell_info["app"] = spec
        if params:
            steps = {}
            for param in params:
                stepid = "step_" + str(param[0])
                if stepid not in steps:
                    steps[stepid] = {}
                    steps[stepid]["inputState"] = {}
                steps[stepid]["inputState"][param[1]] = param[2]
            state = {"state": {"step": steps}}
            widget_state.append(state)
        cell_info[self.KB_STATE] = widget_state
        cell["metadata"][self.KB_CELL] = cell_info
        return cell

    def _build_method_cell(
        self: "NarrativeManager",
        pos: int,
        spec: dict[str, Any],
        params: list[list[Any]]
    ) -> dict[str, Any]:
        cell_id = "kb-cell-" + str(pos) + "-" + str(uuid.uuid4())
        cell = {"cell_type": "markdown",
                "source": "<div id='" + cell_id + "'></div>" +
                          "\n<script>" +
                          "$('#" + cell_id + "').kbaseNarrativeMethodCell({'method' : '" +
                          self._safe_json_stringify(spec) + "'});" +
                          "</script>",
                "metadata": {}}
        cell_info = {"method": spec,
                    "widget": spec["widgets"]["input"]}
        cell_info[self.KB_TYPE] = self.KB_FUNCTION_CELL
        widget_state = []
        if params:
            wparams = {}
            for param in params:
                wparams[param[1]] = param[2]
            widget_state.append({"state": wparams})
        cell_info[self.KB_STATE] = widget_state
        cell["metadata"][self.KB_CELL] = cell_info
        return cell

    def _complete_new_narrative(
        self: "NarrativeManager",
        ws_id: str | int,
        obj_id: str | int,
        import_data: list[str],
        is_temporary: int,
        title: str,
        num_cells: int
    ) -> list[Any]:
        """
        'Completes' the new narrative by updating workspace metadata with the required fields and
        copying in data from the importData list of references.
        """
        new_meta = {
            "narrative": str(obj_id),
            "is_temporary": is_temporary,
            "searchtags": "narrative",
            "cell_count": str(num_cells)
        }
        if is_temporary == "false" and title is not None:
            new_meta["narrative_nice_name"] = title

        self.ws.alter_workspace_metadata({"wsi": {"id": ws_id},
                                          "new": new_meta})
        # copy_to_narrative:
        if import_data:
            objects_to_copy = [{"ref": x} for x in import_data]
            info_list = self.ws.get_object_info_new({
                "objects": objects_to_copy,
                "includeMetadata": 0
            })
            for item in info_list:
                obj_info = ServiceUtils.object_info_to_object(item)
                self.copy_object(obj_info["ref"], ws_id, None, None, obj_info)

        return self.ws.get_workspace_info({"id": ws_id})

    def _safe_json_stringify(
        self: "NarrativeManager",
        obj: str | list[str] | dict[str, str]
    ) -> str | list[str] | dict[str, str]:
        return json.dumps(self._safe_json_stringify_prepare(obj))

    def _safe_json_stringify_prepare(
        self: "NarrativeManager",
        obj: str | list[str] | dict[str, str]
    ) -> str | list[str] | dict[str, str]:
        if isinstance(obj, str):
            return obj.replace("'", "&apos;").replace('"', "&quot;")
        if isinstance(obj, list):
            for pos in range(len(obj)):
                obj[pos] = self._safe_json_stringify_prepare(obj[pos])
        elif isinstance(obj, dict):
            obj_keys = list(obj.keys())
            for key in obj_keys:
                obj[key] = self._safe_json_stringify_prepare(obj[key])
        else:
            pass  # it's boolean/int/float/None
        return obj

    def copy_object(
        self: "NarrativeManager",
        ref: str,
        target_ws_id: str | int,
        target_ws_name: str,
        target_name: str,
        src_info: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Copies an object from one workspace to another.
        """
        if not target_ws_id and not target_ws_name:
            raise ValueError("Neither target workspace id nor name is defined")
        if not src_info:
            src_info_tuple = self.ws.get_object_info_new({"objects": [{"ref": ref}],
                                                          "includeMetadata": 0})[0]
            src_info = ServiceUtils.object_info_to_object(src_info_tuple)
        if not target_name:
            target_name = src_info["name"]
        obj_info_tuple = self.ws.copy_object({
            "from": {"ref": ref},
            "to": {
                "wsid": target_ws_id,
                "workspace": target_ws_name,
                "name": target_name
            }
        })
        obj_info = ServiceUtils.object_info_to_object(obj_info_tuple)
        return {"info": obj_info}

    def rename_narrative(
        self: "NarrativeManager",
        narrative_ref: str,
        new_name: str,
        service_version: str
    ) -> str:
        """
        Renames a Narrative.
        If the current user (as set by the auth token in self.ws) has admin permission on the
        workspace, then this does the following steps.
        1. Fetch the Narrative object and save it with the name change in the metadata.
        2. Update the workspace metadata so that it has the new name as the narrative nice name.
        3. Flips the workspace metadata so the the narrative is no longer temporary, if it was.

        :param narrative_ref: string, format = "###/###" or "###/###/###" (though the latter is
            very not recommended)
        :param new_name: string, new name for the narrative
        :param service_version: NarrativeService version so the provenance can be tracked properly.
        """
        # 1. Validate inputs.
        if not new_name or not isinstance(new_name, str):
            raise ValueError("new_name should be a non-empty string")

        if len(new_name.encode("utf-8")) > MAX_WS_METADATA_VALUE_SIZE:
            raise ValueError(f"new_name must be less than {MAX_WS_METADATA_VALUE_SIZE} bytes")

        if not narrative_ref or not isinstance(narrative_ref, str):
            raise ValueError("narrative_ref must be a string of format ###/###")

        ref = ServiceUtils.numerical_ref_to_dict(narrative_ref)
        ws_id = ref.get("ws_id")
        if not ws_id or not ref["obj_id"]:
            raise ValueError("narrative_ref must be a string of format ###/###")

        # 2. Check permissions
        perm = ServiceUtils.get_user_workspace_permissions(self.user_id, ws_id, self.ws)
        if perm != "a":
            raise ValueError(
                f"User {self.user_id} must have admin rights to change "
                f"the name of the narrative in workspace {ws_id}"
            )

        # 3. Get narrative object
        narr_obj = self.ws.get_objects2({"objects": [{"ref": narrative_ref}]})["data"][0]

        # 3a. Rename the right fields there.
        if narr_obj["data"]["metadata"]["name"] == new_name:
            # no-op, return the current UPA.
            return f"{narr_obj['info'][6]}/{narr_obj['info'][1]}/{narr_obj['info'][4]}"
        narr_obj["data"]["metadata"]["name"] = new_name
        narr_obj["info"][10]["name"] = new_name

        # 4. Update workspace metadata
        updated_metadata = {
            "is_temporary": "false",
            "narrative_nice_name": new_name,
            "searchtags": "narrative"
        }
        self.ws.alter_workspace_metadata({"wsi": {"id": ws_id}, "new": updated_metadata})

        # 5. Save the Narrative object. Keep all the things intact, with new provenance saying we
        # renamed with the NarrativeService.
        ws_save_obj = {
            "type": NARRATIVE_TYPE,
            "data": narr_obj["data"],
            "objid": ref["obj_id"],
            "meta": narr_obj["info"][10],
            "provenance": [{
                "service": "NarrativeService",
                "description": "Renamed by Narrative Service",
                "service_ver": service_version
            }]
        }
        obj_info = self.ws.save_objects({
            "id": ws_id,
            "objects": [ws_save_obj]
        })[0]
        return f"{obj_info[6]}/{obj_info[0]}/{obj_info[4]}"
