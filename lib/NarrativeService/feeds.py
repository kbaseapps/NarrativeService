import requests

SERVICE_NAME = "narrativeservice"

def make_notification(note, feeds_url, auth_token):
    # calls the feeds service
    note["source"] = SERVICE_NAME
    headers = {"Authorization": auth_token}
    r = requests.post(feeds_url + "/api/V1/notification", json=note, headers=headers)
    if r.status_code != requests.codes.ok:
        raise RuntimeError(f"Unable to create notification: {r.text}")
    return r.json()["id"]
