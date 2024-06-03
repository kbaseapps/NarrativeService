import os
from configparser import ConfigParser

import pytest


@pytest.fixture
def config():
    """Load and return the test config as a dictionary."""
    config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
    config = ConfigParser()
    config.read(config_file)
    return dict(config.items("NarrativeService"))
