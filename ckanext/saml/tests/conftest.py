import pytest
from ckan.tests import factories
from pytest_factoryboy import register


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("saml")


@register
class UserFactory(factories.User):
    pass
