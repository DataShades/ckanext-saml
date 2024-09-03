# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.3.4](https://github.com/DataShades/ckanext-saml/releases/tag/v0.3.4) - 2024-09-03

<small>[Compare with v0.3.3](https://github.com/DataShades/ckanext-saml/compare/v0.3.3...v0.3.4)</small>

### Bug Fixes

- do not duplicate dynamic views ([d53ce75](https://github.com/DataShades/ckanext-saml/commit/d53ce75f086e159ddaab5c9f951b1977951551c1) by Sergey Motornyuk).

## [v0.3.3](https://github.com/DataShades/ckanext-saml/releases/tag/v0.3.3) - 2024-04-18

<small>[Compare with v0.3.2](https://github.com/DataShades/ckanext-saml/compare/v0.3.2...v0.3.3)</small>

### Features

- remove overrides for user edit form ([3205480](https://github.com/DataShades/ckanext-saml/commit/3205480bc001a8045825361834537954b8495791) by Sergey Motornyuk).

## [v0.3.2](https://github.com/DataShades/ckanext-saml/releases/tag/v0.3.2) - 2023-09-07

<small>[Compare with v0.3.1](https://github.com/DataShades/ckanext-saml/compare/v0.3.1...v0.3.2)</small>

### Features

- read remote metadata from file ([b912844](https://github.com/DataShades/ckanext-saml/commit/b9128446c2e713adb7053a2c056628efebb68940) by Sergey Motornyuk).
- saml_idp_refresh accepts `url` parameter ([d66989b](https://github.com/DataShades/ckanext-saml/commit/d66989b9d9a71c07b7ea2260be0ceea86b65fb2d) by Sergey Motornyuk).

### Bug Fixes

- automatically call idp_refresh when it is not available in cache ([3cc8291](https://github.com/DataShades/ckanext-saml/commit/3cc82912414403432f9e7a7a97f9928f421474ff) by Sergey Motornyuk).

## [v0.3.1](https://github.com/DataShades/ckanext-saml/releases/tag/v0.3.1) - 2023-04-24

<small>[Compare with v0.3.0](https://github.com/DataShades/ckanext-saml/compare/v0.3.0...v0.3.1)</small>

### Bug Fixes

- add csrf_token to user form ([05b0048](https://github.com/DataShades/ckanext-saml/commit/05b0048b91e96560ef419fc902402897da65979a) by Sergey Motornyuk).

## [v0.3.0](https://github.com/DataShades/ckanext-saml/releases/tag/v0.3.0) - 2023-04-03

<small>[Compare with v0.2.1](https://github.com/DataShades/ckanext-saml/compare/v0.2.1...v0.3.0)</small>

### Features

- CKAN v2.10 support ([6f0fb3d](https://github.com/DataShades/ckanext-saml/commit/6f0fb3d1a0a07eb842e24d9cae78d8561d8f5084) by Sergey Motornyuk).

## [v0.2.1](https://github.com/DataShades/ckanext-saml/releases/tag/v0.2.1) - 2023-02-02

<small>[Compare with v0.2.0](https://github.com/DataShades/ckanext-saml/compare/v0.2.0...v0.2.1)</small>

### Bug Fixes

- treat `ckan.saml_use_nameid_as_email` as bool ([282cbf1](https://github.com/DataShades/ckanext-saml/commit/282cbf19430bd1873ec15fddfa7f9ffe1d8197e5) by Sergey Motornyuk).

## [v0.2.0](https://github.com/DataShades/ckanext-saml/releases/tag/v0.2.0) - 2022-11-10

<small>[Compare with v0.1.8](https://github.com/DataShades/ckanext-saml/compare/v0.1.8...v0.2.0)</small>

### Bug Fixes

- additional fixes for handling removed users ([421c948](https://github.com/DataShades/ckanext-saml/commit/421c948e4ae13132dd9ea5dcc95a960c271d043c) by Sergey Motornyuk).
- use came_from ([1c768cc](https://github.com/DataShades/ckanext-saml/commit/1c768cc3b6ad95a703046170a69f835a25b8e182) by Sergey Motornyuk).
- reactivate deleted accounts ([7ae982d](https://github.com/DataShades/ckanext-saml/commit/7ae982d91923696fbe96179ea00f850736235b14) by Sergey Motornyuk).

## [v0.1.8](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.8) - 2022-11-09

<small>[Compare with v0.1.7](https://github.com/DataShades/ckanext-saml/compare/v0.1.7...v0.1.8)</small>

## [v0.1.7](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.7) - 2022-11-09

<small>[Compare with v0.1.6](https://github.com/DataShades/ckanext-saml/compare/v0.1.6...v0.1.7)</small>

### Bug Fixes

- configurable redirect after login ([bfea66b](https://github.com/DataShades/ckanext-saml/commit/bfea66b17ed8398108ba1f82279f6a280063d18e) by Sergey Motornyuk).

## [v0.1.6](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.6) - 2022-10-25

<small>[Compare with v0.1.5](https://github.com/DataShades/ckanext-saml/compare/v0.1.5...v0.1.6)</small>

### Features

- Allow login without sso URL parameter ([3d78e2a](https://github.com/DataShades/ckanext-saml/commit/3d78e2ad5391575c5d76d6c936b07ba639e2c3d9) by Sergey Motornyuk).

## [v0.1.5](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.5) - 2022-10-24

<small>[Compare with v0.1.4](https://github.com/DataShades/ckanext-saml/compare/v0.1.4...v0.1.5)</small>

### Bug Fixes

- standardize config option names ([108db0f](https://github.com/DataShades/ckanext-saml/commit/108db0f31e336d3b38986e5b2e26ca01553d5dc7) by Sergey Motornyuk).

## [v0.1.4](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.4) - 2022-10-15

<small>[Compare with v0.1.3](https://github.com/DataShades/ckanext-saml/compare/v0.1.3...v0.1.4)</small>

### Bug Fixes

- use name_id in logout request ([2ccd99e](https://github.com/DataShades/ckanext-saml/commit/2ccd99eb144ecddb5a6c8fe03fce9acfbd937f82) by Sergey Motornyuk).

## [v0.1.3](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.3) - 2022-10-13

<small>[Compare with v0.1.2](https://github.com/DataShades/ckanext-saml/compare/v0.1.2...v0.1.3)</small>

### Features

- configurable SSO and SLO routes ([a84e5a7](https://github.com/DataShades/ckanext-saml/commit/a84e5a7a11c12d5b66c28bb4b6eddaddea308fd2) by Sergey Motornyuk).

## [v0.1.2](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.2) - 2022-10-04

<small>[Compare with v0.1.1](https://github.com/DataShades/ckanext-saml/compare/v0.1.1...v0.1.2)</small>

### Bug Fixes

- include migrations into package ([ac11cc2](https://github.com/DataShades/ckanext-saml/commit/ac11cc2509b9dcf116c248dc7466253375615a8e) by Sergey Motornyuk).

## [v0.1.1](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.1) - 2022-08-19

<small>[Compare with v0.1.0](https://github.com/DataShades/ckanext-saml/compare/v0.1.0...v0.1.1)</small>

## [v0.1.0](https://github.com/DataShades/ckanext-saml/releases/tag/v0.1.0) - 2022-07-26

<small>[Compare with first commit](https://github.com/DataShades/ckanext-saml/compare/8dbcd271f149884fd7c082dda98897a95587d601...v0.1.0)</small>

