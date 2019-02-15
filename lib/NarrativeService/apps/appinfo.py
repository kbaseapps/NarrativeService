from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from installed_clients.CatalogClient import Catalog


def get_all_app_info(tag, user, nms_url, catalog_url):
    if tag not in ["release", "beta", "dev"]:
        raise ValueError("tag must be one of 'release', 'beta', or 'dev'")
    nms = NarrativeMethodStore(nms_url)
    catalog = Catalog(catalog_url)
    apps = nms.list_methods({"tag": tag})
    app_infos = {}
    module_versions = {}
    for a in apps:
        app_infos[a["id"].lower()] = {"info": a}
        if "module_name" in a:
            module_versions[a["module_name"].lower()] = a.get("ver")

    categories = nms.list_categories({})[0]
    favorites = catalog.list_favorites(user)

    for fav in favorites:
        app_id = fav["module_name_lc"] + "/" + fav["id"]
        if app_id in app_infos:
            app_infos[app_id]["favorite"] = fav["timestamp"]

    return {
        "module_versions": module_versions,
        "categories": categories,
        "app_infos": app_infos
    }
