"""Tests for SAML email ownership helpers used during SSO login."""

from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.tests import factories, helpers

from ckanext.saml.model.user import User
from ckanext.saml.views import saml as saml_views


@pytest.mark.usefixtures("clean_db")
class TestUsersByEmail:
    def test_find_prefers_unique_email_states_over_deleted(self, faker):
        email = faker.email()
        deleted = factories.User(email=email, state="deleted")
        active = factories.User(email=email)

        found = saml_views._find_user_by_email(email)

        assert found is not None
        assert found.id == active["id"]
        assert found.id != deleted["id"]

    def test_find_falls_back_to_deleted_when_no_owner(self, faker):
        email = faker.email()
        deleted = factories.User(email=email, state="deleted")

        found = saml_views._find_user_by_email(email)

        assert found is not None
        assert found.id == deleted["id"]
        assert found.state == "deleted"

    def test_find_among_deleted_prefers_saml_bound_user(self, faker):
        email = faker.email()
        first = factories.User(email=email, state="deleted")
        second = factories.User(email=email, state="deleted")
        nameid = faker.uuid4()

        model.Session.add(
            User(id=second["id"], name_id=nameid, attributes={"email": [email]})
        )
        model.Session.commit()

        found = saml_views._find_user_by_email(email, nameid="unrelated-nameid")

        assert found is not None
        assert found.id == second["id"]
        assert found.id != first["id"]

    def test_find_among_deleted_prefers_exact_nameid(self, faker):
        email = faker.email()
        first = factories.User(email=email, state="deleted")
        second = factories.User(email=email, state="deleted")
        nameid = faker.uuid4()

        model.Session.add(
            User(id=first["id"], name_id=faker.uuid4(), attributes={"email": [email]})
        )
        model.Session.add(
            User(id=second["id"], name_id=nameid, attributes={"email": [email]})
        )
        model.Session.commit()

        found = saml_views._find_user_by_email(email, nameid=nameid)

        assert found is not None
        assert found.id == second["id"]

    def test_email_owner_conflict_for_deleted_user(self, faker):
        email = faker.email()
        deleted = factories.User(email=email, state="deleted")
        active = factories.User(email=email)

        conflict = saml_views._email_owner_conflict(email, deleted["id"])

        assert conflict is not None
        assert conflict.id == active["id"]

    def test_no_conflict_when_email_only_on_deleted_user(self, faker):
        email = faker.email()
        deleted = factories.User(email=email, state="deleted")

        assert saml_views._email_owner_conflict(email, deleted["id"]) is None

    def test_no_conflict_between_two_deleted_users(self, faker):
        """Deleted twins are not unique_email_states owners by default."""
        email = faker.email()
        first = factories.User(email=email, state="deleted")
        second = factories.User(email=email, state="deleted")

        assert saml_views._email_owner_conflict(email, first["id"]) is None
        assert saml_views._email_owner_conflict(email, second["id"]) is None

    def test_rebind_nameid_moves_binding_to_active_user(self, faker):
        email = faker.email()
        deleted = factories.User(email=email, state="deleted")
        active = factories.User(email=email)
        nameid = faker.uuid4()

        binding = User(id=deleted["id"], name_id=nameid, attributes={"email": [email]})
        model.Session.add(binding)
        model.Session.commit()

        active_obj = model.User.get(active["id"])
        assert active_obj is not None

        new_binding = saml_views._rebind_nameid(
            binding, active_obj, nameid, {"email": [email]}
        )
        model.Session.commit()

        assert new_binding.id == active["id"]
        assert new_binding.name_id == nameid
        assert model.Session.query(User).filter(User.id == deleted["id"]).first() is None
        assert model.Session.query(User).filter(User.name_id == nameid).one().id == active["id"]


@pytest.mark.usefixtures("clean_db")
@pytest.mark.ckan_config("ckanext.saml.reactivate_deleted_account", "true")
class TestRestorePathViaHelpers:
    def test_deleted_without_conflict_can_be_reactivated(self, faker):
        email = faker.email()
        user = factories.User(email=email, state="deleted")

        assert saml_views._email_owner_conflict(email, user["id"]) is None

        helpers.call_action(
            "user_update",
            id=user["id"],
            name=user["name"],
            email=email,
            state="active",
        )
        restored = model.User.get(user["id"])
        assert restored is not None
        assert restored.state == "active"

    def test_deleted_with_conflict_cannot_be_reactivated(self, faker):
        email = faker.email()
        deleted = factories.User(email=email, state="deleted")
        factories.User(email=email)

        with pytest.raises(tk.ValidationError):
            helpers.call_action(
                "user_update",
                id=deleted["id"],
                name=deleted["name"],
                email=email,
                state="active",
            )
