import io
import os
import sys
from configparser import ConfigParser

from jinja2 import Template

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: <program> <deploy_cfg_template_file> <file_with_properties>")
        print("Properties from <file_with_properties> will be applied to <deploy_cfg_template_file>")
        print("template which will be overwritten with .orig copy saved in the same folder first.")
        sys.exit(1)
    file = open(sys.argv[1])
    text = file.read()
    t = Template(text)
    config = ConfigParser()
    if os.path.isfile(sys.argv[2]):
        config.read(sys.argv[2])
    elif "KBASE_ENDPOINT" in os.environ:
        kbase_endpoint = os.environ.get("KBASE_ENDPOINT")
        props = "[global]\n" + \
                "kbase_endpoint = " + kbase_endpoint + "\n" + \
                "job_service_url = " + kbase_endpoint + "/userandjobstate\n" + \
                "workspace_url = " + kbase_endpoint + "/ws\n" + \
                "shock_url = " + kbase_endpoint + "/shock-api\n" + \
                "handle_url = " + kbase_endpoint + "/handle_service\n" + \
                "srv_wiz_url = " + kbase_endpoint + "/service_wizard\n" + \
                "njsw_url = " + kbase_endpoint + "/njs_wrapper\n" + \
                "search_url = " + kbase_endpoint + "/searchapi2/rpc\n"
        if "AUTH_SERVICE_URL" in os.environ:
            props += "auth_service_url = " + os.environ.get("AUTH_SERVICE_URL") + "\n"
        elif "auth2services" in kbase_endpoint:
            props += "auth_service_url = " + kbase_endpoint + "/auth/api/legacy/KBase/Sessions/Login\n"
        props += "auth_service_url_allow_insecure = " + \
                 os.environ.get("AUTH_SERVICE_URL_ALLOW_INSECURE", "false") + "\n"
        config.read_file(io.StringIO(props))
    else:
        raise ValueError("Neither " + sys.argv[2] + " file nor KBASE_ENDPOINT env-variable found")
    props = dict(config.items("global"))
    for key in os.environ:
        if key.startswith("KBASE_SECURE_CONFIG_PARAM_"):
            param_name = key[len("KBASE_SECURE_CONFIG_PARAM_"):]
            props[param_name] = os.environ.get(key)
    output = t.render(props)
    with open(sys.argv[1] + ".orig", "w") as f:
        f.write(text)
    with open(sys.argv[1], "w") as f:
        f.write(output)
