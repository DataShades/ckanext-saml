# ckanext-saml

This extension adds an ability to login from other source (known as
[IdP](https://en.wikipedia.org/wiki/Identity_provider_(SAML))) using
[SAML2](https://en.wikipedia.org/wiki/SAML_2.0) standard. Your instance is
presented as the [SP](https://en.wikipedia.org/wiki/Service_provider_(SAML)).

See the [documentation](https://datashades.github.io/ckanext-saml/) for more 
information.

## Quick start

- Install it with `PyPi`: 

    ```pip install ckanext-saml```

- Add `saml` to the list of plugins in your CKAN config (`ckan.plugins = saml`)

Configure the extension according to [documentation](https://datashades.github.io/ckanext-saml/).


## Developer installation

To install `ckanext-saml` for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/DataShades/ckanext-saml.git
    cd ckanext-saml
    pip install -e .

## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Building the documentation

We are using `mkdocs` to build the documentation. To build and deploy the 
documentation, do:

    mkdocs build && mkdocs gh-deploy

If you're working on the documentation, you can run the following command to 
start a live-reloading server without gathering the chart types fields data. It 
will speed up the process significantly, as we won't need to wait for the
CKAN initialization:

    mkdocs serve -a 127.0.0.1:8001

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
