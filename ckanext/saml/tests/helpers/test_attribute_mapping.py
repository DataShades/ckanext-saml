import pytest

import ckan.plugins.toolkit as tk

from ckanext.saml import config, const


@pytest.mark.usefixtures("with_plugins")
class TestAttributeMapper:
    """We use a Mapper to map the user attributes given to us by the remote IDP
    to match ours"""

    @pytest.mark.ckan_config(config.CONFIG_USE_CUSTOM_MAPPER, False)
    def test_default_mapping(self):
        """Same as previous, but we are stricly disabling the custom mapping"""
        assert tk.h.saml_get_attribute_mapper() == const.DEFAULT_MAPPING

    @pytest.mark.ckan_config(config.CONFIG_USE_CUSTOM_MAPPER, True)
    def test_custom_mapping_without_settings_attrs(self):
        """If the custom mapping is enabled, but we didn't set any attr, there
        will be an empty dict"""
        assert tk.h.saml_get_attribute_mapper() == {}

    @pytest.mark.ckan_config(config.CONFIG_USE_CUSTOM_MAPPER, True)
    @pytest.mark.ckan_config(f"{const.MAPPING_PREFIX}user_id", "uid")
    @pytest.mark.ckan_config(f"{const.MAPPING_PREFIX}email", "mail")
    @pytest.mark.ckan_config(f"{const.MAPPING_PREFIX}weird.key", "123")
    @pytest.mark.ckan_config(
        f"{const.MAPPING_PREFIX}name",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
    )
    def test_custom_mapping(self):
        """If the custom mapping is enabled, but we didn't set any attr, there
        will be an empty dict"""
        assert tk.h.saml_get_attribute_mapper() == {
            "email": "mail",
            "user_id": "uid",
            "weird.key": "123",
            "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
        }


@pytest.mark.usefixtures("with_plugins")
class TestAttributeMapperConfig:
    def test_custom_mapping_disabled_by_default(self):
        assert config.use_custom_mapper() is False

    @pytest.mark.ckan_config(config.CONFIG_USE_CUSTOM_MAPPER, False)
    def test_custom_mapping_disabled_explicitly(self):
        assert config.use_custom_mapper() is False

    @pytest.mark.ckan_config(config.CONFIG_USE_CUSTOM_MAPPER, True)
    def test_custom_mapping_enabled(self):
        assert config.use_custom_mapper() is True
