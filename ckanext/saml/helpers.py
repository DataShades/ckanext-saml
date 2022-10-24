from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

import ckan.model as model
import ckan.plugins.toolkit as tk


from ckanext.saml.model.user import User
from ckanext.toolbelt.decorators import Collector
from . import utils, config

log = logging.getLogger(__name__)

helper, get_helpers = Collector("saml").split()


@helper
def logout_url(name_id: Optional[str] = None) -> str:
    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    return auth.logout(
        return_to=tk.h.url_for("saml.post_logout", _external=True),
        name_id=name_id,
    )


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
    return config.login_button_text()


@helper
def folder_path():
    return config.folder_path()


@helper
def attr_mapper():
    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location(
            "module.name",
            tk.h.saml_folder_path()
            + "/attributemaps/"
            + tk.config.get("ckan.saml_custom_attr_map", "mapper.py"),
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

    if config.use_remote_idp():
        settings["idp"] = tk.get_action("saml_idp_show")(
            {"ignore_auth": True}, {}
        )

    settings.setdefault("custom_base_path", custom_folder)
    return settings
