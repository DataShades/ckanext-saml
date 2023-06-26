from __future__ import annotations

import logging
from typing import Any, Optional

from onelogin.saml2.auth import OneLogin_Saml2_Settings as SAMLSettings

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.saml import config, const, utils
from ckanext.saml.model.user import User

log = logging.getLogger(__name__)


def saml_logout_url(name_id: Optional[str] = None) -> str:
    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    return auth.logout(
        return_to=tk.h.url_for("saml.post_logout", _external=True),
        name_id=name_id,
    )


def saml_is_saml_user(name: str) -> bool:
    user = model.User.get(name)
    if not user:
        return False

    return model.Session.query(
        model.Session.query(User).filter_by(id=user.id).exists()
    ).scalar()


def saml_get_login_button_text():
    return config.get_login_button_text()


def saml_get_attribute_mapper() -> dict[str, str]:
    """Return a SAML user attributes mapping. If the custom mapping is not
    enabled, use default mapping."""
    if not config.use_custom_mapper():
        return const.DEFAULT_MAPPING

    mapping: dict[str, str] = {}

    prefix = const.MAPPING_PREFIX

    for k, v in tk.config.items():
        if not k.startswith(prefix):
            continue

        mapping[k[len(prefix) :]] = v

    return mapping


def saml_get_settings() -> SAMLSettings:
    """Prepare a SAML settings. Fill a settings with a default values before,
    then update it if an option is declared."""

    return SAMLSettings(settings=_parse_settings())


def _parse_settings():
    settings = _get_default_sp_settings()

    prefix = const.SETTINGS_PREFIX

    for k, v in tk.config.items():
        if not k.startswith(prefix):
            continue

        keys = list(enumerate(k[len(prefix) :].split(".")))
        nested_dict = settings

        for idx, key in keys:
            is_last_key = keys[-1] == (idx, key)
            value: str | dict[str, Any] = v if is_last_key else {}

            if not is_last_key:
                nested_dict.setdefault(key, value)
            else:
                nested_dict[key] = value

            nested_dict = nested_dict[key]

    if config.get_remote_idp_metadata_url():
        settings["idp"] = _get_remote_idp_settings()

    return settings


def _get_default_sp_settings() -> dict[str, Any]:
    """Since SP is our CKAN instance, we can assume, that user could use it
    with a default values"""

    return {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": tk.config["ckan.site_url"],
            "assertionConsumerService": {
                "url": tk.url_for("saml.post_login", _external=True),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": tk.url_for("saml.post_logout", _external=True),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
            "x509cert": "",
            "privateKey": "",
        },
        "idp": {},
    }


def _get_remote_idp_settings() -> dict[str, Any]:
    return tk.get_action("saml_idp_show")({"ignore_auth": True}, {})
