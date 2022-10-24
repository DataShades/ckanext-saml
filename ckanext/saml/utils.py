from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Utils

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from .interfaces import ICKANSAML
from . import config


def prepare_from_flask_request() -> dict[str, Any]:
    url_data = urlparse(tk.request.url)

    req_path = tk.request.path
    if tk.asbool(tk.config.get("ckan.saml_use_root_path", False)):
        # FIX FOR ROOT_PATH REMOVED IN request.path
        root_path = tk.config.get("ckan.root_path", None)
        if root_path:
            root_path = re.sub("/{{LANG}}", "", root_path)
            req_path = root_path + req_path

    host = tk.request.host
    static_host = config.static_host()
    forwarded_host = tk.request.environ.get("HTTP_X_FORWARDED_HOST")

    if config.use_forwarded_host() and forwarded_host:
        host = forwarded_host
    elif static_host:
        host = static_host

    return {
        "https": config.https(),
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

    if config.use_dynamic_config():
        return Auth(req, old_settings=tk.h.saml_settings())

    custom_folder = tk.h.saml_folder_path()
    return Auth(req, custom_base_path=custom_folder)


def decode_saml_response(response: str) -> bytes:
    return OneLogin_Saml2_Utils.decode_base64_and_inflate(response)
