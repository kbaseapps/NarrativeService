import os
import unittest
from configparser import ConfigParser

from installed_clients.authclient import KBaseAuth as _KBaseAuth
from installed_clients.CatalogClient import Catalog
from NarrativeService.apps.appinfo import get_all_app_info
from NarrativeService.NarrativeServiceImpl import NarrativeService
from NarrativeService.NarrativeServiceServer import MethodContext

IGNORE_CATEGORIES = {"inactive", "importers", "viewers"}


class AppInfoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get("KB_AUTH_TOKEN", None)
        config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items("NarrativeService"):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get("auth-service-url",
                                     "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        cls.user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({"token": token,
                        "user_id": cls.user_id,
                        "provenance": [
                            {"service": "NarrativeService",
                             "method": "please_never_use_it_in_production",
                             "method_params": []
                             }],
                        "authenticated": 1})
        cls.nmsURL = cls.cfg["narrative-method-store"]
        cls.catalogURL = cls.cfg["catalog-url"]
        cls.wsURL = cls.cfg["workspace-url"]
        cls.serviceImpl = NarrativeService(cls.cfg)

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_get_all_app_info_unit_ok(self):
        tags = ["release", "beta", "dev"]
        for t in tags:
            info = get_all_app_info(t, self.user_id, self.nmsURL, self.catalogURL)
            self._validate_app_info(info)

    def test_get_all_app_info_bad_tag(self):
        bad_tags = [None, [], {}, "foo", 5, -3]
        for t in bad_tags:
            with self.assertRaises(ValueError) as e:
                get_all_app_info(t, self.user_id, self.nmsURL, self.catalogURL)
            self.assertIn("tag must be one of 'release', 'beta', or 'dev'", str(e.exception))

    def test_get_all_app_info_impl_ok(self):
        impl = self.getImpl()
        ctx = self.getContext()
        tags = ["release", "beta", "dev"]
        for t in tags:
            info = impl.get_all_app_info(ctx, {
                "tag": t,
                "user": self.user_id
            })[0]
            self._validate_app_info(info)

    def test_app_info_with_favorites(self):
        impl = self.getImpl()
        ctx = self.getContext()
        tag = "release"
        catalog = Catalog(self.catalogURL)
        favorite_user = "wjriehl"  # this is all public info, so just use my username, and i'll make sure to have at least one favorite
        cat_favorites = catalog.list_favorites(favorite_user)
        app_info = impl.get_all_app_info(ctx, {"tag": tag, "user": favorite_user})[0]
        for f in cat_favorites:
            fav_id = f"{f['module_name_lc']}/{f['id']}".lower()
            if fav_id in app_info["app_infos"]:
                self.assertIn("favorite", app_info["app_infos"][fav_id])

    def _validate_app_info(self, info):
        self.assertIn("module_versions", info)
        self.assertIn("app_infos", info)
        for m in info["module_versions"]:
            self.assertIsNotNone(info["module_versions"][m])
        for a in info["app_infos"]:
            app = info["app_infos"][a]["info"]
            self.assertIn("app_type", app)
            self.assertIn("authors", app)
            self.assertIsInstance(app["authors"], list)
            self.assertIn("categories", app)
            self.assertIsInstance(app["categories"], list)
            for category in IGNORE_CATEGORIES:
                self.assertNotIn(category, app["categories"])
            self.assertIn("id", app)
            self.assertIn("input_types", app)
            self.assertIsInstance(app["input_types"], list)
            self.assertIn("short_input_types", app)
            self.assertIsInstance(app["short_input_types"], list)
            self.assertIn("name", app)
            self.assertIn("namespace", app)
            self.assertIn("output_types", app)
            self.assertIsInstance(app["output_types"], list)
            self.assertIn("short_output_types", app)
            self.assertIsInstance(app["short_output_types"], list)
            self.assertIn("subtitle", app)
            self.assertIn("tooltip", app)
            self.assertIn("ver", app)

    def test_get_ignore_categories_ok(self):
        impl = self.getImpl()
        ctx = self.getContext()
        ignore_categories = impl.get_ignore_categories(ctx)[0]

        expected_keys = ["inactive", "importers", "viewers"]
        self.assertCountEqual(expected_keys, ignore_categories.keys())
