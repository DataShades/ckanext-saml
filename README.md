# ckanext-saml
Adds an ability to login from other source (known as [IdP](https://en.wikipedia.org/wiki/Identity_provider_(SAML))) using [SAML2](https://en.wikipedia.org/wiki/SAML_2.0) standard. Your instance is presented as the [SP](https://en.wikipedia.org/wiki/Service_provider_(SAML)).

**This extension works for python 3.6+**

#### Requirements ####
``ckanext-saml`` uses ``python3-saml`` library in order to make requests to the IdP and return responses from it. Github repository can be found [here](https://github.com/onelogin/python3-saml).

#### Installation ####
**Before start the installation make sure that CKAN virtual environment is enabled!**

To install ``ckanext-saml``:
1. Download or clone the [repository](https://github.com/datashades/ckanext-saml) into your CKAN installation.
2. Go to extension directory and run command:
		python setup.py develop
3.  Install requirements:
		pip install -r requirements.txt
4. Add ``saml`` to the ``ckan.plugins`` setting in your CKAN config file (by default the config file is located at  ``/etc/ckan/default/production.ini``).
5. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:
		sudo service apache2 reload

#### Config settings ####
``ckan.saml_login_button_text`` - Provides an ability to customize login button text. By **default** set to ``SAML Login``.

``ckan.saml_custom_base_path`` - Provides custom path where saml files/folders will be searched. By **default**  set to ``/etc/ckan/default/saml``.

``ckan.saml_custom_attr_map`` -  Used to modify mapper filename. By **default** searches for ``mapper.py``.

#### Configuration ####
Before start configuring, make sure that the config setting ``ckan.saml_custom_base_path`` is set if your config file is not stored at ``/etc/ckan/default`` directory.

Copy the ``saml`` folder from ``ckanext-saml`` into the directory where your CKAN config file is placed:

		cp -R saml_example/saml YOUR_CONFIG_DIRECTORY/saml

Open the ``settings.json`` file that is in your copied ``saml`` folder in order to modify it.

**Configure main settings file**
The main sections that should be updated within the file are ``sp`` and ``idp``

In order to make it more clear lets start from configuring ``idp``:
1. Modify ``entityId`` by filling it with the ``entityID`` that should be present in the ``idp_metadata.xml`` file (name of the file can be different) that is been sent to you by the IdP.
2. Modify ``url`` in  ``singleSignOnService``. You can find this ``url`` in ``idp_metadata.xml`` at ``SingleSignOnService`` section, it should have ``Location`` attribute where the url is specified.
3. Modify ``x509cert`` by filling it with the`` X509Certificate`` that should be present in ``idp_metadata.xml``. Make sure the this set as a **single line string**.

**Note**:  ``singleLogoutService`` is not implemented.

Modifications for ``sp``:
1. Modify ``entityId`` with the domain name of your portal.
2. Modify ``url`` in ``assertionConsumerService`` with the domain name of your portal plus adding ``/saml/`` at the end. This is the URL where IdP will send back the reponse with User Data.

**Note**:  ``singleLogoutService`` is not implemented.

``advanced_settings.json`` is used for additional configurations such as security.  It also needed to modify the ``contactPerson`` and ``organization`` sections in it if your are going to provide your SP data to your IdP.
After compliting configuration in ``settings.json``, at ``DOMAIN_NAME/saml/metadata URL`` you can find the ``sp.xml`` generated, which you can provide to the IdP for configuration on their side.

The main infomation that is needed for the IdP is the ``AssertionConsumerService``(ACS) which is should be set on their APP for SAML. ``AssertionConsumerService`` should match to what you have in your settings.json and IdP APP, otherwise errors might appear.

#### SP Metadata file ####
As mentioned above, you can find SP metadata at ``DOMAIN_NAME/saml/metadata URL`` after configuring ``advanced_settings.json``.
This **URL** is accessible only to ``sysadmins`` and presented in **XML** format.
Additional tab on ``/ckan-admin/`` is added, that leads to this page.

#### Data encryption ####
In order to encrypt the coming data from the IdP use ``advanced_settings.json`` file. In ``security`` section, you can enable encryption for NAMEID and all other data that will be returned to the SP.
If you enable one of ``authnRequestsSigned``,``logoutRequestSigned``,``logoutResponseSigned``,``wantAssertionsEncrypted``, ``wantNameIdEncrypted`` (you can find description of earch option [here](https://github.com/onelogin/python3-saml#how-it-works)), you will have to create [x509 certificate](https://en.wikipedia.org/wiki/X.509) in you SP. Cerificate should be created in ``certs`` folder, files should be named as ``sp.crt`` and ``sp.key`` (private key). After creating it, your ``sp.xml`` will show you public key ``ds:X509Certificate`` that should be delivered to your IdP in order to configure encryption.