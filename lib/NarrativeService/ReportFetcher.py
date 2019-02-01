from NarrativeService.ServiceUtils import ServiceUtils

class ReportFetcher(object):
    def __init__(self, ws_client):
        self.ws_client = ws_client

    def find_report_from_object(self, upa):
        #TODO:
        # 1. make sure upa's real.

        # first, fetch object references (without data)
        ref_list = self.ws_client.list_referencing_objects([{"ref": upa}])[0]
        # scan it for a report.
        # if we find at least one, return them
        # if we find 0, test if it's a copy, and search upstream.
        if len(ref_list):
            report_upas = list()
            for ref_info in ref_list:
                if "KBaseReport.Report" in ref_info[2]:
                    report_upas.append(ServiceUtils.objectInfoToObject(ref_info)['ref'])
            if len(report_upas):
                return self.build_output(upa, report_upas)
            else:
                return self.find_report_from_copy_source(upa)
        else:
            return self.find_report_from_copy_source(upa)

    def find_report_from_copy_source(self, upa):
        """
        Fetch the info about this object. If it's a copy, run find_report_from_object on its source.
        If it's not, return an error state, or just an empty list for the upas.
        """
        obj_data = self.ws_client.get_objects2({'objects': [{'ref': upa}], 'no_data': 1})['data'][0]
        if obj_data.get('copy_source_inaccessible', 0) == 1:
            err = "No report found. This object is a copy, and its source is inaccessible."
            return self.build_output(upa, [], inaccessible=1, error=err)
        elif 'copied' in obj_data:
            return self.find_report_from_object(obj_data['copied'])
        return self.build_output(upa, [])

    def build_output(self, upa, report_upas=[], inaccessible=0, error=None):
        retVal = {
            "report_upas": report_upas,
            "object_upa": upa
        }
        if inaccessible != 0:
            retVal["inaccessible"] = inaccessible
        if error is not None:
            retVal["error"] = error
        return retVal
