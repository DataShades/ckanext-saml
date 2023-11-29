from __future__ import annotations

from typing import Optional

import ckan.plugins.toolkit as tk

CONFIG_ERROR_TPL = "ckanext.saml.error_template"

CONFIG_SSO_PATH = "ckanext.saml.sso_path"
DEFAULT_SSO_PATH = "/sso/post"

CONFIG_SLO_PATH = "ckanext.saml.slo_path"
DEFAULT_SLO_PATH = "/slo/post"

CONFIG_STATIC_HOST = "ckanext.saml.static_host"
DEFAULT_STATIC_HOST = None

CONFIG_USE_FORWARDED_HOST = "ckanext.saml.use_forwarded_host"
DEFAULT_USE_FORWARDED_HOST = False

CONFIG_UNCONDITIONAL_LOGIN = "ckanext.saml.unconditional_login"
DEFAULT_UNCONDITIONAL_LOGIN = False

CONFIG_LOGIN_TEXT = "ckanext.saml.login_button_text"
DEFAULT_LOGIN_TEXT = "SAML Login"

CONFIG_REACTIVATE = "ckanext.saml.reactivate_deleted_account"
DEFAULT_REACTIVATE = False

CONFIG_USE_HTTPS = "ckanext.saml.use_https"
DEFAULT_USE_HTTPS = False

CONFIG_USE_NAMEID_AS_EMAIL = "ckanext.saml.use_nameid_as_email"
DEFAULT_USE_NAMEID_AS_EMAIL = False

CONFIG_USE_CUSTOM_MAPPER = "ckanext.saml.use_custom_mapper"
DEFAULT_USE_CUSTOM_MAPPER = False

CONFIG_REMOTE_IDP_METADATA_URL = "ckanext.saml.idp_metadata_url"
DEFAULT_REMOTE_IDP_METADATA_URL = None

CONFIG_RELAY_STATE = "ckanext.saml.relay_state"
DEFAULT_RELAY_STATE = None

CONFIG_USE_ROOT_PATH = "ckanext.saml.use_root_path"
DEFAULT_USE_ROOT_PATH = False

CONFIG_TTL = "ckanext.saml.session.ttl"
DEFAULT_TTL = 30 * 24 * 3600

CONFIG_FOLDER_PATH = "ckanext.saml.metadata.base_path"
DEFAULT_FOLDER_PATH = ""

CONFIG_SAVE_LAST_SAML_RESPONSE = "ckanext.saml.log_last_saml_response"
DEFAULT_SAVE_LAST_SAML_RESPONSE = False


def reactivate_deleted_account() -> bool:
    return tk.asbool(tk.config.get(CONFIG_REACTIVATE, DEFAULT_REACTIVATE))


def get_sso_path() -> str:
    return tk.config.get(CONFIG_SSO_PATH, DEFAULT_SSO_PATH)


def get_slo_path() -> str:
    return tk.config.get(CONFIG_SLO_PATH, DEFAULT_SLO_PATH)


def get_error_template() -> Optional[str]:
    return tk.config.get(CONFIG_ERROR_TPL)


def get_login_button_text() -> str:
    return tk.config.get(CONFIG_LOGIN_TEXT, DEFAULT_LOGIN_TEXT)


def is_unconditional_login_enabled() -> bool:
    return tk.asbool(
        tk.config.get(CONFIG_UNCONDITIONAL_LOGIN, DEFAULT_UNCONDITIONAL_LOGIN)
    )


def use_forwarded_host() -> bool:
    return tk.asbool(
        tk.config.get(CONFIG_USE_FORWARDED_HOST, DEFAULT_USE_FORWARDED_HOST)
    )


def static_host() -> Optional[str]:
    return tk.config.get(CONFIG_STATIC_HOST, DEFAULT_STATIC_HOST)


def use_https() -> str:
    return (
        "on" if tk.asbool(tk.config.get(CONFIG_USE_HTTPS, DEFAULT_USE_HTTPS)) else "off"
    )


def use_nameid_as_email() -> bool:
    return tk.asbool(
        tk.config.get(CONFIG_USE_NAMEID_AS_EMAIL, DEFAULT_USE_NAMEID_AS_EMAIL)
    )


def use_custom_mapper() -> bool:
    return tk.asbool(tk.config.get(CONFIG_USE_CUSTOM_MAPPER, DEFAULT_USE_CUSTOM_MAPPER))


def get_remote_idp_metadata_url() -> str | None:
    """User can define a url to IDP metadata, istead of configuring it manually
    via CKAN config"""
    return tk.config.get(
        CONFIG_REMOTE_IDP_METADATA_URL, DEFAULT_REMOTE_IDP_METADATA_URL
    )


def get_relay_state() -> str | None:
    """The destination that the user will be redirected to after they have
    completed the authentication process at the identity provider (IdP)."""
    return tk.config.get(CONFIG_RELAY_STATE, DEFAULT_RELAY_STATE)


def use_root_path() -> bool:
    return tk.asbool(tk.config.get(CONFIG_USE_ROOT_PATH, DEFAULT_USE_ROOT_PATH))


def get_session_ttl() -> int:
    return tk.asint(tk.config.get(CONFIG_TTL, DEFAULT_TTL))


def get_folder_path() -> str:
    """Return a path to a folder with SAML settings"""
    return tk.config.get(CONFIG_FOLDER_PATH, DEFAULT_FOLDER_PATH)


def log_last_saml_response() -> bool:
    """Define if we need to store a last SAML response for a debug purpose.
    If could be used to infer the user attributes if the client didn't provide it"""
    return tk.asbool(
        tk.config.get(CONFIG_SAVE_LAST_SAML_RESPONSE, DEFAULT_SAVE_LAST_SAML_RESPONSE)
    )
