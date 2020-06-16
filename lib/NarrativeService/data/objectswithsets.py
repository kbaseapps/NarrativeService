from ..WorkspaceListObjectsIterator import WorkspaceListObjectsIterator


class ObjectsWithSets:
    def __init__(self, set_api_client, data_palette_client, workspace_client):
        self.set_api_client = set_api_client
        self.data_palette_client = data_palette_client
        self.workspace_client = workspace_client

    def list_objects_with_sets(self, ws_id: int = None, ws_name: str = None, workspaces: list = None,
                               types: list = None, include_metadata: int = 0,
                               include_data_palettes: int = 0):
        if not workspaces:
            if not ws_id and not ws_name:
                raise ValueError("One and only one of 'ws_id', 'ws_name', 'workspaces' "
                                 "parameters should be set")
            ws_ident = ws_name
            if not ws_ident:
                ws_ident = ws_id
            workspaces = [ws_ident]
        return self._list_objects_with_sets(workspaces, types, include_metadata, include_data_palettes)

    def _check_info_type(self, info, type_map):
        if type_map is None:
            return True
        obj_type = info[2].split('-')[0]
        return type_map.get(obj_type, False)

    def _list_objects_with_sets(self, workspaces, types, include_metadata, include_data_palettes):
        type_map = None
        if types is not None:
            type_map = {key: True for key in types}

        processed_refs = {}
        data = []
        set_ret = self.set_api_client.call_method(
            "list_sets",
            [{
                "workspaces": workspaces,
                "include_set_item_info": 1,
                "include_metadata": include_metadata
            }]
        )
        sets = set_ret["sets"]
        for set_info in sets:
            # Process
            target_set_items = []
            for set_item in set_info["items"]:
                target_set_items.append(set_item["info"])
            if self._check_info_type(set_info["info"], type_map):
                data_item = {
                    "object_info": set_info["info"],
                    "set_items": {"set_items_info": target_set_items}}
                data.append(data_item)
                processed_refs[set_info["ref"]] = data_item

        ws_info_list = []
        # for ws in workspaces:
        if len(workspaces) == 1:
            ws = workspaces[0]
            ws_id = None
            ws_name = None
            if str(ws).isdigit():
                ws_id = int(ws)
            else:
                ws_name = str(ws)
            ws_info_list.append(self.workspace_client.get_workspace_info({"id": ws_id, "workspace": ws_name}))
        else:
            ws_map = {key: True for key in workspaces}
            for ws_info in self.workspace_client.list_workspace_info({'perm': 'r'}):
                if ws_info[1] in ws_map or str(ws_info[0]) in ws_map:
                    ws_info_list.append(ws_info)

        for info in WorkspaceListObjectsIterator(self.workspace_client,
                                                 ws_info_list=ws_info_list,
                                                 list_objects_params={
                                                     "includeMetadata": include_metadata
                                                 }):
            item_ref = str(info[6]) + '/' + str(info[0]) + '/' + str(info[4])
            if item_ref not in processed_refs and self._check_info_type(info, type_map):
                data_item = {"object_info": info}
                data.append(data_item)
                processed_refs[item_ref] = data_item

        return_data = {
            "data": data
        }

        if include_data_palettes == 1:
            dp_ret = self.data_palette_client.call_method(
                "list_data",
                [{'workspaces': workspaces, 'include_metadata': include_metadata}]
            )
            for item in dp_ret['data']:
                ref = item['ref']
                if self._check_info_type(item['info'], type_map):
                    data_item = None
                    if ref in processed_refs:
                        data_item = processed_refs[ref]
                    else:
                        data_item = {'object_info': item['info']}
                        processed_refs[ref] = data_item
                        data.append(data_item)
                    dp_info = {}
                    if 'dp_ref' in item:
                        dp_info['ref'] = item['dp_ref']
                    if 'dp_refs' in item:
                        dp_info['refs'] = item['dp_refs']
                    data_item['dp_info'] = dp_info
            return_data["data_palette_refs"] = dp_ret['data_palette_refs']

        return return_data

    def list_available_types(self, workspaces):
        data = self.list_objects_with_sets(workspaces=workspaces)['data']
        type_stat = {}
        for item in data:
            info = item['object_info']
            obj_type = info[2].split('-')[0]
            if obj_type in type_stat:
                type_stat[obj_type] += 1
            else:
                type_stat[obj_type] = 1
        return {'type_stat': type_stat}
