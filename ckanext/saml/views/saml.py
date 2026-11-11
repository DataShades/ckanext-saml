from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from flask import Blueprint, make_response, session
from sqlalchemy import func as sql_func

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.logic import functools
from ckan.logic.action.create import _get_random_username_from_email

from ckanext.saml import config, utils
from ckanext.saml.interfaces import ICKANSAML
from ckanext.saml.model.user import User

log = logging.getLogger(__name__)
use_nameid_as_email = tk.asbool(tk.config.get("ckan.saml_use_nameid_as_email", False))

saml_details = [
    "samlUserdata",
    "samlNameIdFormat",
    "samlNameId",
    "samlCKANuser",
]

saml = Blueprint("saml", __name__)


@functools.lru_cache(1)
def get_bp():
    saml.add_url_rule(config.slo_path(), view_func=post_logout)

    saml.add_url_rule(config.sso_path(), view_func=post_login, methods=["POST"])

    return saml


def post_logout():
    if "SAMLResponse" in tk.request.args:
        log.debug(
            "SAML2 Logout response: %s",
            utils.decode_saml_response(tk.request.args["SAMLResponse"]),
        )
    return tk.h.redirect_to("user.logout")


def post_login():
    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    request_id = None
    auth.process_response(request_id=request_id)
    errors = auth.get_errors()

    if errors:
        log.error("Cannot process IdP response: %s", errors)
        log.error("Last error reason: %s", auth.get_last_error_reason())

        error_tpl = config.error_template()
        if error_tpl:
            return tk.render(error_tpl, {"errors": errors})

        h.flash_error("Login failed.")
        return h.redirect_to(h.url_for("saml.saml_login"))

    log.debug("User succesfully logged in the IdP. Extracting NAMEID.")
    nameid = auth.get_nameid()

    if not nameid:
        log.error("Something went wrong, no NAMEID was found, redirecting back to to login page.")
        return h.redirect_to(h.url_for("user.login"))

    mapped_data = {}
    attr_mapper = tk.h.saml_attr_mapper()

    if not attr_mapper:
        log.error('User mapping is empty, please set "ckan.saml_custom_attr_map" param in config.')
        return h.redirect_to(h.url_for("user.login"))

    for key, value in attr_mapper.items():
        field = auth.get_attribute(value)
        if field:
            mapped_data[key] = field
    log.debug(f"NAMEID: {nameid}")

    for item in p.PluginImplementations(ICKANSAML):
        item.after_mapping(mapped_data, auth)
    log.debug("Client data: %s", attr_mapper)
    log.debug("Mapped data: %s", mapped_data)
    log.debug("If you are experiencing login issues, make sure that email is present in the mapped data")
    saml_user = model.Session.query(User).filter(User.name_id == nameid).first()

    if not saml_user:
        log.debug(f"No User with NAMEID '{nameid}' was found. Creating one.")

        try:
            email = nameid if config.use_nameid_as_email() else mapped_data["email"][0]

            log.debug(f'Check if User with "{email}" email already exists.')
            user_exist = _find_user_by_email(email, nameid=nameid)

            if user_exist:
                log.debug(
                    'Found User "%s" (state=%s) that has same email.',
                    user_exist.name,
                    user_exist.state,
                )
                new_user = user_exist.as_dict()
                log_message = "User is being detected with such NameID, adding to Saml2 table..."
            else:
                user_dict = {
                    "name": _get_random_username_from_email(email)
                    if not config.use_name_from_response()
                    else mapped_data["name"][0],
                    "email": email,
                    "id": str(uuid.uuid4()),
                    "password": str(uuid.uuid4()),
                    "fullname": mapped_data["fullname"][0] if mapped_data.get("fullname") else "",
                }

                log.debug("Trying to create User with name '{}'".format(user_dict["name"]))

                # Before User creation
                for item in p.PluginImplementations(ICKANSAML):
                    item.saml_before_user_create(mapped_data, user_dict)

                new_user = tk.get_action("user_create")({"ignore_auth": True}, user_dict)
                log_message = "User succesfully created. Authorizing..."

            # Make sure that User ID is not already in saml2_user table
            saml_user = model.Session.query(User).filter(User.id == new_user["id"]).first()

            if saml_user:
                log.debug("Found existing row with such User ID, updating NAMEID...")
                saml_user.name_id = nameid
            else:
                saml_user = User(
                    id=new_user["id"],
                    name_id=nameid,
                    attributes=mapped_data,
                )
                model.Session.add(saml_user)
            model.Session.commit()
            log.debug(log_message)
            user = model.User.get(new_user["name"])
        except Exception as e:
            log.exception("Cannot create SAML2 user")
            return h.redirect_to(h.url_for("user.login"))
    else:
        user = model.User.get(saml_user.id)

    user_dict = user.as_dict()
    saml_user.attributes = mapped_data

    # Resolve deleted accounts before syncing profile fields, so updates apply
    # to the account we will actually log in (restored or rebound).
    if user_dict["state"] == "deleted":
        if not config.reactivate_deleted_account():
            log.warning("Blocked login attempt for deleted user %s", user_dict["name"])
            h.flash_error(
                tk._("Your account was deleted. Please, contact the administrator if you want to restore it")
            )
            return tk.abort(403)

        conflict = _email_owner_conflict(user_dict["email"], user.id)
        if conflict:
            # Email already belongs to another account in unique_email_states.
            # Do not restore the deleted user — rebind NameID to the owner.
            log.warning(
                "Cannot restore deleted user %s: email %s belongs to %s (%s). "
                "Rebinding NameID to the email owner.",
                user.name,
                user_dict["email"],
                conflict.name,
                conflict.state,
            )
            saml_user = _rebind_nameid(saml_user, conflict, nameid, mapped_data)
            user = conflict
            user_dict = user.as_dict()
        else:
            log.debug("Restore deleted user %s", user_dict["name"])

    # Compare User data if update is needed.
    check_fields = config.user_fields_trigger_update()
    update_dict: dict[str, Any] = {}

    for field in check_fields:
        if mapped_data.get(field):
            updated = True if mapped_data[field][0] != user_dict[field] else False
            if updated:
                update_dict[field] = mapped_data[field][0]

    # Still deleted here only when email was free and we plan to restore.
    if user_dict["state"] == "deleted" and config.reactivate_deleted_account():
        update_dict["state"] = "active"

    if update_dict:
        for item in update_dict:
            user_dict[item] = update_dict[item]

        # username can be changed only if user is in pending state
        user.state = "pending"
        try:
            tk.get_action("user_update")({"ignore_auth": True}, user_dict)
        except tk.ValidationError:
            log.exception("SSO user cannot be updated")
            h.flash_error("This account is not available. Contact portal administration for support.")
            return h.redirect_to(h.url_for("saml.saml_login"))

    model.Session.commit()

    # Roles and Organizations
    for item in p.PluginImplementations(ICKANSAML):
        item.roles_and_organizations(mapped_data, auth, user)

    if tk.check_ckan_version("2.10"):
        duration_time = timedelta(milliseconds=config.ttl())

        tk.login_user(user, duration=duration_time)
    else:
        session["samlUserdata"] = auth.get_attributes()
        session["samlNameIdFormat"] = auth.get_nameid_format()
        session["samlNameId"] = nameid
        session["samlCKANuser"] = user.name
        session["samlLastLogin"] = datetime.utcnow()

        tk.g.user = user.name

    if "RelayState" in req["post_data"] and req["post_data"]["RelayState"]:
        log.info('Redirecting to "{}"'.format(req["post_data"]["RelayState"]))
        return h.redirect_to(req["post_data"]["RelayState"])

    return tk.redirect_to(_destination())


