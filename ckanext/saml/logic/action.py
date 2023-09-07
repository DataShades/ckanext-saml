from __future__ import annotations

import json
from typing import Any

import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis
from onelogin.saml2.idp_metadata_parser import (
    OneLogin_Saml2_IdPMetadataParser as Parser,
)

CONFIG_URL = "ckanext.saml.metadata.url"


def get_actions():
    return {
        "saml_idp_refresh": idp_refresh,
        "saml_idp_show": idp_show,
    }


def _idp_key():
    """Cache key for IdP details."""
    site_id = tk.config["ckan.site_id"]
    return "ckan:{}:saml:idp".format(site_id)


def _read_remote_metadata(path_or_url: str):
    if path_or_url.startswith("file://"):
        with open(path_or_url[len("file://"):]) as src:
            return Parser.parse(src.read())

    return Parser.parse_remote(path_or_url)


def idp_refresh(context: dict[str, Any], data_dict: dict[str, Any]):
    """Refresh IdP details using remote metadata."""
    tk.check_access("sysadmin", context, data_dict)

    url = data_dict.get("url", tk.config.get(CONFIG_URL))

    if not url:
        raise tk.ObjectNotFound(
            "Metadata URL is not configured: {}".format(CONFIG_URL)
        )
    meta = _read_remote_metadata(url)

    cache = connect_to_redis()
    cache.set(_idp_key(), json.dumps(meta["idp"]))
    return meta["idp"]


def idp_show(context: dict[str, Any], data_dict: dict[str, Any]):
    """Show IdP details pulled from the remote metadata."""
    tk.check_access("sysadmin", context, data_dict)
    cache = connect_to_redis()

    if value := cache.get(_idp_key()):
        return json.loads(value)

    return tk.get_action("saml_idp_refresh")(context, data_dict)
