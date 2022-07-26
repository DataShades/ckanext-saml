from __future__ import annotations

import json
import logging
import os
from typing import Any

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.common import config

from ckanext.saml.model.user import User
from ckanext.toolbelt.decorators import Collector

log = logging.getLogger(__name__)

CONFIG_USE_REMOTE_IDP = "ckanext.saml.metadata.remote_idp"
CONFIG_LOGIN_TEXT = "ckan.saml_login_button_text"
CONFIG_FOLDER_PATH = "ckan.saml_custom_base_path"

DEFAULT_USE_REMOTE_IDP = False
DEFAULT_LOGIN_TEXT = "SAML Login"
DEFAULT_FOLDER_PATH = "/etc/ckan/default/saml"

helper, get_helpers = Collector("saml").split()


@helper
def is_saml_user(name: str) -> bool:
    user = model.User.get(name)
    if not user:
        return False

    return model.Session.query(
        model.Session.query(User).filter_by(id=user.id).exists()
    ).scalar()


@helper
def login_button_text():
    text = config.get(CONFIG_LOGIN_TEXT, DEFAULT_LOGIN_TEXT)
    return text


@helper
def folder_path():
    path = config.get(CONFIG_FOLDER_PATH, DEFAULT_FOLDER_PATH)
    return path


@helper
def attr_mapper():
    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location(
            "module.name",
            tk.h.saml_folder_path()
            + "/attributemaps/"
            + config.get("ckan.saml_custom_attr_map", "mapper.py"),
        )

        mapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mapper)
    except Exception as e:
        log.error("{0}".format(e))
        return None

    return mapper.MAP


@helper
def settings() -> dict[str, Any]:
    custom_folder = tk.h.saml_folder_path()

    filepath = os.path.join(custom_folder, "settings.json")
    if not os.path.exists(filepath):
        log.warning("SAML2 settings file not found: %s", filepath)
        return {}

    with open(filepath) as src:
        settings_str = src.read()

    prefix = "ckanext.saml.settings.substitution."
    for k, v in tk.config.items():
        if not k.startswith(prefix):
            continue
        settings_str = settings_str.replace(f"<{k[len(prefix):]}>", v)
    settings = json.loads(settings_str)

    if tk.asbool(tk.config.get(CONFIG_USE_REMOTE_IDP, DEFAULT_USE_REMOTE_IDP)):
        settings["idp"] = tk.get_action("saml_idp_show")({"ignore_auth": True}, {})

    settings.setdefault("custom_base_path", custom_folder)
    return settings
