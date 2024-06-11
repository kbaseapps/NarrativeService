from unittest.mock import MagicMock

import pytest
from installed_clients.CatalogClient import Catalog
from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from NarrativeService.apps.appinfo import get_all_app_info, get_ignore_categories

IGNORE_CATEGORIES = {"inactive", "importers", "viewers"}
APP_TAGS = ["release", "beta", "dev"]
USER_ID = "some_user"
NUM_DATA_APPS = 3
FAVORITE = "compoundsetutils/compound_set_from_model"
FAV_TIME = 1585695012878

@pytest.fixture
def mock_catalog(json_data, mocker) -> MagicMock:
    catalog = mocker.MagicMock()
    catalog.list_favorites.return_value = json_data("test_app_favorites.json")
    return catalog


@pytest.fixture
def mock_nms(json_data, mocker) -> MagicMock:
    nms = mocker.MagicMock()
    nms.list_methods.return_value = json_data("test_app_data.json")
    return nms


@pytest.mark.parametrize("app_tag", APP_TAGS)
def test_get_all_app_info_ok(
    app_tag: str,
    mock_nms: NarrativeMethodStore,
    mock_catalog: Catalog
) -> None:
    info = get_all_app_info(app_tag, USER_ID, mock_nms, mock_catalog)
    assert info["module_versions"] == {
        "compoundsetutils": "2.1.3"
    }
    assert len(info["app_infos"]) == NUM_DATA_APPS
    assert "favorite" in info["app_infos"][FAVORITE]
    assert info["app_infos"][FAVORITE]["favorite"] == FAV_TIME


@pytest.mark.parametrize("bad_tag", [None, [], {}, "foo", 5, -3])
def test_get_all_app_info_bad_tag(
    bad_tag: str,
    mock_nms: NarrativeMethodStore,
    mock_catalog: Catalog
) -> None:
    with pytest.raises(ValueError, match="tag must be one of 'release', 'beta', or 'dev'"):
        get_all_app_info(bad_tag, USER_ID, mock_nms, mock_catalog)


def test_get_ignore_categories_ok() -> None:
    ignore_categories = get_ignore_categories()
    expected = {"inactive", "importers", "viewers"}
    assert expected == set(ignore_categories.keys())
