# -*- coding: utf-8 -*-

import time
from .baseclient import (
    BaseClient,
    ServerError
)


class DynamicServiceClient:

    def __init__(self, sw_url: str, service_ver: str, module_name: str,
                 token: str, url_cache_time: int = 300):
        """
        sw_url - service wizard URL
        service_ver - version of service to invoke
        module_name - the registered module name used in URL lookup
        url_cache_time - seconds
        """
        self.sw_url = sw_url
        self.service_ver = service_ver
        self.module_name = module_name
        self.url_cache_time = url_cache_time
        self.cached_url = None
        self.last_refresh_time = None
        self.token = token

    def call_method(self, method: str, params_array: list) -> list:
        """
        Calls the given method. Uses the BaseClient and cached service URL.
        """
        was_url_refreshed = False
        if not self.cached_url or (time.time() - self.last_refresh_time > self.url_cache_time):
            self._lookup_url()
            was_url_refreshed = True
        try:
            return self._call(method, params_array, self.token)
        except ServerError:
            # Happens if a URL expired for real, even though it's still cached.
            if was_url_refreshed:
                raise  # Forwarding error with no changes
            else:
                self._lookup_url()
                return self._call(method, params_array, self.token)

    def _lookup_url(self):
        bc = BaseClient(url=self.sw_url, lookup_url=False)
        self.cached_url = bc.call_method('ServiceWizard.get_service_status',
                                         [{'module_name': self.module_name,
                                           'version': self.service_ver}])['url']
        self.last_refresh_time = time.time()

    def _call(self, method, params_array, token):
        bc = BaseClient(url=self.cached_url, token=token, lookup_url=False)
        return bc.call_method(self.module_name + '.' + method, params_array)
