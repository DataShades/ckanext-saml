from __future__ import annotations

import os
import json
import logging
from typing import Any
from ckan.common import config
import ckan.plugins.toolkit as tk
import ckan.model as model

from ckanext.toolbelt.decorators import Collector
from ckanext.saml.model.saml2_user import SAML2User


log = logging.getLogger(__name__)

CONFIG_USE_REMOTE_IDP = "ckanext.saml.metadata.remote_idp"
DEFAULT_USE_REMOTE_IDP = False

helper, get_helpers = Collector("saml").split()


@helper
def is_saml_user(name: str) -> bool:
    user = model.User.get(name)
    if not user:
        return False

    return model.Session.query(
        model.Session.query(SAML2User).filter_by(id=user.id).exists()
    ).scalar()



@helper
def login_button_text():
    text = config.get("ckan.saml_login_button_text", "SAML Login")
    return text


@helper
def folder_path():
    path = config.get("ckan.saml_custom_base_path", "/etc/ckan/default/saml")
    return path


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

    with open(os.path.join(custom_folder, "settings.json")) as src:
        settings_str = src.read()

    prefix = "ckanext.saml.settings.substitution."
    for k, v in tk.config.items():
        if not k.startswith(prefix):
            continue
        settings_str = settings_str.replace(f"<{k[len(prefix):]}>", v)
    settings = json.loads(settings_str)

    if tk.asbool(tk.config.get(CONFIG_USE_REMOTE_IDP, DEFAULT_USE_REMOTE_IDP)):
        settings["idp"] = tk.get_action("saml_idp_show")({"ignore_auth": True}, {})

    settings.setdefault('custom_base_path', custom_folder)
    return settings
