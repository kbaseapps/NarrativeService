import pytest
from installed_clients.CatalogClient import Catalog
from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from NarrativeService.apps.appinfo import IGNORE_CATEGORIES, get_all_app_info
from NarrativeService.NarrativeServiceImpl import NarrativeService

APP_TAGS = ["release", "beta", "dev"]
USER_ID = "wjriehl"


def validate_app_info(info):
    info_keys = ["module_versions", "app_infos"]
    app_str_keys = [
        "app_type",
        "id",
        "name",
        "namespace",
        "subtitle",
        "tooltip",
        "ver"
    ]
    app_list_keys = [
        "authors",
        "categories",
        "input_types",
        "short_input_types",
        "output_types",
        "short_output_types"
    ]
    for key in info_keys:
        assert key in info
    for m in info["module_versions"]:
        assert info["module_versions"][m] is not None
    for a in info["app_infos"]:
        app = info["app_infos"][a]["info"]
        for str_key in app_str_keys:
            assert str_key in app
            assert isinstance(app[str_key], str)
        for list_key in app_list_keys:
            assert list_key in app
            assert isinstance(app[list_key], list)


@pytest.fixture
def catalog_client(config: dict[str, any]) -> Catalog:
    return Catalog(config["catalog-url"])


@pytest.fixture
def nms_client(config: dict[str, any]) -> NarrativeMethodStore:
    return NarrativeMethodStore(config["narrative-method-store"])


@pytest.mark.parametrize("app_tag", APP_TAGS)
def test_get_all_app_info_unit_ok(
    app_tag: str,
    nms_client: NarrativeMethodStore,
    catalog_client: Catalog
) -> None:
    info = get_all_app_info(app_tag, USER_ID, nms_client, catalog_client)
    validate_app_info(info)


@pytest.mark.parametrize("bad_tag", [None, [], {}, "foo", 5, -3, True, ""])
def test_get_all_app_info_bad_tag(
    bad_tag: str,
    nms_client: NarrativeMethodStore,
    catalog_client: Catalog
) -> None:
    with pytest.raises(ValueError, match="tag must be one of 'release', 'beta', or 'dev'"):
        get_all_app_info(bad_tag, USER_ID, nms_client, catalog_client)


@pytest.mark.parametrize("app_tag", APP_TAGS)
def test_get_all_app_info_impl_ok(
    app_tag: str,
    context: dict[str, any],
    service_impl: NarrativeService
) -> None:
    info = service_impl.get_all_app_info(context, {
        "tag": app_tag,
        "user": USER_ID
    })[0]
    validate_app_info(info)


def test_app_info_with_favorites(
    context: dict[str, any],
    service_impl: NarrativeService,
    catalog_client: Catalog
) -> None:
    # this is all public info, so just use my username, and i'll keep at least one favorite
    favorite_user = "wjriehl"
    cat_favorites = catalog_client.list_favorites(favorite_user)
    app_info = service_impl.get_all_app_info(context, {"tag": "release", "user": favorite_user})[0]
    for f in cat_favorites:
        fav_id = f"{f['module_name_lc']}/{f['id']}".lower()
        if fav_id in app_info["app_infos"]:
            assert "favorite" in app_info["app_infos"][fav_id]


def test_get_ignore_categories_ok(
    context: dict[str, any],
    service_impl: NarrativeMethodStore
) -> None:
    ignore_categories = service_impl.get_ignore_categories(context)[0]
    assert set(ignore_categories.keys()) == IGNORE_CATEGORIES
