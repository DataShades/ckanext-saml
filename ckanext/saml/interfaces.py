# -*- coding: utf-8 -*-
from ckan.plugins import Interface


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
