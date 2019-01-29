# -*- coding: utf-8 -*-
import time
import unittest
from configparser import ConfigParser
from os import environ
from pprint import pprint

from NarrativeService.NarrativeListUtils import NarrativeInfoCache, NarratorialUtils, \
    NarrativeListUtils
from NarrativeService.NarrativeServiceImpl import NarrativeService
from NarrativeService.NarrativeServiceServer import MethodContext
from installed_clients.WorkspaceClient import Workspace
from installed_clients.authclient import KBaseAuth as _KBaseAuth


class NarrativeListUtilsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
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

    def test_narrative_info_cache(self):

        ws_list = self.wsClient.list_workspace_info({})

        ws_lookup_table = {}
        for ws_info in ws_list:
            if 'narrative' in ws_info[8]:
                ws_lookup_table[ws_info[0]] = ws_info

        nic = NarrativeInfoCache(5000)
        self.assertEqual(nic.check_cache_size(), 0)
        t1 = time.time()
        nic.get_info_list(ws_lookup_table, self.wsClient)
        t2 = time.time()
        t3 = time.time()
        nic.get_info_list(ws_lookup_table, self.wsClient)
        t4 = time.time()
        self.assertTrue(nic.check_cache_size() > 0)
        pprint(nic.clear_cache())
        self.assertEqual(nic.check_cache_size(), 0)

        wsName = "test_NarrativeService_CacheTest_" + str(int(time.time() * 1000))
        ws_info = self.wsClient.create_workspace({'workspace': wsName})
        ws_lookup_table[ws_info[0]] = ws_info
        t5 = time.time()
        nic.get_info_list(ws_lookup_table, self.wsClient)
        t6 = time.time()

        # cached access should always be significantly faster, if not we have a problem
        print('Empty cache call took  %0.3f ms' % ((t2 - t1) * 1000.0))
        print('Fully cached call took %0.3f ms' % ((t4 - t3) * 1000.0))
        print('One cache miss call took  %0.3f ms' % ((t6 - t5) * 1000.0))
        self.assertTrue((t2 - t1) > (t4 - t3))


    def test_narratorial_utils_and_listing(self):

        suffix = int(time.time() * 1000)
        wsName = "test_NarrativeService_Narratorial_" + str(suffix)
        ws_info = self.wsClient.create_workspace({'workspace': wsName})
        wsid = ws_info[0]

        nu = NarratorialUtils()
        nu.set_narratorial(wsid, 'some narratorial', self.wsClient)
        nar_info = self.wsClient.save_objects({'workspace': wsName,
                                               'objects': [{'type': 'KBaseNarrative.Narrative',
                                                            'data': {'nbformat_minor': 0,
                                                                     'cells': [],
                                                                     'metadata': {'description': '',
                                                                                  'data_dependencies': []},
                                                                     'nbformat': 4},
                                                            'name': 'narrrrr',
                                                            'provenance': []}]})[0]
        self.wsClient.alter_workspace_metadata({'wsi': {'id': wsid}, 'new': {'narrative': nar_info[0]}})

        nlu = NarrativeListUtils(5000)
        narratorial_list = nlu.list_narratorials(self.wsClient)
        self.assertTrue(len(narratorial_list) > 0)
        found = False
        for nt in narratorial_list:
            self.assertIn('ws', nt)
            self.assertIn('nar', nt)
            self.assertIn('narratorial', nt['ws'][8])
            self.assertIn('narratorial_description', nt['ws'][8])
            self.assertTrue(int(nt['ws'][8]['narrative']), nt['nar'][0])
            if wsid == nt['ws'][0]:
                found = True
                self.assertEqual('some narratorial', nt['ws'][8]['narratorial_description'])

        self.assertTrue(found)

        # remove the narratorial, make sure it doesn't show up anymore
        nu.remove_narratorial(wsid, self.wsClient)

        narratorial_list = nlu.list_narratorials(self.wsClient)
        found = False
        for nt in narratorial_list:
            self.assertIn('ws', nt)
            self.assertIn('nar', nt)
            self.assertTrue(int(nt['ws'][8]['narrative']), nt['nar'][0])
            if wsid == nt['ws'][0]:
                found = True
        self.assertTrue(not found)

        self.wsClient.delete_workspace({'id': wsid})
