from ckan.common import config


def get_helpers():
	return {
		'get_login_button_text': get_login_button_text,
		'get_saml_folter_path': get_saml_folter_path,
		'get_attr_mapper': get_attr_mapper,
	}


def get_login_button_text():
	text = config.get('ckan.saml_login_button_text', 'SAML Login')
	return text


def get_saml_folter_path():
	path = config.get('ckan.saml_custom_base_path', '/etc/ckan/default/saml')
	return path


def get_attr_mapper():
	import importlib.util
	spec = importlib.util.spec_from_file_location(
		"module.name", get_saml_folter_path() + '/attributemaps/' +
		config.get('ckan.saml_custom_attr_map', 'mapper.py'))
	
	mapper = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mapper)
	
	return mapper.MAP