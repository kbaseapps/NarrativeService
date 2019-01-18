import requests

def make_notification(note, feeds_url, auth_token):
    # calls the feeds service
    try:
        headers = {"Authorization": auth_token}
        r = requests.post("feeds_url" + "/api/V1/notification", json=note, headers=headers)
        r.raise_for_status()
        return r.json()["id"]
    except requests.HTTPError as e:
        raise RuntimeError("Unable to create notification: {}".format(str(e)))
