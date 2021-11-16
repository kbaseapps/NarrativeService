import time
import requests
import json

class SearchServiceClient:

    def __init__(self, url, token=None):
        self.url = url
        self.token = token

    def search_workspace_by_id(self, ws_id, obj_id, version=None):

        """
            a method used currently to check on whether a specific version has been successfully indexed 
            in search_api2. Returns 1 instance of search doc if found, None if no matches were found. workspace
            and object ID are required; version number is optional.
        """

        headers = {'Authorization': self.token}

        params = {
            "filters": {
                "operator": "AND",
                "fields": [
                    {"field": "access_group", "term": ws_id},
                    {"field": "obj_id", "term": obj_id}
                ]
            },
            "paging": {
                "length": 1,
                "offset": 0
            },
            "types": ["KBaseNarrative.Narrative"]
        }

        if version is not None:
            params["filters"]["fields"].append({"field": "version", "term": version})

        body = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "search_workspace",
            "params": params
        }
    
        data = requests.post(self.url, data=json.dumps(body), headers=headers).json()

        return data['result']['hits'][0] if data['result']['count'] > 0 else None

        