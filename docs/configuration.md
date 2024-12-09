# Configuration

Before start configuring, make sure that the config setting 
``ckan.saml_custom_base_path`` is set if your config file is not stored at
``/etc/ckan/default/saml`` directory.

Copy the ``saml`` folder from ``ckanext-saml`` into the directory where your 
CKAN config file is placed:

```
cp -R saml_example/saml YOUR_CONFIG_DIRECTORY/saml
```

Open the ``settings.json`` file that is in your copied ``saml`` folder in order 
to modify it.

You can also set them in the CKAN configuration file (e.g. ckan.ini or 
production.ini) using with prefix ``ckanext.saml.settings.substitution`` 
or using the admin configuration page.


## Configure main settings file

The main sections that should be updated within the file are``sp`` and ``idp``.

### SP modifications (CKAN):

1. Modify ``entityId`` with the domain name of your portal.

2. Modify ``url`` in ``assertionConsumerService`` with the domain name of your
   portal plus adding ``/saml/`` at the end. This is the URL where IdP will
   send back the reponse with User Data. Make sure the the slash is present in
   the end of the URL.

### IdP modifications

1. Modify ``entityId`` by filling it with the ``entityID`` that should be 
present in the ``idp_metadata.xml`` file (name of the file can be different) 
that is been sent to you by the IdP.

2. Modify ``url`` in ``singleSignOnService``. You can find this ``url`` in 
``idp_metadata.xml`` at ``SingleSignOnService`` section, it should have 
``Location`` attribute where the url is specified.

3. Modify ``x509cert`` by filling it with the ``X509Certificate`` that should be 
present in ``idp_metadata.xml``. Make sure this set as a **single line string**.

**Note**:  ``singleLogoutService`` is not implemented.


### Other modifications

``advanced_settings.json`` is used for additional configurations such as
security.  It also needed to modify the ``contactPerson`` and ``organization``
sections in it if your are going to provide your SP data to your IdP.

After updating all mentioned values in ``settings.json``, at
``DOMAIN_NAME/saml/metadata URL`` you can find the ``sp.xml`` generated, which
you can provide to the IdP for configuration on their side.

The main infomation that is needed for the IdP is the
``AssertionConsumerService``(ACS) which should be set on their APP for
SAML. ``AssertionConsumerService`` should match to what you have in your
settings.json and IdP APP, otherwise errors might appear.


## Configuration options

There is a number of configuration options available for the extension. You can 
set them in the CKAN configuration file (e.g. ckan.ini or production.ini).


### Config SSO path

**`ckanext.saml.sso_path`** [__optional__]

Set ``path`` to single sign-on.

**Type**: `str`

**Default**: `/sso/post`

-----

### Config SLO path

**`ckanext.saml.slo_path`** [__optional__]

Set ``path`` to single logout.

**Type**: `str`

**Default**: `/slo/post`

-----

### Config static host

**`ckanext.saml.static_host`** [__optional__]

Set the name of static host for SSO.

**Type**: `str`

**Default**: `None`

-----

### IdP metadata url 

**`ckanext.saml.metadata.url`** [__optional__]

Set the URL to IdP remote metadata.

**Type**: `str`

**Default**: `None`

-----

### Login button text

**`ckanext.saml.login_button_text`** [__optional__]

Provides an ability to customize login button text.

**Legacy**: `ckan.saml_login_button_text`

**Type**: `str`

**Default**: `SAML Login`

-----

### Mapper filename

**`ckan.saml_custom_attr_map`** [__optional__]

Used to modify mapper filename.

**Type**: `str`

**Default**: `mapper.py`

-----

### NameID as an email

**`ckan.saml_use_nameid_as_email`** [__optional__]

Set to ``true`` if you want to use NameID as an email for the User in order not 
to claim it additionally from the IdP.

**Type**: `bool`

**Default**: `false`

-----

### Path to error TPL