@saml.route("/saml/metadata")
def metadata():
    try:
        context = dict(model=model, user=tk.g.user, auth_user_obj=tk.g.userobj)
        tk.check_access("sysadmin", context)
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))

    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
    else:
        resp = make_response(", ".join(errors), 500)
    return resp


@saml.route("/saml/login")
def saml_login():
    req = utils.prepare_from_flask_request()
    try:
        auth = utils.make_auth(req)

        if tk.asbool(tk.request.args.get("sso")) or config.unconditional_login():
            saml_relaystate = tk.config.get("ckan.saml_relaystate", None)
            redirect = saml_relaystate if saml_relaystate else _destination()
            if tk.request.args.get("redirect"):
                redirect = tk.request.args.get("redirect")

            if tk.g.user:
                return h.redirect_to(redirect)

            log.info("Redirect to SAML IdP.")
            auth_url = auth.login(return_to=redirect, force_authn=config.force_authn())
            return h.redirect_to(auth_url)
        else:
            log.warning(
                "No arguments been provided in this URL. If you want to make"
                " auth request to SAML IdP point, please provide '?sso=true'"
                " at the end of the URL."
            )
    except Exception as e:
        h.flash_error("SAML: An issue appeared while validating settings file.")
        log.error(f"{e}")

    return h.redirect_to(h.url_for("user.login"))


