from __future__ import annotations

from datetime import datetime, timedelta

from flask import session

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.saml.config as config
from ckanext.saml.cli import get_commnads
from ckanext.saml.helpers import get_helpers
from ckanext.saml.logic.action import get_actions
from ckanext.saml.views import saml


@tk.blanket.config_declarations
class SamlPlugin(p.SingletonPlugin):
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.IClick)
    p.implements(p.ITemplateHelpers)

    # IActions
    def get_actions(self):
        return get_actions()

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # ITemplateHelpers

    def get_helpers(self):
        return get_helpers()

    if not tk.check_ckan_version("2.10"):
        # specifically for ckan 2.9 and lower versions
        p.implements(p.IAuthenticator, inherit=True)
        # IAuthenticator

        def identify(self):
            if "samlCKANuser" not in session:
                return

            now = datetime.utcnow()
            last_login = session.get("samlLastLogin", now)
            diff = now - last_login

            ttl = config.ttl()
            if diff < timedelta(seconds=ttl):
                tk.g.user = session["samlCKANuser"]

        def logout(self):
            if "samlNameId" in session:
                for key in saml.saml_details:
                    del session[key]

    # IBlueprint
    def get_blueprint(self):
        return [saml.get_bp()]

    # IClick
    def get_commands(self):
        return get_commnads()
