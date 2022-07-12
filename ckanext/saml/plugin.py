from __future__ import annotations

from datetime import datetime, timedelta

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from flask import session

from ckanext.saml.cli import get_commnads
from ckanext.saml.helpers import get_helpers
from ckanext.saml.logic.action import get_actions
from ckanext.saml.views import saml

CONFIG_TTL = "ckanext.saml.session.ttl"
DEFAULT_TTL = 30 * 24 * 3600


class SamlPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthenticator, inherit=True)
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

    # IAuthenticator

    def identify(self):

        if "samlCKANuser" not in session:
            return

        now = datetime.utcnow()
        last_login = session.get("samlLastLogin", now)
        diff = now - last_login

        ttl = tk.asint(tk.config.get(CONFIG_TTL, DEFAULT_TTL))
        if diff < timedelta(seconds=ttl):
            tk.g.user = session["samlCKANuser"]

    def logout(self):
        if "samlNameId" in session:
            for key in saml.saml_details:
                del session[key]

    # IBlueprint
    def get_blueprint(self):
        return [saml.saml]

    # IClick
    def get_commands(self):
        return get_commnads()