def _destination() -> str:
    dynamic = tk.request.args.get("came_from", "")
    static = tk.config.get("ckan.auth.route_after_login", "dashboard.index")
    return dynamic or static


def _unique_email_states() -> list[str]:
    """States that count as 'owning' an email (see ckan.user.unique_email_states)."""
    return tk.aslist(tk.config.get("ckan.user.unique_email_states"))


def _users_by_email(email: str, states: Optional[list[str]] = None) -> list[model.User]:
    """Return users with the given email, optionally limited to account states."""
    query = model.Session.query(model.User).filter(
        sql_func.lower(model.User.email) == sql_func.lower(email)
    )
    if states is not None:
        query = query.filter(model.User.state.in_(states))
    return query.all()


def _saml_bound_user_ids(user_ids: list[str]) -> set[str]:
    if not user_ids:
        return set()
    rows = model.Session.query(User.id).filter(User.id.in_(user_ids)).all()
    return {row[0] for row in rows}


def _pick_among_email_users(
    candidates: list[model.User],
    nameid: Optional[str] = None,
) -> Optional[model.User]:
    """Choose one account when several share an email outside unique_email_states.

    Prefer (in order):
    1. Exact ``saml2_user.name_id`` match for this login
    2. Any account that already has a ``saml2_user`` row
    3. First candidate (with a warning if there were several)
    """
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    if nameid:
        by_nameid = (
            model.Session.query(User)
            .filter(User.name_id == nameid, User.id.in_([u.id for u in candidates]))
            .first()
        )
        if by_nameid:
            return model.User.get(by_nameid.id)

    bound_ids = _saml_bound_user_ids([u.id for u in candidates])
    for user in candidates:
        if user.id in bound_ids:
            log.debug(
                "Multiple users share email %s; preferring %s which already has saml2_user",
                user.email,
                user.name,
            )
            return user

    log.warning(
        "Multiple users share email %s with no saml2_user preference; using %s",
        candidates[0].email,
        candidates[0].name,
    )
    return candidates[0]


def _find_user_by_email(
    email: str,
    nameid: Optional[str] = None,
) -> Optional[model.User]:
    """Pick a CKAN user for SAML binding by email.

    1. Prefer owners in ``ckan.user.unique_email_states`` (usually active).
    2. If none, fall back to other accounts with that email (often deleted).
       When several deleted share the email, prefer one that already has a
       ``saml2_user`` binding (see ``_pick_among_email_users``).
    """
    owners = _users_by_email(email, states=_unique_email_states())
    if owners:
        # More than one owner should be rare (partial unique index on active),
        # but still prefer an existing SAML binding if present.
        return _pick_among_email_users(owners, nameid=nameid)

    others = _users_by_email(email)
    return _pick_among_email_users(others, nameid=nameid)


def _email_owner_conflict(email: str, user_id: str) -> Optional[model.User]:
    """Return another account that would block restoring/updating this email.

    Scope is intentionally only ``ckan.user.unique_email_states`` — the same
    set ``email_is_unique`` uses. Other deleted users with the same email are
    *not* conflicts under the default ``[active]`` config: restoring one of
    them is allowed by CKAN. Ambiguous deleted duplicates are handled when
    *choosing* a user (``_find_user_by_email``), not here.

    NameID login already resolves to a specific ``saml2_user`` row before this
    runs; a second deleted twin with its own NameID does not prevent restore.
    """
    for other in _users_by_email(email, states=_unique_email_states()):
        if other.id != user_id:
            return other
    return None


def _rebind_nameid(
    saml_user: User,
    target_user: model.User,
    nameid: str,
    mapped_data: dict[str, Any],
) -> User:
    """Move NameID from the current saml2_user row onto ``target_user``.

    ``saml2_user.id`` is the CKAN user id (PK), so the old row is removed and
    the binding is created/updated on the target account.
    """
    if saml_user.id == target_user.id:
        saml_user.name_id = nameid
        saml_user.attributes = mapped_data
        return saml_user

    model.Session.delete(saml_user)
    model.Session.flush()

    existing = model.Session.query(User).filter(User.id == target_user.id).first()
    if existing:
        existing.name_id = nameid
        existing.attributes = mapped_data
        return existing

    binding = User(id=target_user.id, name_id=nameid, attributes=mapped_data)
    model.Session.add(binding)
    return binding
