# -*- coding: utf-8 -*-
from typing import Optional

from ckan.plugins import Interface
from onelogin.saml2.auth import OneLogin_Saml2_Auth


class ICKANSAML(Interface):
    """Implement custom SAML response modification."""

    def after_mapping(self, mapped_data, auth):
        """Return dictonary mapped fields.

        :returns: dictonary
        :rtype: dict

        """

        return mapped_data

    def roles_and_organizations(self, mapped_data, auth, user):
        """Map Roles and assign User to Organizations"""
        pass

    def saml_auth_class(self) -> Optional[OneLogin_Saml2_Auth]:
        """Custom SamlAuthenticator(subclass of OneLogin_Saml2_Auth)"""
        pass
