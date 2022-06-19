import json
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser as Parser
import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis

CONFIG_URL = "ckanext.saml.metadata.url"

def get_actions():
    return {
        "saml_idp_refresh": idp_refresh,
        "saml_idp_show": idp_show,
    }


def _idp_key():
    site_id = tk.config["ckan.site_id"]
    return "ckan:{}:saml:idp".format(site_id)


def idp_refresh(context, data_dict):
    tk.check_access("sysadmin", context, data_dict)

    url = tk.config.get(CONFIG_URL)
    if not url:
        raise tk.ObjectNotFound("Metadata URL is not convigured: {}".format(CONFIG_URL))
    meta = Parser.parse_remote(url)

    cache = connect_to_redis()
    cache.set(_idp_key(), json.dumps(meta))
    return meta


def idp_show(context, data_dict):
    tk.check_access("sysadmin", context, data_dict)
    cache = connect_to_redis()
    value = cache.get(_idp_key())

    if not value:
        raise tk.ObjectNotFound("No IdP details found")

    return json.loads(value)
