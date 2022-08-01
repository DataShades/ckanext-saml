import pytest

import ckan.model as model
from ckanext.saml.model import User

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestUser:
    def test_relationship(self, user):
        assert model.User.get(user["id"]).saml2_user is None

        su = User(id=user["id"], name_id="test")
        model.Session.add(su)
        model.Session.commit()

        assert su.user.name == user["name"]
        assert su.user.saml2_user == su

    def test_saml_user_use_cascade_remove(self, user):
        su = User(id=user["id"], name_id="test")
        model.Session.add(su)
        model.Session.commit()

        model.Session.delete(model.User.get(user["id"]))
        model.Session.commit()

        stored = model.Session.query(User).filter_by(id=su.id).one_or_none()
        assert stored is None

    def test_attributes(self, user):
        su = User(id=user["id"], name_id="test")
        model.Session.add(su)
        model.Session.commit()

        assert su.attributes == {}

        su.attributes = {"id": "test"}
        model.Session.commit()

        su = model.Session.query(User).filter_by(id=su.id).one()

        assert su.attributes == {"id": "test"}
