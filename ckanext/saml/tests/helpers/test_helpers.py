import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.saml import config
from ckanext.saml.model.user import User


@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_is_saml_user(user):
    assert not tk.h.saml_is_saml_user(user["name"])

    model.Session.add(User(id=user["id"], name_id="test"))
    model.Session.commit()

    assert tk.h.saml_is_saml_user(user["name"])


@pytest.mark.usefixtures("with_plugins")
def test_login_button_text(ckan_config, monkeypatch, faker):
    assert tk.h.saml_get_login_button_text() == config.DEFAULT_LOGIN_TEXT

    label = faker.sentence()
    monkeypatch.setitem(ckan_config, config.CONFIG_LOGIN_TEXT, label)
    assert tk.h.saml_get_login_button_text() == label
