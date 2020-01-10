import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import request, g
import ckan.lib.helpers as h
from flask import session

from ckanext.saml.views import saml
from ckanext.saml.cli import get_commnads
from ckanext.saml.helpers import get_helpers


class SamlPlugin(plugins.SingletonPlugin):
	plugins.implements(plugins.IConfigurer)
	plugins.implements(plugins.IAuthenticator, inherit=True)
	plugins.implements(plugins.IBlueprint)
	plugins.implements(plugins.IClick)
	plugins.implements(plugins.ITemplateHelpers)

	# IConfigurer

	def update_config(self, config_):
		toolkit.add_template_directory(config_, 'templates')
		toolkit.add_public_directory(config_, 'public')
		toolkit.add_resource('fanstatic',
			'saml')

	# ITemplateHelpers

	def get_helpers(self):
		return get_helpers()

	# IAuthenticator

	def identify(self):
		if 'samlCKANuser' in session:
			g.user = session['samlCKANuser']
			return

	def logout(self):
		if 'samlNameId' in session:
			for key in saml.saml_details:
				del session[key]

	# IBlueprint
	def get_blueprint(self):
		return saml.saml

	# IClick
	def get_commands(self):
		return get_commnads()
