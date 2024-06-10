from NarrativeService.reportfetcher import ReportFetcher

REPORT_OBJ_INFO = [
    2,
    "some_report",
    "KBaseReport.Report-1.0",
    "2024-05-30T15:22:20+0000",
    1,
    "some-user",
    123,
    "some_workspace",
    123,
    123,
    None
]

def test_fetch_report_ok(mocker):
    mock_ws = mocker.MagicMock()
    mock_ws.list_referencing_objects.return_value = [[REPORT_OBJ_INFO]]
    rf = ReportFetcher(mock_ws)
    result = rf.find_report_from_object("123/1/1")
    assert result == {
        "report_upas": ["123/2/1"],
        "object_upa": "123/1/1"
    }

def test_fetch_report_from_copy(mocker):
    def list_ref_objects_effect(ref_list):
        if ref_list[0]["ref"] == "123/5/1":
            return [[REPORT_OBJ_INFO]]
        return [[[]]]

    mock_ws = mocker.MagicMock()
    mock_ws.list_referencing_objects.side_effect = list_ref_objects_effect
    mock_ws.get_objects2.return_value = { "data": [{"copied": "123/5/1"}] }

    rf = ReportFetcher(mock_ws)
    result = rf.find_report_from_object("123/1/1")
    assert result == {
        "report_upas": ["123/2/1"],
        "object_upa": "123/5/1"
    }

def test_fetch_report_none(mocker):
    mock_ws = mocker.MagicMock()
    mock_ws.list_referencing_objects.return_value = [[[]]]
    mock_ws.get_objects2.return_value = { "data": [{}] }
    rf = ReportFetcher(mock_ws)
    assert rf.find_report_from_object("123/1/1") == {
        "report_upas": [],
        "object_upa": "123/1/1"
    }

def test_fetch_report_copy_inaccessible(mocker):
    mock_ws = mocker.MagicMock()
    mock_ws.list_referencing_objects.return_value = [[[]]]
    mock_ws.get_objects2.return_value = { "data": [{"copy_source_inaccessible": 1}] }
    rf = ReportFetcher(mock_ws)
    assert rf.find_report_from_object("123/1/1") == {
        "report_upas": [],
        "object_upa": "123/1/1",
        "inaccessible": 1,
        "error": "No report found. This object is a copy, and its source is inaccessible."
    }