**`ckanext.saml.error_template`** [__optional__]

Set ``path`` to custom template for errors rendering.

**Type**: `str`

**Default**: `None`

-----

### Path to SAML config files

**`ckanext.saml.metadata.base_path`** [__optional__]

Provides custom path where saml settings files/folders will be searched.

**Legacy**: `ckan.saml_custom_base_path`

**Type**: `str`

**Default**: `/etc/ckan/default/saml`

-----

### Reactivate deleted account

**`ckanext.saml.reactivate_deleted_account`** [__optional__]

Change the state of a `deleted` account status to `active`.

**Type**: `bool`

**Default**: `false`

-----

### RelayState path

**`ckan.saml_relaystate`** [__optional__]

Set a custom RelayState ``path``.

**Type**: `str`

**Default**: `None`

-----

### Session TTL

**`ckanext.saml.session.ttl`** [__optional__]

Set the time a user can remain idle before the session is terminated and the 
user must log in again.

**Type**: `str`

**Default**: `30 * 24 * 3600`

-----

### Use HTTPS

**`ckan.saml_use_https`** [__optional__]

Used to send data while **https**, set ``on`` to enable it.

**Options**: `on`, `off`

**Type**: `bool`

**Default**: `off`

-----

### Using ``ckan.root_path``

**`ckan.saml_use_root_path`** [__optional__]

This needs to be set to ``true`` if you run your portal using the 
``ckan.root_path``.

**Type**: `bool`

**Default**: `false`

-----

### Use dynamic

**`ckanext.saml.settings.dynamic`** [__optional__]

Use dynamic Single Sign-On (SSO) URLs rather than pre-defined static SSO URLs.

**Type**: `bool`

**Default**: `false`

-----

### Use remote IdP

**`ckanext.saml.metadata.remote_idp`** [__optional__]

Use remote identity provider.

**Type**: `bool`

**Default**: `false`

-----

### Use forwarded host

**`ckanext.saml.use_forwarded_host`** [__optional__]

Use HTTP_X_FORWARDED_HOST when there is a proxy (or multiple proxies) between 
the browser and your server.

**Type**: `bool`

**Default**: `false`

-----

### Use unconditional login

**`ckanext.saml.unconditional_login`** [__optional__]

Use unconditional login for single sign-on.

**Type**: `bool`

**Default**: `false`

-----


## SP metadata

As mentioned above, you can find SP metadata at ``DOMAIN_NAME/saml/metadata
URL`` after configuring ``advanced_settings.json``.  This **URL** is accessible
only to ``sysadmins`` and presented in **XML** format.  Additional tab on
``/ckan-admin/`` is added, that leads to this page.


## Data encryption

In order to encrypt the coming data from the IdP use ``advanced_settings.json``
file. In ``security`` section, you can enable encryption for NameId and all
other data that will be returned to the SP.

If you enable one of
``authnRequestsSigned``,``logoutRequestSigned``,``logoutResponseSigned``,
``wantAssertionsEncrypted``, ``wantNameIdEncrypted`` (you can find description 
of each option [here](https://github.com/onelogin/python3-saml#how-it-works)), 
you will have to create [x509 certificate](https://en.wikipedia.org/wiki/X.509) 
in you SP. Cerificate should be created in ``certs`` folder, files should be 
named as ``sp.crt`` and ``sp.key`` (private key). After creating it, your 
``sp.xml`` will show you public key ``ds:X509Certificate`` that should be 
delivered to your IdP in order to configure encryption.


## Extras

ckanext-saml has interface ``ICKANSAML`` which has two hooks that can be used
for User data modificaiton and Organization memberships logic while login.

- ``after_mapping`` - Used after Users data is being mapped, but before the
User is being created.

- ``roles_and_organizations`` - Used for adding custom logic for Organization
membership that is going to be applied to the User. There is no default logic
for this, so should be added in your custom extension using this hook.
