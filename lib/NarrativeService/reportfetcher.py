from NarrativeService.ServiceUtils import ServiceUtils

from lib.installed_clients.WorkspaceClient import Workspace

REPORT_TYPE: str = "KBaseReport.Report"
class ReportFetcher:
    def __init__(self, ws_client: Workspace) -> None:
        self.ws_client = ws_client

    def find_report_from_object(self, upa: str) -> dict[str, list|str]:
        """
        Given the UPA of an object, this attempts to find any reports that it references.
        If the object doesn't have any referencing reports, but it was a copy of another
        object, this tries to find the copy's reports.
        """
        # TODO: make sure upa's real.

        # first, fetch object references (without data)
        ref_list = self.ws_client.list_referencing_objects([{"ref": upa}])[0]
        # scan it for a report.
        # if we find at least one, return them
        # if we find 0, test if it's a copy, and search upstream.
        report_upas = [
            ServiceUtils.object_info_to_object(ref_info)["ref"]
            for ref_info in ref_list
            if len(ref_info) and REPORT_TYPE in ref_info[2]
        ]
        if len(report_upas):
            return self.build_output(upa, report_upas)
        return self.find_report_from_copy_source(upa)

    def find_report_from_copy_source(self, upa: str) -> dict[str, list|str]:
        """
        Fetch the info about this object. If it's a copy, run find_report_from_object on its source.
        If it's not, return an error state, or just an empty list for the upas.
        """
        obj_data = self.ws_client.get_objects2({"objects": [{"ref": upa}], "no_data": 1})["data"][0]
        if obj_data.get("copy_source_inaccessible", 0) == 1:
            err = "No report found. This object is a copy, and its source is inaccessible."
            return self.build_output(upa, [], inaccessible=1, error=err)
        if "copied" in obj_data:
            return self.find_report_from_object(obj_data["copied"])
        return self.build_output(upa, [])

    def build_output(
        self,
        upa: str,
        report_upas: list[str] | None=None,
        inaccessible: int=0,
        error: str | None=None
    ) -> dict[str, list|str|int]:
        """
        Builds the output dictionary for the report fetching.
        Definitely has keys:
        report_upas - list[str] - list of report object UPAs, if they exist
        object_upa - str - the UPA of the object referencing the reports.
        Might have keys:
        inaccessible - int (1) if the given object in object_upa was copied, and its source
            (which might reference reports) is inaccessible
        error - str - if an error occurred.
        """
        if report_upas is None:
            report_upas = []
        ret_val = {
            "report_upas": report_upas,
            "object_upa": upa
        }
        if inaccessible != 0:
            ret_val["inaccessible"] = inaccessible
        if error is not None:
            ret_val["error"] = error
        return ret_val
