from __future__ import annotations

from datetime import datetime, timedelta

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from flask import session

from ckanext.saml.cli import get_commnads
from ckanext.saml.helpers import get_helpers
from ckanext.saml.logic.action import get_actions
from ckanext.saml.views import saml
import ckanext.saml.config as config


class SamlPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)

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
        plugins.implements(plugins.IAuthenticator, inherit=True)
        # IAuthenticator

        def identify(self):
            if "samlCKANuser" not in session:
                return

            now = datetime.utcnow()
            last_login = session.get("samlLastLogin", now)
            diff = now - last_login

            ttl = tk.asint(tk.config.get(
                config.CONFIG_TTL, config.DEFAULT_TTL))
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
