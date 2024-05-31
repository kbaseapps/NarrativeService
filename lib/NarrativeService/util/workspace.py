from installed_clients.WorkspaceClient import Workspace


def get_ws_admins(ws_id, ws_url, admin_token):
    ws = Workspace(url=ws_url, token=admin_token)
    perms = ws.administer({
        "command": "getPermissionsMass",
        "params": {
            "workspaces": [{"id": ws_id}]
        }
    })["perms"][0]

    admins = list()
    for u in perms:
        if perms[u] == "a":
            admins.append(u)
    return admins
