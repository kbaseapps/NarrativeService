import os
import time

import pytest
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from NarrativeService.NarrativeServiceImpl import NarrativeService


@pytest.fixture(scope="module")
def fake_reads(workspace: list[any], fake_obj_for_tests_client: FakeObjectsForTests):
    """Make a fake reads object and return the UPA for it."""
    reads_name = f"some_fake_reads_{int(time.time()*1000)}"
    info = fake_obj_for_tests_client.create_fake_reads({
        "ws_name": workspace[1],
        "obj_names": [reads_name]
    })[0]
    return f"{info[6]}/{info[0]}/{info[4]}"

@pytest.fixture(scope="module")
def fake_report(workspace: list[any], fake_reads: str) -> tuple[str, str]:
    """Makes a dummy report and a fake reads object to link to it. Return both the
    report UPA and reads UPA."""
    report_params = {
        "message": "dummy report for testing",
        "objects_created": [{
            "ref": fake_reads,
            "description": "dummy reads lib"
        }],
        "report_object_name": f"NarrativeServiceTest_report_{int(time.time() * 1000)}",
        "workspace_name": workspace[1]
    }
    kr = KBaseReport(os.environ["SDK_CALLBACK_URL"])
    report_output = kr.create_extended_report(report_params)
    return (report_output["ref"], fake_reads)


def test_fetch_report_ok(
    context: dict[str, any],
    service_impl: NarrativeService,
    fake_report: str
) -> None:
    report_upa, reads_upa = fake_report
    ret = service_impl.find_object_report(context, {"upa": reads_upa})[0]
    assert "report_upas" in ret
    assert len(ret["report_upas"]) == 1
    assert report_upa == ret["report_upas"][0]
    assert "object_upa" in ret
    assert reads_upa == ret["object_upa"]
    assert "copy_inaccessible" not in ret
    assert "error" not in ret


def test_fetch_report_copy(
    context: dict[str, any],
    service_impl: NarrativeService,
    fake_report: str,
    workspace: list[any],
    workspace_client: Workspace
) -> None:
    report_upa, reads_upa = fake_report
    copy_info = workspace_client.copy_object({
        "from": {
            "ref": reads_upa
        },
        "to": {
            "wsid": workspace[0],
            "name": "copied_reads"
        }
    })
    copy_upa = f"{copy_info[6]}/{copy_info[0]}/{copy_info[4]}"
    ret = service_impl.find_object_report(context, {"upa": copy_upa})[0]
    assert "report_upas" in ret
    assert len(ret["report_upas"]) == 1
    assert report_upa == ret["report_upas"][0]
    assert "object_upa" in ret
    assert reads_upa == ret["object_upa"]
    assert "copy_inaccessible" not in ret
    assert "error" not in ret


def test_fetch_report_copy_inaccessible(
    context: dict[str, any],
    service_impl: NarrativeService,
    workspace: list[any],
    workspace_client: Workspace,
    fake_reads: str
) -> None:
    """Test that the report fetcher fails properly when the object is visible, but the report
    is in an inaccessible workspace.
    Steps to do here:
    0. Given: existing workspace (see fixtures)
    1. Make a new workspace
    2. Make a new reads object
    3. Make a report attached to the reads
    4. Copy reads to old workspace
    5. Delete the new workspace
    6. Try to access the report from the copied reads.
    7. Cleanup: delete the copied reads
    """
    # steps to make a report fetch throw an error
    # Look for a report from a reads object, but the report is in an inaccessible workspace
    #
    # 1. new ws
    new_ws = workspace_client.create_workspace({"name": f"new_fake_ws_{int(time.time()*1000)}"})
    # 2. new reads
    new_reads_upa = fake_reads
    # 3. new report with those reads in the new ws
    report_params = {
        "message": "dummy report for testing",
        "objects_created": [{
            "ref": new_reads_upa,
            "description": "dummy reads lib"
        }],
        "report_object_name": f"NarrativeServiceTest_report_{int(time.time() * 1000)}",
        "workspace_name": new_ws[1]
    }
    kr = KBaseReport(os.environ["SDK_CALLBACK_URL"])
    kr.create_extended_report(report_params)
    # 4. copy the reads to the old (fixture'd) workspace
    copy_info = workspace_client.copy_object({
        "from": {
            "ref": new_reads_upa
        },
        "to": {
            "wsid": workspace[0],
            "name": "reads_copy_report_inaccessible"
        }
    })
    reads_copy_upa = f"{copy_info[6]}/{copy_info[0]}/{copy_info[4]}"
    # 5. delete the new workspace
    workspace_client.delete_workspace({"id": new_ws[0]})
    # 6. Try to get the report.
    ret = service_impl(context, {"upa": reads_copy_upa})[0]
    for key in ["report_upas", "object_upa", "inaccessible", "error"]:
        assert key in ret
    assert len(ret["report_upas"]) == 0
    assert reads_copy_upa == ret["object_upa"]


def test_fetch_report_none(
    context: dict[str, any],
    service_impl: NarrativeService,
    fake_report: str
) -> None:
    upa = fake_report[0]  # just use the report as an upa. it doesn't have a report, right?
    ret = service_impl.find_object_report(context, {"upa": upa})[0]
    assert "report_upas" in ret
    assert len(ret["report_upas"]) == 0
    assert "copy_inaccessible" not in ret
    assert "error" not in ret
