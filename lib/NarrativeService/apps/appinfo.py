from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from installed_clients.CatalogClient import Catalog

IGNORE_CATEGORIES = {"inactive", "importers", "viewers"}
UNUSED_INFO = {'tooltip', 'icon', 'authors', 'app_type', 'namespace'}


def get_ignore_categories():
    return {x: 1 for x in IGNORE_CATEGORIES}


def _shorten_types(type_list):
    '''
    convert ['KBaseMatrices.AmpliconMatrix'] to ['AmpliconMatrix']
    '''
    shorten_types = list()
    for t in type_list:
        try:
            shorten_types.append(t.split('.')[1])
        except IndexError:
            pass

    return shorten_types


def get_all_app_info(tag, user, nms_url, catalog_url):
    if tag not in ["release", "beta", "dev"]:
        raise ValueError("tag must be one of 'release', 'beta', or 'dev'")
    nms = NarrativeMethodStore(nms_url)
    catalog = Catalog(catalog_url)
    apps = nms.list_methods({"tag": tag})
    app_infos = {}
    module_versions = {}
    for a in apps:
        if not set(a.get('categories')).isdisjoint(IGNORE_CATEGORIES):
            # ignore apps in IGNORE_CATEGORIES
            continue
        [a.pop(key, None) for key in UNUSED_INFO]  # remove unused info
        a['short_input_types'] = _shorten_types(a.get('input_types'))
        a['short_output_types'] = _shorten_types(a.get('output_types'))
        app_infos[a["id"].lower()] = {"info": a}
        if "module_name" in a:
            module_versions[a["module_name"].lower()] = a.get("ver")

    favorites = catalog.list_favorites(user)

    for fav in favorites:
        app_id = fav["module_name_lc"] + "/" + fav["id"]
        if app_id in app_infos:
            app_infos[app_id]["favorite"] = fav["timestamp"]

    return {
        "module_versions": module_versions,
        "app_infos": app_infos
    }
