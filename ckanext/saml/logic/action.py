import json

from onelogin.saml2.idp_metadata_parser import (
    OneLogin_Saml2_IdPMetadataParser as Parser,
)

import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis

from ckanext.saml import config


def saml_idp_refresh(context, data_dict):
    """Refresh the IDP metadata from the remote source"""
    tk.check_access("sysadmin", context, data_dict)

    metadata_url = config.get_remote_idp_metadata_url()

    if not metadata_url:
        raise tk.ObjectNotFound("Metadata URL is not configured")

    meta = Parser.parse_remote(metadata_url)

    conn = connect_to_redis()
    conn.set(_get_redis_idp_key(), json.dumps(meta["idp"]))
    return meta["idp"]


def _get_redis_idp_key():
    return "ckan:{}:saml:idp".format(tk.config["ckan.site_id"])


def saml_idp_show(context, data_dict):
    """Return the cached IDP metadata info from Redis if it's here. Otherwise,
    perform an idp_refresh to fetch it from remote and return"""
    tk.check_access("sysadmin", context, data_dict)
    conn = connect_to_redis()

    if value := conn.get(_get_redis_idp_key()):
        return json.loads(value)

    return tk.get_action("saml_idp_refresh")(context, data_dict)
