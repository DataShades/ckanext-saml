from __future__ import annotations
from typing import Optional

import ckan.plugins.toolkit as tk

CONFIG_ERROR_TPL = "ckanext.saml.error_template"

CONFIG_SSO_PATH = "ckanext.saml.sso_path"
DEFAULT_SSO_PATH = "/sso/post"

CONFIG_SLO_PATH = "ckanext.saml.slo_path"
DEFAULT_SLO_PATH = "/slo/post"


def sso_path() -> str:
    return tk.config.get(CONFIG_SSO_PATH, DEFAULT_SSO_PATH)


def slo_path() -> str:
    return tk.config.get(CONFIG_SLO_PATH, DEFAULT_SLO_PATH)


def error_template() -> Optional[str]:
    return tk.config.get(CONFIG_ERROR_TPL)
