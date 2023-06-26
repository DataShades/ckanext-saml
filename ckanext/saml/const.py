DEFAULT_MAPPING = {
    "user_id": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
    "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
    "given_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
    "family_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
    "upn": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn",
    "groups": "http://schemas.xmlsoap.org/claims/Group",
}

MAPPING_PREFIX: str = "ckanext.saml.mapping."
SETTINGS_PREFIX: str = "ckanext.saml.settings."
