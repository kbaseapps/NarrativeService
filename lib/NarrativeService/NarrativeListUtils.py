import pylru

# For reference:
#   workspace_info:
#     0 ws_id id
#     1 ws_name workspace
#     2 username owner
#     3 timestamp moddate
#     4 int max_objid
#     5 permission user_permission
#     6 permission globalread
#     7 lock_status lockstat
#     8 usermeta metadata


class NarrativeInfoCache(object):

    def __init__(self, cache_size):
        self.cache = pylru.lrucache(int(cache_size))

    def clear_cache(self):
        self.cache.clear()

    def check_cache_size(self):
        return len(self.cache)

    def get_info_list(self, ws_lookup_table, wsClient):
        '''
            Given a set of WS info, lookup the corresponding Narrative
            information.

            input:
                ws_lookup_table = dict of ws_id -> workspace_info
            output:
                [{
                    'ws': workspace_info,
                    'nar': narrative_info
                 },
                 ...
                 ]
        '''
        # search the cache and extract what we have, mark what was missed
        res = self._search_cache(ws_lookup_table)
        items = res['items']
        missed_items = res['missed']

        # for objects that were missed, we have to go out and fetch that
        # narrative object info
        all_items = items
        if len(missed_items) > 0:
            more_items = self._fetch_objects_and_cache(missed_items, ws_lookup_table, wsClient)
            all_items += more_items

        return all_items

    def _search_cache(self, ws_lookup_table):
        items = []  # =[{'ws': [...], 'nar': [...]}, ...]
        missed = []  # =[ws_info1, ws_info2, ... ]
        for ws_info in ws_lookup_table.values():
            key = self._get_cache_key(ws_info)
            if key in self.cache:
                items.append({'ws': ws_info, 'nar': self.cache[key]})
            else:
                missed.append(ws_info)
        return {'items': items, 'missed': missed}

    def _fetch_objects_and_cache(self, ws_list, full_ws_lookup_table, wsClient):
        ''' Fetches narrative objects (if possible) for everything in ws_list '''
        obj_ref_list = []
        for ws_info in ws_list:
            if 'narrative' not in ws_info[8]:
                continue
            if not ws_info[8]['narrative'].isdigit() or not int(ws_info[8]['narrative']) > 0:
                continue
            ref = str(ws_info[0]) + '/' + str(ws_info[8]['narrative'])
            obj_ref_list.append({'ref': ref})

        if len(obj_ref_list) == 0:
            return []

        # ignore errors
        get_obj_params = {'objects': obj_ref_list, 'includeMetadata': 1, 'ignoreErrors': 1}
        narrative_list = wsClient.get_object_info3(get_obj_params)['infos']

        items = []
        for nar in narrative_list:
            if nar:
                ws_info = full_ws_lookup_table[nar[6]]
                items.append({'ws': ws_info, 'nar': nar})
                self.cache[self._get_cache_key(ws_info)] = nar
        return items

    def _get_cache_key(self, ws_info):
        return str(ws_info[0]) + '__' + str(ws_info[3])



class NarrativeListUtils(object):

    def __init__(self, cache_size):
        self.narrativeInfo = NarrativeInfoCache(cache_size)


    def list_public_narratives(self, wsClient):
        # get all the workspaces marked as narratorials
        ws_list = wsClient.list_workspace_info({})
        ws_global_list = []
        for ws_info in ws_list:
            if ws_info[6] == 'r':  # indicates that this ws is globally readable
                ws_global_list.append(ws_info)
        # build a ws_list lookup table
        ws_lookup_table = self._build_ws_lookup_table(ws_global_list)
        # based on the WS lookup table, lookup the narratives
        return self.narrativeInfo.get_info_list(ws_lookup_table, wsClient)


    def list_my_narratives(self, my_user_id, wsClient):
        # get all the workspaces marked as narratorials
        ws_list = wsClient.list_workspace_info({'owners': [my_user_id]})
        # build a ws_list lookup table
        ws_lookup_table = self._build_ws_lookup_table(ws_list)
        # based on the WS lookup table, lookup the narratives
        return self.narrativeInfo.get_info_list(ws_lookup_table, wsClient)


    def list_shared_narratives(self, my_user_id, wsClient):
        # get all the workspaces marked as narratorials
        ws_list = wsClient.list_workspace_info({})
        ws_shared_list = []
        for ws_info in ws_list:
            if ws_info[2] == my_user_id:
                continue
            if ws_info[5] == 'n':  # indicates that this ws is globally readable
                continue
            ws_shared_list.append(ws_info)
        # build a ws_list lookup table
        ws_lookup_table = self._build_ws_lookup_table(ws_shared_list)
        # based on the WS lookup table, lookup the narratives
        return self.narrativeInfo.get_info_list(ws_lookup_table, wsClient)


    def list_narratorials(self, wsClient):
        # get all the workspaces marked as narratorials
        ws_list = wsClient.list_workspace_info({'meta': {'narratorial': '1'}})
        # build a ws_list lookup table
        ws_lookup_table = self._build_ws_lookup_table(ws_list)
        # based on the WS lookup table, lookup the narratives
        return self.narrativeInfo.get_info_list(ws_lookup_table, wsClient)


    def _build_ws_lookup_table(self, ws_list):
        ''' builds a lookup table, skips anything without a 'narrative' metadata field set '''
        ws_lookup_table = {}
        for ws_info in ws_list:
            if 'narrative' in ws_info[8]:
                if ws_info[8]['narrative'].isdigit() and int(ws_info[8]['narrative']) > 0:
                    ws_lookup_table[ws_info[0]] = ws_info
        return ws_lookup_table


class NarratorialUtils(object):

    def __init__(self):
        pass

    def _get_workspace_identity(self, wsid):
        if str(wsid).isdigit():
            return {'id': int(wsid)}
        else:
            return {'workspace': str(wsid)}

    def set_narratorial(self, wsid, description, wsClient):
        wsi = self._get_workspace_identity(wsid)
        wsClient.alter_workspace_metadata({'wsi': wsi, 'new': {'narratorial': '1'}})
        wsClient.alter_workspace_metadata({'wsi': wsi, 'new': {'narratorial_description': description}})

    def remove_narratorial(self, wsid, wsClient):
        wsi = self._get_workspace_identity(wsid)
        wsClient.alter_workspace_metadata({'wsi': wsi, 'remove': ['narratorial', 'narratorial_description']})
