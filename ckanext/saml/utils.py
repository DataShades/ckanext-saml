from __future__ import annotations

import logging
import re
import json
from typing import Any
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Utils

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckanext.saml import config
from ckanext.saml.interfaces import ICKANSAML

log = logging.getLogger(__name__)


def prepare_from_flask_request() -> dict[str, Any]:
    url_data = urlparse(tk.request.url)
    req_path = tk.request.path
    host = tk.request.host
    static_host = config.static_host()
    forwarded_host = tk.request.environ.get("HTTP_X_FORWARDED_HOST")

    if config.use_root_path():
        # FIX FOR ROOT_PATH REMOVED IN request.path
        root_path: str = tk.config["ckan.root_path"]

        if root_path:
            root_path = re.sub("/{{LANG}}", "", root_path)
            req_path = root_path + req_path

    if config.use_forwarded_host() and forwarded_host:
        host = forwarded_host
    elif static_host:
        host = static_host

    return {
        "https": config.use_https(),
        "http_host": host,
        "server_port": url_data.port,
        "script_name": req_path,
        "get_data": tk.request.args.copy(),
        "post_data": tk.request.form.copy(),
    }


def make_auth(req: dict[str, Any]) -> OneLogin_Saml2_Auth:
    for p in plugins.PluginImplementations(ICKANSAML):
        Auth = p.saml_auth_class()
        if Auth:
            break
    else:
        Auth = OneLogin_Saml2_Auth

    return Auth(req, tk.h.saml_get_settings())


def decode_saml_response(response: str) -> bytes:
    return OneLogin_Saml2_Utils.decode_base64_and_inflate(response)


def log_saml_response(saml_response_data: dict[str, Any]) -> None:
    """Log SAML response details"""
    log.debug("*** SAML DEBUG ***")
    log.debug(json.dumps(saml_response_data, indent=4))
    log.debug("*** SAML DEBUG ***")
