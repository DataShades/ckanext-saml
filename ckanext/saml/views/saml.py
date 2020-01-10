from flask import Blueprint, make_response, session
import ckan.lib.base as base
from ckan.common import request, g, config
import ckan.lib.helpers as h
import ckan.logic as logic
from ckan.logic.action.create import _get_random_username_from_email
import ckan.model as model
from ckanext.saml.model.saml2_user import SAML2User
import ckanext.saml.helpers as saml_helpers

import uuid
from urllib.parse import urlparse
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

custom_folder =  saml_helpers.get_saml_folter_path()
attr_mapper = saml_helpers.get_attr_mapper()

saml_details = [
	'samlUserdata',
	'samlNameIdFormat',
	'samlNameId',
	'samlCKANuser'
]

saml = Blueprint(u'saml', __name__, url_prefix=u'/saml',)


def prepare_from_flask_request():
	url_data = urlparse(request.url)
	return {
		'http_host': request.host,
		'server_port': url_data.port,
		'script_name': request.path,
		'get_data': request.args.copy(),
		'post_data': request.form.copy()
	}

@saml.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		req = prepare_from_flask_request()
		auth = OneLogin_Saml2_Auth(req, custom_base_path=custom_folder)
		request_id = None

		auth.process_response(request_id=request_id)
		errors = auth.get_errors()
		if len(errors) == 0:
			nameid = auth.get_nameid()

			if not nameid:
				return h.redirect_to('user.login')
			else:
				saml_user = model.Session.query(SAML2User)\
					.filter(SAML2User.name_id == nameid).first()

				if not saml_user:
					mapped_data = {}
					for key, value in attr_mapper.items():
						field = auth.get_attribute(value)
						if field:
							mapped_data[key] = field

					user_dict = {
						'name': _get_random_username_from_email(mapped_data['email'][0]),
						'email': mapped_data['email'][0],
						'id': str(uuid.uuid4()),
						'password': str(uuid.uuid4()),
					}
					try:	
						user = logic.get_action('user_create')(
							{'ignore_auth': True}, user_dict)
						if user:
							model.Session.add(SAML2User(id=user['id'],
														name_id=nameid))
							model.Session.commit()
					except Exception as e:
						print(e)
						return h.redirect_to('user.login')
				else:
					user = model.User.get(saml_user.id)
			
			session['samlUserdata'] = auth.get_attributes()
			session['samlNameIdFormat'] = auth.get_nameid_format()
			session['samlNameId'] = nameid
			session['samlCKANuser'] = user.name
			
			g.user = user.name
			return h.redirect_to('dashboard.index')
		# return 'OK'
	return h.redirect_to('/saml/login')

def metadata():
	req = prepare_from_flask_request()
	auth = OneLogin_Saml2_Auth(req, custom_base_path=custom_folder)
	
	settings = auth.get_settings()
	metadata = settings.get_sp_metadata()
	errors = settings.validate_metadata(metadata)
	
	if len(errors) == 0:
		resp = make_response(metadata, 200)
		resp.headers['Content-Type'] = 'text/xml'
	else:
		resp = make_response(', '.join(errors), 500)
	return resp

def saml_login():
	req = prepare_from_flask_request()
	auth = OneLogin_Saml2_Auth(req, custom_base_path=custom_folder)
	
	if 'sso' in request.args and request.args['sso'] == 'true':
		return h.redirect_to(auth.login())

	return h.redirect_to('user.login')


util_rules = [
	(u'metadata', metadata),
	(u'login', saml_login),
]

for rule, view_func in util_rules:
	saml.add_url_rule(rule, view_func=view_func)

