import unittest.mock as mock

import pytest
from onelogin.saml2.errors import OneLogin_Saml2_Error as SAMLError

import ckan.plugins.toolkit as tk

from ckanext.saml import config, const, helpers


@pytest.mark.usefixtures("with_plugins")
@pytest.mark.ckan_config(
    "ckan.site_url",
    "http://127.0.0.1:5000",
)
class TestSettingsParser:
    """The SAML is configured via ckan configuration and we should parse a nested
    structure"""

    def test_config_without_idp(self):
        """If there's no configuration for IDP, there must be an error"""
        with pytest.raises(SAMLError, match="idp_sso_url_invalid"):
            tk.h.saml_get_settings()

    @pytest.mark.ckan_config(f"{const.SETTINGS_PREFIX}idp.entityId", "idp_eid")
    @pytest.mark.ckan_config(
        f"{const.SETTINGS_PREFIX}idp.singleSignOnService.url",
        "http://idp/sso/post",
    )
    @pytest.mark.ckan_config(
        f"{const.SETTINGS_PREFIX}idp.singleSignOnService.binding",
        "idp_login_binding",
    )
    @pytest.mark.ckan_config(
        f"{const.SETTINGS_PREFIX}idp.singleLogoutService.url",
        "http://idp/slo/post",
    )
    @pytest.mark.ckan_config(
        f"{const.SETTINGS_PREFIX}idp.singleLogoutService.binding",
        "idp_logout_binding",
    )
    @pytest.mark.ckan_config(f"{const.SETTINGS_PREFIX}idp.x509cert", "idp_cert")
    def test_config_with_idp(self):
        """If there's no configuration for IDP, there must be an error"""
        settings = helpers._parse_dynamic_settings()

        assert settings["strict"] is True
        assert settings["debug"] is True

        assert settings["idp"]
        assert settings["idp"]["entityId"] == "idp_eid"
        assert settings["idp"]["x509cert"] == "idp_cert"
        assert settings["idp"]["singleSignOnService"]["url"] == "http://idp/sso/post"
        assert settings["idp"]["singleSignOnService"]["binding"] == "idp_login_binding"
        assert settings["idp"]["singleLogoutService"]["url"] == "http://idp/slo/post"
        assert settings["idp"]["singleLogoutService"]["binding"] == "idp_logout_binding"

        assert settings["sp"]
        assert (
            settings["sp"]["NameIDFormat"]
            == "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
        )
        assert settings["sp"]["entityId"] == "http://127.0.0.1:5000"
        assert settings["sp"]["privateKey"] == ""
        assert (
            settings["sp"]["assertionConsumerService"]["url"]
            == "http://127.0.0.1:5000/sso/post"
        )
        assert (
            settings["sp"]["assertionConsumerService"]["binding"]
            == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        )
        assert (
            settings["sp"]["singleLogoutService"]["url"]
            == "http://127.0.0.1:5000/slo/post"
        )
        assert (
            settings["sp"]["singleLogoutService"]["binding"]
            == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        )

    @pytest.mark.ckan_config(
        config.CONFIG_REMOTE_IDP_METADATA_URL, "http://127.0.0.1:5000"
    )
    def test_remote_idp(self, idp_metadata):
        """If the IDP metdata URL is provided, we don't have to provide settings
        manually. The function is mocked to prevent a real request"""
        with mock.patch(
            "ckanext.saml.helpers._get_remote_idp_settings",
            return_value=idp_metadata,
        ):
            settings = helpers._parse_dynamic_settings()

        assert settings["idp"]
        assert settings["idp"]["x509cert"]
        assert settings["idp"]["singleLogoutService"]
        assert settings["idp"]["singleSignOnService"]
        assert (
            settings["idp"]["entityId"]
            == "http://localhost:9001/simplesaml/saml2/idp/metadata.php"
        )
