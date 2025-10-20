from __future__ import annotations

from typing import Optional

import ckan.plugins.toolkit as tk

ERROR_TPL = "ckanext.saml.error_template"
SSO_PATH = "ckanext.saml.sso_path"
SLO_PATH = "ckanext.saml.slo_path"
DYNAMIC = "ckanext.saml.settings.dynamic"
USE_REMOTE_IDP = "ckanext.saml.metadata.remote_idp"
STATIC_HOST = "ckanext.saml.static_host"
USE_FORWARDED_HOST = "ckanext.saml.use_forwarded_host"
UNCONDITIONAL_LOGIN = "ckanext.saml.unconditional_login"
LOGIN_TEXT = "ckanext.saml.login_button_text"
REACTIVATE = "ckanext.saml.reactivate_deleted_account"
FOLDER_PATH = "ckanext.saml.metadata.base_path"
HTTPS = "ckan.saml_use_https"
USE_NAMEID_AS_EMAIL = "ckan.saml_use_nameid_as_email"
TTL = "ckanext.saml.session.ttl"
NAME_FROM_RESPONSE = "ckan.saml.name_from_response"
USER_FIELDS_TRIGGER_UPDATE = "ckan.saml.user_fields_trigger_update"
FORCE_AUTHN = "ckanext.saml.force_authn"


def reactivate_deleted_account() -> bool:
    return tk.config[REACTIVATE]


def sso_path() -> str:
    return tk.config[SSO_PATH]


def slo_path() -> str:
    return tk.config[SLO_PATH]


def error_template() -> str | None:
    return tk.config[ERROR_TPL]


def login_button_text() -> str:
    return tk.config[LOGIN_TEXT]


def folder_path() -> str:
    return tk.config[FOLDER_PATH]


def use_remote_idp() -> bool:
    return tk.config[USE_REMOTE_IDP]


def use_dynamic_config() -> bool:
    return tk.config[DYNAMIC]


def unconditional_login() -> bool:
    return tk.config[UNCONDITIONAL_LOGIN]


def use_forwarded_host() -> bool:
    return tk.config[USE_FORWARDED_HOST]


def static_host() -> str | None:
    return tk.config[STATIC_HOST]


def https() -> str:
    return tk.config[HTTPS]


def use_nameid_as_email() -> bool:
    return tk.config[USE_NAMEID_AS_EMAIL]


def ttl() -> int:
    return tk.config[TTL]


def use_name_from_response() -> bool:
    return tk.config[NAME_FROM_RESPONSE]


def user_fields_trigger_update() -> list[str]:
    return tk.config[USER_FIELDS_TRIGGER_UPDATE]


def force_authn() -> bool:
    return tk.config[FORCE_AUTHN]
