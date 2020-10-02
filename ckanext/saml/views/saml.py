import re
import logging
import uuid
from flask import Blueprint, make_response, session
from urllib.parse import urlparse

import ckan.lib.base as base
from ckan.common import request, g, config, _, asbool
import ckan.lib.helpers as h
import ckan.logic as logic
from ckan.logic.action.create import _get_random_username_from_email
import ckan.model as model
from ckanext.saml.model.saml2_user import SAML2User
import ckanext.saml.helpers as saml_helpers

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

log = logging.getLogger(__name__)
custom_folder =  saml_helpers.get_saml_folter_path()
attr_mapper = saml_helpers.get_attr_mapper()
use_https = config.get('ckan.saml_use_https', 'off')

saml_details = [
    'samlUserdata',
    'samlNameIdFormat',
    'samlNameId',
    'samlCKANuser'
]

saml = Blueprint('saml', __name__, url_prefix='/saml',)


def prepare_from_flask_request():
    url_data = urlparse(request.url)

    req_path = request.path
    if asbool(config.get('ckan.saml_use_root_path', False)):
        # FIX FOR ROOT_PATH REMOVED IN request.path
        root_path = config.get('ckan.root_path', None)
        if root_path:
            root_path = re.sub('/{{LANG}}', '', root_path)
            req_path = root_path + req_path 

    return {
        'https': use_https,
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': req_path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }

@saml.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        log.info('Got responsne from the IdP. Start analyzing it.')
        req = prepare_from_flask_request()
        auth = OneLogin_Saml2_Auth(req, custom_base_path=custom_folder)
        request_id = None
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        if len(errors) == 0:
            log.info('User succesfully logged in the IdP. Extracting NAMEID.')
            
            nameid = auth.get_nameid()

            if not nameid:
                log.error(
                    (
                        'Something went wrong, no NAMEID was found, '
                        'redirecting back to to login page.'
                    )
                )
                return h.redirect_to(h.url_for('user.login'))
            else:
                log.info('NAMEID: {0}'.format(nameid))
                
                saml_user = model.Session.query(SAML2User)\
                    .filter(SAML2User.name_id == nameid).first()

                if not saml_user:
                    log.info(
                        (
                            'No User with NAMEID \'{0}\' was found. '
                            'Creating one.'.format(nameid)
                        )
                    )
                    mapped_data = {}

                    log.info('Extracting data from IdP response.')
                    if attr_mapper:
                        for key, value in attr_mapper.items():
                            field = auth.get_attribute(value)
                            if field:
                                mapped_data[key] = field

                        user_dict = {
                            'name': _get_random_username_from_email(
                                mapped_data['email'][0]),
                            'email': mapped_data['email'][0],
                            'id': str(uuid.uuid4()),
                            'password': str(uuid.uuid4()),
                        }
                        try:
                            log.info(
                                ('Trying to create User with name \'{0}\''.format(
                                user_dict['name']
                                ))
                            )
                            new_user = logic.get_action('user_create')(
                                {'ignore_auth': True}, user_dict)
                            if new_user:
                                model.Session.add(SAML2User(
                                    id=new_user['id'],
                                    name_id=nameid)
                                )
                                model.Session.commit()
                                log.info(
                                    'User succesfully created. Authorizing...')
                            user = model.User.get(new_user['name'])
                        except Exception as e:
                            print(e)
                            return h.redirect_to(h.url_for('user.login'))
                    else:
                        log.error('User mapping is empty, please set "ckan.saml_custom_attr_map" param in config.')
                        return h.redirect_to(h.url_for('user.login'))
                else:
                    user = model.User.get(saml_user.id)
                    log.info('User already created. Authorizing...')
            
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameIdFormat'] = auth.get_nameid_format()
            session['samlNameId'] = nameid
            session['samlCKANuser'] = user.name
            
            g.user = user.name
            
            return h.redirect_to(h.url_for('dashboard.index'))
        else:
            h.flash_error('SAML: Errors appeared while logging process.')
            log.error('{}'.format(errors))
    
    return h.redirect_to(h.url_for('saml.saml_login'))

def metadata():
    try:
        context = dict(model=model, user=g.user, auth_user_obj=g.userobj)
        logic.check_access(u'sysadmin', context)
    except logic.NotAuthorized:
        base.abort(403, _(u'Need to be system administrator to administer'))

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
    try:
        auth = OneLogin_Saml2_Auth(req, custom_base_path=custom_folder)
        if 'sso' in request.args and request.args['sso'].lower() == 'true':
            log.info('Redirect to SAML IdP.')
            return h.redirect_to(auth.login())
        else:
            log.warning(
                (
                    'No arguments been provided in this URL. If you want to make '
                    'auth request to SAML IdP point, please provide \'?sso=true\' at '
                    'the end of the URL.'
                )
            )
    except Exception as e:
        h.flash_error('SAML: An issue appeared while validating settings file.')
        log.error('{}'.format(e))

    return h.redirect_to(h.url_for('user.login'))


util_rules = [
    ('metadata', metadata),
    ('login', saml_login),
]

for rule, view_func in util_rules:
    saml.add_url_rule(rule, view_func=view_func)

