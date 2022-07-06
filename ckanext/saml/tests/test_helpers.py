import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.saml.model.saml2_user import SAML2User

@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_is_saml_user(user):
    assert not tk.h.saml_is_saml_user(user["name"])

    model.Session.add(SAML2User(id=user["id"], name_id="test"))
    model.Session.commit()

    assert tk.h.saml_is_saml_user(user["name"])
