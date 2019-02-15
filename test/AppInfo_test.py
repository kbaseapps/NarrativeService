import unittest
from NarrativeService.apps.appinfo import get_all_app_info
import os
from configparser import ConfigParser
from installed_clients.authclient import KBaseAuth as _KBaseAuth
from NarrativeService.NarrativeServiceImpl import NarrativeService
from NarrativeService.NarrativeServiceServer import MethodContext

class AppInfoTestCase(unittest.TestCase):
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
        cls.user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': cls.user_id,
                        'provenance': [
                            {'service': 'NarrativeService',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.nmsURL = cls.cfg['narrative-method-store']
        cls.catalogURL = cls.cfg['catalog-url']
        cls.wsURL = cls.cfg['workspace-url']
        cls.serviceImpl = NarrativeService(cls.cfg)

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_get_all_app_info_unit_ok(self):
        tags = ['release', 'beta', 'dev']
        for t in tags:
            info = get_all_app_info(t, self.user_id, self.nmsURL, self.catalogURL)
            self._validate_app_info(info)

    def test_get_all_app_info_impl_ok(self):
        impl = self.getImpl()
        ctx = self.getContext()
        tags = ['release', 'beta', 'dev']
        for t in tags:
            info = impl.get_all_app_info(ctx, {
                'tag': t,
                'user': self.user_id
            })[0]
            self._validate_app_info(info)

    def _validate_app_info(self, info):
        self.assertIn('module_versions', info)
        self.assertIn('categories', info)
        self.assertIn('app_infos', info)
        for m in info['module_versions']:
            self.assertIsNotNone(info['module_versions'][m])
        for c in info['categories']:
            category = info['categories'][c]
            self.assertIsNotNone(category)
            self.assertIn('description', category)
            self.assertIn('id', category)
            self.assertIn('name', category)
            self.assertIn('parent_ids', category)
            self.assertIn('tooltip', category)
            self.assertIn('ver', category)
        for a in info['app_infos']:
            app = info['app_infos'][a]['info']
            self.assertIn('app_type', app)
            self.assertIn('authors', app)
            self.assertIsInstance(app['authors'], list)
            self.assertIn('categories', app)
            self.assertIsInstance(app['categories'], list)
            self.assertIn('id', app)
            self.assertIn('input_types', app)
            self.assertIsInstance(app['input_types'], list)
            self.assertIn('name', app)
            self.assertIn('namespace', app)
            self.assertIn('output_types', app)
            self.assertIsInstance(app['output_types'], list)
            self.assertIn('subtitle', app)
            self.assertIn('tooltip', app)
            self.assertIn('ver', app)
