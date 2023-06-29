The `ckanext-saml` extensions adds an ability to login from other source (known as [IdP](https://en.wikipedia.org/wiki/Identity_provider_(SAML))) using [SAML2](https://en.wikipedia.org/wiki/SAML_2.0) standard. Your instance is presented as the [SP](https://en.wikipedia.org/wiki/Service_provider_(SAML)).

This extension uses ``python3-saml`` library in order to make requests to the IdP and return responses from it. Github repository can be found
[here](https://github.com/onelogin/python3-saml). There you can also find information about available settings.

#### Installation ####

To install ``ckanext-saml``:

1. Install additional packages (example is shown for CentOS):

		yum install python3-devel xmlsec1-devel libtool-ltdl-devel

1.  Install extension:

		pip install ckanext-saml

1. Add ``saml`` to the ``ckan.plugins`` setting in your CKAN config file.

1. Initialize new table.

		ckan db pending-migrations --apply

If error that mentioned below appears on CentOS, you might need to install
additional packages - ``yum install libxml2-devel xmlsec1-devel
xmlsec1-openssl-devel libtool-ltdl-devel``:

		import xmlsec
		SystemError: null argument to internal

#### Configuration ####

Since the CKAN portal itself is an SP, you don't need to configure it from our side (only if you really want to change something). There is a default configuration that can be retrieved using a CLI command. Type `ckan saml show-config` to get the current SAML configuration.

```
{
    "strict": "true",
    "debug": true,
    "sp": {
        "entityId": "http://127.0.0.1:5000",
        "assertionConsumerService": {
            "url": "http://127.0.0.1:5000/sso/post",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": "http://127.0.0.1:5000/slo/post",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
        "x509cert": "",
        "privateKey": "",
    },
    "idp": {
        "entityId": "<IDP ENTITY ID>",
        "singleSignOnService": {
            "url": "<LOGIN URL>",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "singleLogoutService": {
            "url": "<LOGOUT URL>",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": ""
    }
}
```
As you can see, there are multiple placeholder for an `idp` configuration. There are two ways to setup IdP properly. You could do it manually via CKAN configuration file, like that:
```
ckanext.saml.settings.idp.entityId = http://127.0.0.1:9001/simplesaml/saml2/idp/metadata.php
ckanext.saml.settings.idp.singleSignOnService.url = http://127.0.0.1:9001/simplesaml/saml2/idp/SSOService.php
ckanext.saml.settings.idp.singleLogoutService.url = http://127.0.0.1:9001/simplesaml/saml2/idp/SingleLogoutService.php
ckanext.saml.settings.idp.x509cert = <KEY>
```
Or setup it with URL to IdP metadata, like that:
```
ckanext.saml.idp_metadata_url = http://127.0.0.1:9001/simplesaml/saml2/idp/metadata.php
```
**Note**:  ``singleLogoutService`` for IdP is not implemented.

If you don't want to use dynamic settings or you have a complicated settings with arrays and objects,
you can use an old styled config file. Use `ckanext.saml.metadata.base_path` option and provide here a folder
with your SAML settings with `settings.json` file.

#### Config settings ####

- ``ckanext.saml.use_https`` - Used to send request with **https**, set ``true`` to
  enable it. By **default** is set to ``false`` and uses **http**.

- ``ckan.saml_use_nameid_as_email`` - Set to ``true`` if you want to use NameID
  as an email for the User in order not to claim it additionally from the
  IdP. Default is set to ``false``.

- ``ckanext.saml.login_button_text`` - Provides an ability to customize login
  button text. By **default** set to ``SAML Login``.

- ``ckanext.saml.use_root_path`` - This needs to be set to ``true`` if you run
  your portal using the ``ckan.root_path``. By **default** set to ``false``.

- ``ckanext.saml.relay_state`` - The destination that the user will be redirected
    to after they have completed the authentication process at the identity
    provider (IdP). By **default** it's either ``came_from`` or ``/dashboard``.

- ``ckanext.saml.error_template`` - Path to a template to render an SAML login error.
    The template will recieve `errors` variable with a list of error strings.
    By **default** it redirect you to login page with a flash_error if not provided.

- ``ckanext.saml.sso_path`` - Custom path for SSO. By **default** it's `/sso/post`.

- ``ckanext.saml.slo_path`` - Custom path for SLO. By **default** it's `/slo/post`.

- ``ckanext.saml.static_host`` - Use static host for a SAML request. By **default** it's None

- ``ckanext.saml.use_forwarded_host`` - Set it to `true` if you want to use forwarded
    host for a SAML request. By **default** it's `false`.

- ``ckanext.saml.unconditional_login`` - Set it to `true` if you want to allow unconditional
    login. By **default** it's `false`.

- ``ckanext.saml.reactivate_deleted_account`` - Set to `true` if you want to reactivate deleted
    accounts on SAML login. By **default** it's `false`.

- ``ckanext.saml.use_custom_mapper`` - Set to `true` if you want to use your custom mapper.
    Otherwise, the default mapping will be used.
    ```
    DEFAULT_MAPPING = {
        "user_id": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
        "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
        "given_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
        "family_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
        "upn": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn",
        "groups": "http://schemas.xmlsoap.org/claims/Group",
    }
    ```
    Example, how to provide a custom mapping:
    ```
    ckanext.saml.mapping.email = mail
    ckanext.saml.mapping.user_id = uid
    ```
    With those options, your attribute mapping will be next:
    ```
    {
        "email": "mail",
        "user_id": "uid"
    }
    ```
- ``ckanext.saml.idp_metadata_url`` - Set to fetch the IdP settings from a URL. By **default**
    it's None and IdP settings must be provided manually (either with `settings.json` or with
    dinamyc configuration)

- ``ckanext.saml.session.ttl`` - The amount of time in seconds before the remember cookie
    expires. By **default** it's 2592000

- ``ckanext.saml.metadata.base_path`` - A path to a folder with SAML settings (e.g. `settings.json`
    or `certs` folder). By **default** we are using dynamic settings.

#### SP Metadata file ####

To setup your SP on the IdP side you could either do it manually, providing required values, that you could get from the `ckan saml show-config` command, or  give a link to this URL `/saml/metadata` that will return the SP settings in `XML` format.
This **URL** is accessible only to ``sysadmins`` and could be also accessed via tab on a `ckan-admin` page.

#### Data encryption ####

In order to encrypt the coming data from the IdP you have two options:
- Use ``ckanext.saml.settings.security.`` dynamic config options.
    For example: `ckanext.saml.settings.security.wantNameIdEncrypted = true`.
- Set it withing your `settings.json` file

Using those options requires a certificate, that must be provided via dynamic settings or inside `certs` folder.

Check `python3-saml` github page to know more about settings.

### Interfaces ###

`ckanext-saml` has interface ``ICKANSAML`` which has two hooks that can be used for User data modificaiton and Organization memberships logic while login.

- ``after_mapping`` - Used after the user data is mapped but before the user is created.

- ``roles_and_organizations`` - Used to add custom organization membership logic
    to be applied to a user. There is no default logic for this, so you should
    add it to your own extension using this hook

### CLI ###

`ckanext-saml` has few CLI commands:
- `show-config` - show the current SAML configuration for IdP and SP
- `show-mapping` - show the current attribute mapping
