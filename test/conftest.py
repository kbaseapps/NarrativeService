import os
from configparser import ConfigParser

import pytest


@pytest.fixture
def config():
    config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
    config = ConfigParser()
    config.read(config_file)
    return dict(config.items("NarrativeService"))
