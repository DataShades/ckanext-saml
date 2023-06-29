# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.


### [1.0.0](https://github.com/DataShades/ckanext-saml/compare/v0.3.1...v1.0.0) (2023-06-20)
#### ⚠ BREAKING CHANGES
* drop support Python lower than 3.8 (Python 3.7 secury support EOL - 27 Jun 2023)
* drop support CKAN lower than 2.10.0
* drop `advanced_settings.json` and `mapping.py` support.
    * Use `settings.json` for a static SAML settings and place here settings you've used in `advanced_settings.json`
      Or use `ckanext.saml.settings.` dynamic config options to declare SAML settings
    * Use `ckanext.saml.mapping.`to declare SAML attribute mapping.
* If you are using dynamic config, instead of creating a `certs` folder, you could use respective config options, e.g `x509cert`, `privateKey`, `x509certNew` for `sp` and `idp` configuration.
* Config option changes:
    * `ckan.saml_use_https` changed to `ckanext.saml.use_https`
    * `ckanext.saml.use_https` now must be `True` or `False`
    * `ckan.saml_use_nameid_as_email` changed to `ckanext.saml.use_nameid_as_email`
    * `ckan.saml_login_button_text` legacy option dropped. Use `ckanext.saml.login_button_text` instead
    * `ckan.saml_custom_base_path` legacy option dropped. Use `ckanext.saml.metadata.base_path` instead
### [0.3.1](https://github.com/DataShades/ckanext-saml/compare/v0.3.0...v0.3.1) (2023-04-24)


### Bug Fixes

* add csrf_token to user form ([05b0048](https://github.com/DataShades/ckanext-saml/commit/05b0048b91e96560ef419fc902402897da65979a))

## [0.3.0](https://github.com/DataShades/ckanext-saml/compare/v0.2.1...v0.3.0) (2023-04-03)


### ⚠ BREAKING CHANGES

* CKAN v2.10 support

### Features

* CKAN v2.10 support ([6f0fb3d](https://github.com/DataShades/ckanext-saml/commit/6f0fb3d1a0a07eb842e24d9cae78d8561d8f5084))

### [0.2.1](https://github.com/DataShades/ckanext-saml/compare/v0.2.0...v0.2.1) (2023-02-02)


### Bug Fixes

* treat `ckan.saml_use_nameid_as_email` as bool ([282cbf1](https://github.com/DataShades/ckanext-saml/commit/282cbf19430bd1873ec15fddfa7f9ffe1d8197e5))

## [0.2.0](https://github.com/DataShades/ckanext-saml/compare/v0.1.8...v0.2.0) (2022-11-10)


### Bug Fixes

* additional fixes for handling removed users ([421c948](https://github.com/DataShades/ckanext-saml/commit/421c948e4ae13132dd9ea5dcc95a960c271d043c))
* reactivate deleted accounts ([7ae982d](https://github.com/DataShades/ckanext-saml/commit/7ae982d91923696fbe96179ea00f850736235b14))
* use came_from ([1c768cc](https://github.com/DataShades/ckanext-saml/commit/1c768cc3b6ad95a703046170a69f835a25b8e182))

### [0.1.8](https://github.com/DataShades/ckanext-saml/compare/v0.1.7...v0.1.8) (2022-11-09)


### Features

* configurable redirect after login ([bfea66b](https://github.com/DataShades/ckanext-saml/commit/bfea66b17ed8398108ba1f82279f6a280063d18e))


### [0.1.7](https://github.com/DataShades/ckanext-saml/compare/v0.1.6...v0.1.7) (2022-11-09)


### Bug Fixes

* reactivate deleted accounts ([7ae982d](https://github.com/DataShades/ckanext-saml/commit/7ae982d91923696fbe96179ea00f850736235b14))


### [0.1.6](https://github.com/DataShades/ckanext-saml/compare/v0.1.5...v0.1.6) (2022-10-25)


### Features

* Allow login without sso URL parameter ([3d78e2a](https://github.com/DataShades/ckanext-saml/commit/3d78e2ad5391575c5d76d6c936b07ba639e2c3d9))

### [0.1.5](https://github.com/DataShades/ckanext-saml/compare/v0.1.4...v0.1.5) (2022-10-24)


### Bug Fixes

* standardize config option names ([108db0f](https://github.com/DataShades/ckanext-saml/commit/108db0f31e336d3b38986e5b2e26ca01553d5dc7))

### [0.1.4](https://github.com/DataShades/ckanext-saml/compare/v0.1.3...v0.1.4) (2022-10-15)


### Bug Fixes

* use name_id in logout request ([2ccd99e](https://github.com/DataShades/ckanext-saml/commit/2ccd99eb144ecddb5a6c8fe03fce9acfbd937f82))

### [0.1.3](https://github.com/DataShades/ckanext-saml/compare/v0.1.2...v0.1.3) (2022-10-13)


### Features

* configurable SSO and SLO routes ([a84e5a7](https://github.com/DataShades/ckanext-saml/commit/a84e5a7a11c12d5b66c28bb4b6eddaddea308fd2))

### [0.1.1](https://github.com/DataShades/ckanext-saml/compare/v0.1.0...v0.1.1) (2022-08-19)

### [0.1.1](https://github.com/DataShades/ckanext-saml/compare/v0.1.0...v0.1.1) (2022-08-19)
