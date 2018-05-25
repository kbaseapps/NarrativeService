import unittest
import os
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

class ReportFetcherTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('NarrativeService'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
                "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'NarrativeService',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL, token=token)
        cls.serviceImpl = NarrativeService(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        pass

    def getWsClient(self):
        return self.__class__.wsClient

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_fetch_report_ok(self):
        upa = "32806/4/1"
        report_upa = "32806/5/1"
        ret = self.getImpl().find_object_report(self.getContext(), {"upa": upa})
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 1)
        self.assertEqual(report_upa, ret["report_upas"][0])
        self.assertIn("object_upa", ret)
        self.assertEqual(upa, ret["object_upa"])
        self.assertNotIn("copy_inaccessible", ret)
        self.assertNotIn("error", ret)

    def test_fetch_report_copy(self):
        upa = "32806/6/1"
        source_upa = "32806/4/1"
        ret = self.getImpl().find_object_report(self.getContext(), {"upa": upa})
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 1)
        self.assertEqual(report_upa, ret["report_upas"][0])
        self.assertIn("object_upa", ret)
        self.assertEqual(source_upa, ret["object_upa"])
        self.assertNotIn("copy_inaccessible", ret)
        self.assertNotIn("error", ret)

    def test_fetch_report_copy_inaccessible(self):
        pass

    def test_fetch_report_none(self):
        upa = "32806/5/1"
        ret = self.getImpl().find_object_report(self.getContext(), {"upa": upa})
        self.assertIn("report_upas", ret)
        self.assertEqual(len(ret["report_upas"]), 0)
        self.assertNotIn("copy_inaccessible", ret)
        self.assertNotIn("error", ret)
