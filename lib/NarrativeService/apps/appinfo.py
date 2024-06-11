import contextlib

from installed_clients.CatalogClient import Catalog
from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore

IGNORE_CATEGORIES: set = {"inactive", "importers", "viewers"}
APP_TAGS: set = {"release", "beta", "dev"}


def get_ignore_categories() -> dict[str, int]:
    return dict.fromkeys(IGNORE_CATEGORIES, 1)


def _shorten_types(type_list: list[str]) -> list[str]:
    """
    convert ['KBaseMatrices.AmpliconMatrix'] to ['AmpliconMatrix']
    """
    shorten_types = []
    for t in type_list:
        with contextlib.suppress(IndexError):
            shorten_types.append(t.split(".")[1])

    return shorten_types


def get_all_app_info(tag: str, user: str, nms: NarrativeMethodStore, catalog: Catalog):
    if not isinstance(tag, str) or tag not in APP_TAGS:
        raise ValueError("tag must be one of 'release', 'beta', or 'dev'")
    apps = nms.list_methods({"tag": tag})
    app_infos = {}
    module_versions = {}
    for a in apps:
        # ignore empty apps or apps in IGNORE_CATEGORIES
        if not a or not set(a.get("categories")).isdisjoint(IGNORE_CATEGORIES):
            continue
        # add short version of input/output types
        for target_type in ["input_types", "output_types"]:
            a[f"short_{target_type}"] = _shorten_types(a.get(target_type))
        app_infos[a["id"].lower()] = {"info": a}
        if "module_name" in a:
            module_versions[a["module_name"].lower()] = a.get("ver")

    favorites = catalog.list_favorites(user)

    for fav in favorites:
        app_id = f"{fav['module_name_lc']}/{fav['id']}".lower()
        if app_id in app_infos:
            app_infos[app_id]["favorite"] = fav["timestamp"]

    return {
        "module_versions": module_versions,
        "app_infos": app_infos
    }
