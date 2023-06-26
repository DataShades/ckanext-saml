from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckanext.saml import cli
from ckanext.saml.views import saml


@tk.blanket.actions
@tk.blanket.helpers
class SamlPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # IBlueprint
    def get_blueprint(self):
        return saml.get_blueprints()

    def get_commands(self):
        return cli.get_commands()
