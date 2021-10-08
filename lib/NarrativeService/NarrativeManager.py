import json
import time
import uuid

from NarrativeService.ServiceUtils import ServiceUtils
from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from jsonrpcbase import ServerError

MAX_WS_METADATA_VALUE_SIZE = 900
NARRATIVE_TYPE = "KBaseNarrative.Narrative"


class NarrativeManager:

    KB_CELL = 'kb-cell'
    KB_TYPE = 'type'
    KB_APP_CELL = 'kb_app'
    KB_FUNCTION_CELL = 'function_input'
    KB_OUTPUT_CELL = 'function_output'
    KB_ERROR_CELL = 'kb_error'
    KB_CODE_CELL = 'kb_code'
    KB_STATE = 'widget_state'

    def __init__(self, config, user_id, set_api_client, data_palette_client, workspace_client):
        self.narrativeMethodStoreURL = config["narrative-method-store"]
        self.set_api_client = set_api_client                     # DynamicServiceCache type
        self.data_palette_client = data_palette_client          # DynamicServiceCache type
        self.user_id = user_id
        self.ws = workspace_client
        self.intro_cell_file = config["intro-cell-file"]

    # def get_narrative_doc(self, ws_id, narrative_upa):
    def get_narrative_doc(self, narrative_upa):
        try:
            # ensure correct upa format and get numerical ws_id
            ws_id, _, _, = [int(i) for i in narrative_upa.split('/')]
            obj_data = self.ws.get_objects2({'objects': [{'ref': narrative_upa}]})
        except ValueError as e:
            raise ValueError('Incorrect upa format: required format is <workspace_id>/<object_id>/<version>')
        except ServerError as e:
            raise ValueError('Item with upa "%s" not found in workspace database.' % narrative_upa)

        data_objects = self.ws.list_objects({'ids': [ws_id]})
        permissions = self.ws.get_permissions_mass({'workspaces': [{'id': ws_id}]})['perms']
        shared_users, is_public = self._fmt_doc_permissions(permissions)

        doc = {
            'access_group': obj_data.get('orig_wsid', ws_id),
            'cells': [self._get_doc_cell(c) for c in obj_data['data'][0]['data']['cells']],
            'total_cells': len(obj_data['data'][0]['data']['cells']),
            'data_objects': [{'name': o[1], 'obj_type': o[2]} for o in data_objects],
            'creator': obj_data['data'][0]['data']['metadata'].get('kbase', {}).get('creator', ''),
            'shared_users': shared_users,
            'is_public': is_public,
            'timestamp': obj_data.get('epoch', 0),
            'creation_date': obj_data['created'],
            'narrative_title': obj_data['data'][0]['data']['metadata'].get('name', ''),
            'version': obj_data['data'][0]['info'][4]
        }

        return doc

    def _fmt_doc_permissions(self, permissions):
        # get list of users and whether a narrative is public
        is_public = False
        shared_users = []
        for permission in permissions:
            k, v = permission.popitem()
            if k == '*':
                is_public = (v != 'n')
            elif v != 'n':
                shared_users.append(k)
        return shared_users, is_public

    def _get_doc_cell(self, cell):
        # get the appropriate cell format for search result doc
        meta = cell.get('metadata', {}).get('kbase', {})
        if cell['cell_type'] == 'markdown':
            # type markdown
            return {
                'cell_type': 'markdown',
                'desc': meta.get('attributes', {})
                            .get('title', 'Markdown Cell')
            }
        elif meta['type'] == 'output':
            # type widget
            return {
                'cell_type': 'widget',
                'desc': meta.get('outputCell', {})
                            .get('widget', {})
                            .get('name', 'Widget')
            }
        elif meta['type'] == 'data':
            # type data
            return {
                'cell_type': 'data',
                'desc': meta.get('dataCell', {})
                            .get('objectInfo', {})
                            .get('name', 'Data Cell')
            }
        elif meta['type'] == 'app':
            # type kbase_app
            return {
                'cell_type': 'kbase_app',
                'desc': meta.get('appCell')
                            .get('app', {})
                            .get('spec', {})
                            .get('info', {})
                            .get('name', 'KBase App')
            }
        elif meta['type'] == 'code':
            # type code_cell
            return {
                'cell_type': 'code_cell',
                'desc': cell.get('source', 'Code Cell')
            }
        else:
            return {
                'cell_type': '',
                'desc': ''
            }

    def copy_narrative(self, newName, workspaceRef, workspaceId):
        time_ms = int(round(time.time() * 1000))
        newWsName = self.user_id + ':narrative_' + str(time_ms)
        # add the 'narrative' field to newWsMeta later.
        newWsMeta = {
            "narrative_nice_name": newName,
            "searchtags": "narrative"
        }

        # start with getting the existing narrative object.
        currentNarrative = self.ws.get_objects([{'ref': workspaceRef}])[0]
        if not workspaceId:
            workspaceId = currentNarrative['info'][6]
        # Let's prepare exceptions for clone the workspace.
        # 1) currentNarrative object:
        excluded_list = [{'objid': currentNarrative['info'][0]}]
        # 2) let's exclude objects of types under DataPalette handling:

        # clone the workspace EXCEPT for currentNarrative object
        newWsId = self.ws.clone_workspace({
            'wsi': {'id': workspaceId},
            'workspace': newWsName,
            'meta': newWsMeta,
            'exclude': excluded_list
        })[0]
        try:
            # update the ref inside the narrative object and the new workspace metadata.
            newNarMetadata = currentNarrative['info'][10]
            newNarMetadata['name'] = newName
            newNarMetadata['ws_name'] = newWsName
            newNarMetadata['job_info'] = json.dumps({'queue_time': 0, 'running': 0,
                                                     'completed': 0, 'run_time': 0, 'error': 0})

            is_temporary = newNarMetadata.get('is_temporary', 'false')
            if 'is_temporary' not in newNarMetadata:
                if newNarMetadata['name'] == 'Untitled' or newNarMetadata['name'] is None:
                    is_temporary = 'true'
                newNarMetadata['is_temporary'] = is_temporary

            currentNarrative['data']['metadata']['name'] = newName
            currentNarrative['data']['metadata']['ws_name'] = newWsName
            currentNarrative['data']['metadata']['job_ids'] = {'apps': [], 'methods': [],
                                                               'job_usage': {'queue_time': 0,
                                                                             'run_time': 0}}
            # save the shiny new Narrative so it's at version 1
            newNarInfo = self.ws.save_objects({'id': newWsId, 'objects':
                                               [{'type': currentNarrative['info'][2],
                                                 'data': currentNarrative['data'],
                                                 'provenance': currentNarrative['provenance'],
                                                 'name': currentNarrative['info'][1],
                                                 'meta': newNarMetadata}]})
            # now, just update the workspace metadata to point
            # to the new narrative object

            if 'worksheets' in currentNarrative['data']:  # handle legacy.
                num_cells = len(currentNarrative['data']['worksheets'][0]['cells'])
            else:
                num_cells = len(currentNarrative['data']['cells'])
            newNarId = newNarInfo[0][0]
            self.ws.alter_workspace_metadata({
                'wsi': {
                    'id': newWsId
                },
                'new': {
                    'narrative': str(newNarId),
                    'is_temporary': is_temporary,
                    'cell_count': str(num_cells)
                }
            })
            return {'newWsId': newWsId, 'newNarId': newNarId}
        except Exception:
            # let's delete copy of workspace so it's out of the way - it's broken
            self.ws.delete_workspace({'id': newWsId})
            raise

    def create_new_narrative(self, app, method, appparam, appData, markdown,
                             copydata, importData, includeIntroCell, title):
        if app and method:
            raise ValueError("Must provide no more than one of the app or method params")

        if not importData and copydata:
            importData = copydata.split(';')

        if not appData and appparam:
            appData = []
            for tmp_item in appparam.split(';'):
                tmp_tuple = tmp_item.split(',')
                step_pos = None
                if tmp_tuple[0]:
                    try:
                        step_pos = int(tmp_tuple[0])
                    except ValueError:
                        pass
                appData.append([step_pos, tmp_tuple[1], tmp_tuple[2]])
        cells = None
        if app:
            cells = [{"app": app}]
        elif method:
            cells = [{"method": method}]
        elif markdown:
            cells = [{"markdown": markdown}]
        narr_info = self._create_temp_narrative(cells, appData, importData, includeIntroCell, title)
        if title is not None:
            # update workspace info so it's not temporary
            pass
        return narr_info

    def _get_intro_cell(self):
        """
        Loads intro cell JSON from file
        """
        with open(self.intro_cell_file) as intro_cell:
            return json.load(intro_cell)

    def _create_temp_narrative(self, cells, parameters, importData, includeIntroCell, title):
        # Migration to python of JavaScript class from https://github.com/kbase/kbase-ui/blob/4d31151d13de0278765a69b2b09f3bcf0e832409/src/client/modules/plugins/narrativemanager/modules/narrativeManager.js#L414
        narr_id = int(round(time.time() * 1000))
        workspaceName = self.user_id + ':narrative_' + str(narr_id)
        narrativeName = "Narrative." + str(narr_id)

        ws = self.ws
        ws_info = ws.create_workspace({'workspace': workspaceName, 'description': ''})
        [narrativeObject, metadataExternal] = self._fetchNarrativeObjects(
            workspaceName, cells, parameters, includeIntroCell, title
        )
        is_temporary = 'true'
        if title is not None and title != 'Untitled':
            is_temporary = 'false'

        metadataExternal['is_temporary'] = is_temporary
        objectInfo = ws.save_objects({'workspace': workspaceName,
                                      'objects': [{'type': 'KBaseNarrative.Narrative',
                                                   'data': narrativeObject,
                                                   'name': narrativeName,
                                                   'meta': metadataExternal,
                                                   'provenance': [{'script': 'NarrativeManager.py',
                                                                   'description': 'Created new ' +
                                                                   'Workspace/Narrative bundle.'}],
                                                   'hidden': 0}]})[0]
        objectInfo = ServiceUtils.object_info_to_object(objectInfo)
        ws_info = self._completeNewNarrative(ws_info[0], objectInfo['id'],
                                             importData, is_temporary, title,
                                             len(narrativeObject['cells']))
        return {
            'workspaceInfo': ServiceUtils.workspace_info_to_object(ws_info),
            'narrativeInfo': objectInfo
        }

    def _fetchNarrativeObjects(self, workspaceName, cells, parameters, includeIntroCell, title):
        if not cells:
            cells = []
        if not title:
            title = 'Untitled'

        # fetchSpecs
        appSpecIds = []
        methodSpecIds = []
        specMapping = {'apps': {}, 'methods': {}}
        for cell in cells:
            if 'app' in cell:
                appSpecIds.append(cell['app'])
            elif 'method' in cell:
                methodSpecIds.append(cell['method'])
        nms = NarrativeMethodStore(self.narrativeMethodStoreURL)
        if len(appSpecIds) > 0:
            appSpecs = nms.get_app_spec({'ids': appSpecIds})
            for spec in appSpecs:
                spec_id = spec['info']['id']
                specMapping['apps'][spec_id] = spec
        if len(methodSpecIds) > 0:
            methodSpecs = nms.get_method_spec({'ids': methodSpecIds})
            for spec in methodSpecs:
                spec_id = spec['info']['id']
                specMapping['methods'][spec_id] = spec
        # end of fetchSpecs

        metadata = {'job_ids': {'methods': [],
                                'apps': [],
                                'job_usage': {'queue_time': 0, 'run_time': 0}},
                    'format': 'ipynb',
                    'creator': self.user_id,
                    'ws_name': workspaceName,
                    'name': title,
                    'type': 'KBaseNarrative.Narrative',
                    'description': '',
                    'data_dependencies': []}
        cellData = self._gatherCellData(cells, specMapping, parameters, includeIntroCell)
        narrativeObject = {'nbformat_minor': 0,
                           'cells': cellData,
                           'metadata': metadata,
                           'nbformat': 4}
        metadataExternal = {}
        for key in metadata:
            value = metadata[key]
            if isinstance(value, str):
                metadataExternal[key] = value
            else:
                metadataExternal[key] = json.dumps(value)
        return [narrativeObject, metadataExternal]

    def _gatherCellData(self, cells, specMapping, parameters, includeIntroCell):
        cell_data = []
        if includeIntroCell == 1:
            cell_data.append(
                self._get_intro_cell()
            )
        for cell_pos, cell in enumerate(cells):
            if 'app' in cell:
                cell_data.append(self._buildAppCell(len(cell_data),
                                                    specMapping['apps'][cell['app']],
                                                    parameters))
            elif 'method' in cell:
                cell_data.append(self._buildMethodCell(len(cell_data),
                                                       specMapping['methods'][cell['method']],
                                                       parameters))
            elif 'markdown' in cell:
                cell_data.append({'cell_type': 'markdown', 'source': cell['markdown'],
                                  'metadata': {}})
            else:
                raise ValueError("cannot add cell #" + str(cell_pos) +
                                 ", unrecognized cell content")
        return cell_data

    def _buildAppCell(self, pos, spec, params):
        cellId = 'kb-cell-' + str(pos) + '-' + str(uuid.uuid4())
        cell = {
            "cell_type": "markdown",
            "source": "<div id='" + cellId + "'></div>" +
                      "\n<script>" +
                      "$('#" + cellId + "').kbaseNarrativeAppCell({'appSpec' : '" +
                      self._safeJSONStringify(spec) + "', 'cellId' : '" + cellId + "'});" +
                      "</script>",
            "metadata": {}
        }
        cellInfo = {}
        widgetState = []
        cellInfo[self.KB_TYPE] = self.KB_APP_CELL
        cellInfo['app'] = spec
        if params:
            steps = {}
            for param in params:
                stepid = 'step_' + str(param[0])
                if stepid not in steps:
                    steps[stepid] = {}
                    steps[stepid]['inputState'] = {}
                steps[stepid]['inputState'][param[1]] = param[2]
            state = {'state': {'step': steps}}
            widgetState.append(state)
        cellInfo[self.KB_STATE] = widgetState
        cell['metadata'][self.KB_CELL] = cellInfo
        return cell

    def _buildMethodCell(self, pos, spec, params):
        cellId = "kb-cell-" + str(pos) + "-" + str(uuid.uuid4())
        cell = {"cell_type": "markdown",
                "source": "<div id='" + cellId + "'></div>" +
                          "\n<script>" +
                          "$('#" + cellId + "').kbaseNarrativeMethodCell({'method' : '" +
                          self._safeJSONStringify(spec) + "'});" +
                          "</script>",
                "metadata": {}}
        cellInfo = {"method": spec,
                    "widget": spec["widgets"]["input"]}
        cellInfo[self.KB_TYPE] = self.KB_FUNCTION_CELL
        widgetState = []
        if params:
            wparams = {}
            for param in params:
                wparams[param[1]] = param[2]
            widgetState.append({"state": wparams})
        cellInfo[self.KB_STATE] = widgetState
        cell["metadata"][self.KB_CELL] = cellInfo
        return cell

    def _completeNewNarrative(self, workspaceId, objectId, importData, is_temporary, title, num_cells):
        """
        'Completes' the new narrative by updating workspace metadata with the required fields and
        copying in data from the importData list of references.
        """
        new_meta = {
            'narrative': str(objectId),
            'is_temporary': is_temporary,
            'searchtags': 'narrative',
            'cell_count': str(num_cells)
        }
        if is_temporary == 'false' and title is not None:
            new_meta['narrative_nice_name'] = title

        self.ws.alter_workspace_metadata({'wsi': {'id': workspaceId},
                                          'new': new_meta})
        # copy_to_narrative:
        if importData:
            objectsToCopy = [{'ref': x} for x in importData]
            infoList = self.ws.get_object_info_new({'objects': objectsToCopy, 'includeMetadata': 0})
            for item in infoList:
                objectInfo = ServiceUtils.object_info_to_object(item)
                self.copy_object(objectInfo['ref'], workspaceId, None, None, objectInfo)

        return self.ws.get_workspace_info({'id': workspaceId})

    def _safeJSONStringify(self, obj):
        return json.dumps(self._safeJSONStringifyPrepare(obj))

    def _safeJSONStringifyPrepare(self, obj):
        if isinstance(obj, str):
            return obj.replace("'", "&apos;").replace('"', "&quot;")
        elif isinstance(obj, list):
            for pos in range(len(obj)):
                obj[pos] = self._safeJSONStringifyPrepare(obj[pos])
        elif isinstance(obj, dict):
            obj_keys = list(obj.keys())
            for key in obj_keys:
                obj[key] = self._safeJSONStringifyPrepare(obj[key])
        else:
            pass  # it's boolean/int/float/None
        return obj

    def copy_object(self, ref, target_ws_id, target_ws_name, target_name, src_info):
        """
        Copies an object from one workspace to another.
        """
        if not target_ws_id and not target_ws_name:
            raise ValueError("Neither target workspace id nor name is defined")
        if not src_info:
            src_info_tuple = self.ws.get_object_info_new({'objects': [{'ref': ref}],
                                                          'includeMetadata': 0})[0]
            src_info = ServiceUtils.object_info_to_object(src_info_tuple)
        if not target_name:
            target_name = src_info['name']
        obj_info_tuple = self.ws.copy_object({
            'from': {'ref': ref},
            'to': {
                'wsid': target_ws_id,
                'workspace': target_ws_name,
                'name': target_name
            }
        })
        obj_info = ServiceUtils.object_info_to_object(obj_info_tuple)
        return {'info': obj_info}

    def rename_narrative(self, narrative_ref: str, new_name: str, service_version: str) -> str:
        """
        Renames a Narrative.
        If the current user (as set by the auth token in self.ws) has admin permission on the workspace,
        then this does the following steps.
        1. Fetch the Narrative object and save it with the name change in the metadata.
        2. Update the workspace metadata so that it has the new name as the narrative nice name.
        3. Flips the workspace metadata so the the narrative is no longer temporary, if it was.

        :param narrative_ref: string, format = "###/###" or "###/###/###" (though the latter is very not recommended)
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
            raise ValueError(f"User {self.user_id} must have admin rights to change the name of the narrative in workspace {ws_id}")

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

        # 5. Save the Narrative object. Keep all the things intact, with new provenance saying we renamed with the NarrativeService.
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
