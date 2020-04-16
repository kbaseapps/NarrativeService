from installed_clients.NarrativeMethodStoreClient import NarrativeMethodStore
from installed_clients.CatalogClient import Catalog

IGNORE_CATEGORIES = {"inactive", "importers", "viewers"}


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
        # ignore empty apps or apps in IGNORE_CATEGORIES
        if not a or not set(a.get('categories')).isdisjoint(IGNORE_CATEGORIES):
            continue
        # add short version of input/output types
        for target_type in ['input_types', 'output_types']:
            a['short_{}'.format(target_type)] = _shorten_types(a.get(target_type))
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
