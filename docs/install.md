# Installation

## Requirements

``ckanext-saml`` uses ``python3-saml`` library in order to make requests to the
IdP and return responses from it. Github repository can be found
[here](https://github.com/onelogin/python3-saml). There you can also find
examples of fields that can be used in ``settings.json`` and
``advanced_settings.json``.

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | no            |
| 2.10+           | yes           |


## Installation


- Install the extension from ``PyPI``:

```
pip install ckanext-saml 
```

- Add ``saml`` to the ``ckan.plugins`` setting in your CKAN configuration file (e.g. `ckan.ini` or `production.ini`):

```
ckan.plugins = ... saml ...
```

- Initialize a new table (if you previously used [ckanext-saml2] (https://github.com/datashades/ckanext-saml2), you can skip this step or make sure that you have saml2_user table in your DB):

```
ckan db upgrade -p saml
```

## Dependencies

The extension requires the following libraries to be installed and enabled:

1. ``python`` => 3.7
2. ``python3-saml``: SAML Python3 toolkit.
3. ``xmlsec``: Python bindings for the XML Security Library.
4. ``lxml``: Python bindings for the libxml2 and libxslt libraries.
5. ``isodate``: An ISO 8601 date/time/duration parser and formatter
