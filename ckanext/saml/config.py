from __future__ import annotations
from typing import Optional

import ckan.plugins.toolkit as tk

CONFIG_ERROR_TPL = "ckanext.saml.error_template"

CONFIG_SSO_PATH = "ckanext.saml.sso_path"
DEFAULT_SSO_PATH = "/sso/post"

CONFIG_SLO_PATH = "ckanext.saml.slo_path"
DEFAULT_SLO_PATH = "/slo/post"

CONFIG_DYNAMIC = "ckanext.saml.settings.dynamic"
DEFAULT_DYNAMIC = False

CONFIG_USE_REMOTE_IDP = "ckanext.saml.metadata.remote_idp"
DEFAULT_USE_REMOTE_IDP = False

CONFIG_STATIC_HOST = "ckanext.saml.static_host"
DEFAULT_STATIC_HOST = None

CONFIG_USE_FORWARDED_HOST = "ckanext.saml.use_forwarded_host"
DEFAULT_USE_FORWARDED_HOST = False

CONFIG_UNCONDITIONAL_LOGIN = "ckanext.saml.unconditional_login"
DEFAULT_UNCONDITIONAL_LOGIN = False

CONFIG_LOGIN_TEXT = "ckanext.saml.login_button_text"
LEGACY_CONFIG_LOGIN_TEXT = "ckan.saml_login_button_text"
DEFAULT_LOGIN_TEXT = "SAML Login"

CONFIG_REACTIVATE = "ckanext.saml.reactivate_deleted_account"
DEFAULT_REACTIVATE = False

CONFIG_FOLDER_PATH = "ckanext.saml.metadata.base_path"
LEGACY_CONFIG_FOLDER_PATH = "ckan.saml_custom_base_path"
DEFAULT_FOLDER_PATH = "/etc/ckan/default/saml"

CONFIG_HTTPS = "ckan.saml_use_https"
DEFAULT_HTTPS = "off"


def reactivate_deleted_account() -> bool:
    return tk.asbool(tk.config.get(CONFIG_REACTIVATE, DEFAULT_REACTIVATE))


def sso_path() -> str:
    return tk.config.get(CONFIG_SSO_PATH, DEFAULT_SSO_PATH)


def slo_path() -> str:
    return tk.config.get(CONFIG_SLO_PATH, DEFAULT_SLO_PATH)


def error_template() -> Optional[str]:
    return tk.config.get(CONFIG_ERROR_TPL)


def login_button_text() -> str:
    legacy = tk.config.get(LEGACY_CONFIG_LOGIN_TEXT)
    if legacy:
        return legacy

    return tk.config.get(CONFIG_LOGIN_TEXT, DEFAULT_LOGIN_TEXT)


def folder_path() -> str:
    legacy = tk.config.get(LEGACY_CONFIG_FOLDER_PATH)
    if legacy:
        return legacy

    return tk.config.get(CONFIG_FOLDER_PATH, DEFAULT_FOLDER_PATH)


def use_remote_idp() -> bool:
    return tk.asbool(tk.config.get(CONFIG_USE_REMOTE_IDP, DEFAULT_USE_REMOTE_IDP))

def use_dynamic_config() -> bool:
    return tk.asbool(tk.config.get(CONFIG_DYNAMIC, DEFAULT_DYNAMIC))


def unconditional_login() -> bool:
    return tk.asbool(
            tk.config.get(
                CONFIG_UNCONDITIONAL_LOGIN, DEFAULT_UNCONDITIONAL_LOGIN
            )
        )

def use_forwarded_host() -> bool:
    return tk.asbool(
            tk.config.get(
                CONFIG_USE_FORWARDED_HOST, DEFAULT_USE_FORWARDED_HOST
            )
        )

def static_host() -> Optional[str]:
    return tk.config.get(CONFIG_STATIC_HOST, DEFAULT_STATIC_HOST)

def https() -> str:
    return tk.config.get(CONFIG_HTTPS, DEFAULT_HTTPS)
