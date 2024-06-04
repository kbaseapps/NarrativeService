import os
import time
import unittest
from configparser import ConfigParser

from installed_clients.authclient import KBaseAuth as _KBaseAuth
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from NarrativeService.NarrativeServiceImpl import NarrativeService
from NarrativeService.NarrativeServiceServer import MethodContext


class ReportFetcherTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get("KB_AUTH_TOKEN", None)
        config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items("NarrativeService"):
            cls.cfg[nameval[0]] = nameval[1]
        auth_service_url = cls.cfg.get(
            "auth-service-url",
            "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(auth_service_url)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({"token": token,
                        "user_id": user_id,
                        "provenance": [
                            {"service": "NarrativeService",
                             "method": "please_never_use_it_in_production",
                             "method_params": []
                             }],
                        "authenticated": 1})
        # Set up test Workspace
        cls.ws_url = cls.cfg["workspace-url"]
        cls.ws_client = Workspace(cls.ws_url, token=token)
        cls.test_ws_info = cls.make_workspace()
        cls.test_ws_name = cls.test_ws_info[1]
        # Build test data stuff.
        # 1. Make a fake reads object - test for report (should be null)
        cls.fake_reads_upa = cls.make_fake_reads(cls.test_ws_name, "FakeReads")

        # 2. Make a report, give it that reads object - test for report, should find it
        cls.fake_report_upa = cls.make_fake_report(cls.fake_reads_upa, cls.test_ws_name)

        cls.service_impl = NarrativeService(cls.cfg)

    @classmethod
    def make_workspace(cls):
        """
        make a workspace
        return ws info
        """
        suffix = int(time.time() * 1000)
        ws_name = "test_NarrativeService_" + str(suffix)
        return cls.ws_client.create_workspace({"workspace": ws_name})

    @classmethod
    def make_fake_report(cls, ref_obj, ws_name):
        """
        Make a dummy report, referring to ref_obj, returns report ref
        """
        report_params = {
            "message": "dummy report for testing",
            "objects_created": [{
                "ref": ref_obj,
                "description": "dummy reads lib"
            }],
            "report_object_name": "NarrativeServiceTest_report_" + str(int(time.time() * 1000)),
            "workspace_name": ws_name
        }
        kr = KBaseReport(os.environ["SDK_CALLBACK_URL"])
        report_output = kr.create_extended_report(report_params)
        return report_output["ref"]

    @classmethod
    def make_fake_reads(cls, ws_name, reads_name):
        """
        Make fake reads in the workspace with the given name.
        Return the UPA for those reads.
        """
        foft = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"])
        info = foft.create_fake_reads({
            "ws_name": ws_name,
            "obj_names": [reads_name]})[0]
        return f"{info[6]}/{info[0]}/{info[4]}"

    def get_ws_client(self):
        return self.__class__.ws_client

    def get_impl(self):
        return self.__class__.service_impl

    def get_context(self):
        return self.__class__.ctx

    def test_fetch_report_ok(self):
        ret = self.get_impl().find_object_report(self.get_context(), {"upa": self.fake_reads_upa})[0]
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 1)
        self.assertEqual(self.fake_report_upa, ret["report_upas"][0])
        self.assertIn("object_upa", ret)
        self.assertEqual(self.fake_reads_upa, ret["object_upa"])
        self.assertNotIn("copy_inaccessible", ret)
        self.assertNotIn("error", ret)

    def test_fetch_report_copy(self):
        copy_info = self.ws_client.copy_object({
            "from": {
                "ref": self.fake_reads_upa
            },
            "to": {
                "workspace": self.test_ws_name,
                "name": "FakeReadsCopy"
            }
        })
        upa = f"{copy_info[6]}/{copy_info[0]}/{copy_info[4]}"
        source_upa = self.fake_reads_upa
        ret = self.get_impl().find_object_report(self.get_context(), {"upa": upa})[0]
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 1)
        self.assertEqual(self.fake_report_upa, ret["report_upas"][0])
        self.assertIn("object_upa", ret)
        self.assertEqual(source_upa, ret["object_upa"])
        self.assertNotIn("copy_inaccessible", ret)
        self.assertNotIn("error", ret)

    def test_fetch_report_copy_inaccessible(self):
        # Make a new workspace copy new reads to older WS, delete new WS - test for report, should fail and error.
        new_ws_info = self.__class__.make_workspace()
        # Make reads
        new_reads_upa = self.__class__.make_fake_reads(new_ws_info[1], "NewFakeReads")
        # Make report to new reads
        self.__class__.make_fake_report(new_reads_upa, new_ws_info[1])
        # Copy new reads to old WS
        copy_info = self.ws_client.copy_object({
            "from": {
                "ref": new_reads_upa
            },
            "to": {
                "workspace": self.test_ws_name,
                "name": "NewFakeReadsCopy"
            }
        })
        new_reads_copy_upa = f"{copy_info[6]}/{copy_info[0]}/{copy_info[4]}"
        # delete new WS
        self.ws_client.delete_workspace({"id": new_ws_info[0]})
        # now test for report and find the error
        ret = self.get_impl().find_object_report(self.get_context(), {"upa": new_reads_copy_upa})[0]
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 0)
        self.assertIn("object_upa", ret)
        self.assertEqual(new_reads_copy_upa, ret["object_upa"])
        self.assertIn("inaccessible", ret)
        self.assertIn("error", ret)

    def test_fetch_report_none(self):
        upa = self.fake_report_upa  # just use the report as an upa. it doesn't have a report, right?
        ret = self.get_impl().find_object_report(self.get_context(), {"upa": upa})[0]
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 0)
        self.assertNotIn("copy_inaccessible", ret)
        self.assertNotIn("error", ret)
