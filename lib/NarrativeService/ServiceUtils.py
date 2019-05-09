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
