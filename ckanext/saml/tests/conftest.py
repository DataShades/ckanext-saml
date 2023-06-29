import os

import pytest
from onelogin.saml2.idp_metadata_parser import (
    OneLogin_Saml2_IdPMetadataParser as Parser,
)
from pytest_factoryboy import register

from ckan.tests import factories


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("saml")


@register
class UserFactory(factories.User):
    pass


@pytest.fixture
def idp_metadata():
    here = os.path.dirname(__file__)

    with open(os.path.join(here, "data", "metadata_example.xml")) as f:
        return Parser.parse(f.read())["idp"]
