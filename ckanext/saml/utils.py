from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from .interfaces import ICKANSAML


CONFIG_HTTPS = "ckan.saml_use_https"
DEFAULT_HTTPS = "off"

CONFIG_DYNAMIC = "ckanext.saml.settings.dynamic"
DEFAULT_DYNAMIC = False

CONFIG_USE_FORWARDED_HOST = "ckanext.saml.use_forwarded_host"
DEFAULT_USE_FORWARDED_HOST = False

CONFIG_STATIC_HOST = "ckanext.saml.static_host"
DEFAULT_STATIC_HOST = None


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
    static_host = tk.config.get(CONFIG_STATIC_HOST, DEFAULT_STATIC_HOST)
    forwarded_host = tk.request.environ.get("HTTP_X_FORWARDED_HOST")

    if (
        tk.asbool(tk.config.get(CONFIG_USE_FORWARDED_HOST, DEFAULT_USE_FORWARDED_HOST))
        and forwarded_host
    ):
        host = forwarded_host
    elif static_host:
        host = static_host

    return {
        "https": tk.config.get(CONFIG_HTTPS, DEFAULT_HTTPS),
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

    if tk.asbool(tk.config.get(CONFIG_DYNAMIC, DEFAULT_DYNAMIC)):
        return Auth(req, old_settings=tk.h.saml_settings())

    custom_folder = tk.h.saml_folder_path()
    return Auth(req, custom_base_path=custom_folder)
