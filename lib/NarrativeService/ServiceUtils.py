import dateutil.parser
import datetime
import re


class ServiceUtils:
    @staticmethod
    def workspace_info_to_object(wsInfo):
        return {'id': wsInfo[0],
                'name': wsInfo[1],
                'owner': wsInfo[2],
                'moddate': wsInfo[3],
                'object_count': wsInfo[4],
                'user_permission': wsInfo[5],
                'globalread': wsInfo[6],
                'lockstat': wsInfo[7],
                'metadata': wsInfo[8],
                'modDateMs': ServiceUtils.iso8601_to_millis_since_epoch(wsInfo[3])}

    @staticmethod
    def object_info_to_object(data):
        dtype = re.split("-|\.", data[2])
        return {'id': data[0],
                'name': data[1],
                'type': data[2],
                'save_date': data[3],
                'version': data[4],
                'saved_by': data[5],
                'wsid': data[6],
                'ws': data[7],
                'checksum': data[8],
                'size': data[9],
                'metadata': data[10],
                'ref': str(data[6]) + '/' + str(data[0]) + '/' + str(data[4]),
                'obj_id': 'ws.' + str(data[6]) + '.obj.' + str(data[0]),
                'typeModule': dtype[0],
                'typeName': dtype[1],
                'typeMajorVersion': dtype[2],
                'typeMinorVersion': dtype[3],
                'saveDateMs': ServiceUtils.iso8601_to_millis_since_epoch(data[3])}

    @staticmethod
    def iso8601_to_millis_since_epoch(date):
        epoch = datetime.datetime.utcfromtimestamp(0)
        dt = dateutil.parser.parse(date)
        utc_naive = dt.replace(tzinfo=None) - dt.utcoffset()
        return int((utc_naive - epoch).total_seconds() * 1000.0)

    @staticmethod
    def numerical_ref_to_dict(ref: str) -> dict:
        """
        Converts an object reference to a simple ref type dict
        TODO - make an actual Object Ref class and apply it throughout this module where
        appropriate.
        """
        ref_regex = "^(?P<ws>\\d+)\\/(?P<obj>\\d+)(\\/(?P<ver>\\d+))?$"
        m = re.match(ref_regex, ref)
        if not m:
            return {}
        return {
            "ws_id": m.group("ws"),
            "obj_id": m.group("obj"),
            "ver": m.group("ver")
        }

    @staticmethod
    def get_user_workspace_permissions(user_id: str, ws_id: int, ws_client) -> str:
        # a little complex shortcut.
        # get_permissions_mass returns {"perms": [{ws 1 perms}, {ws 2 perms}, ...]}
        # we just need the first.
        perms = ws_client.get_permissions_mass({"workspaces": [{"ref": ws_id}]}).get("perms", [{}])[0]
        return perms.get(user_id, "n")
