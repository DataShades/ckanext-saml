from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from typing import cast

from flask import Blueprint, make_response
from sqlalchemy import func as sql_func

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic.action.create import _get_random_username_from_email

from ckanext.saml import config, utils
from ckanext.saml.interfaces import ICKANSAML
from ckanext.saml.model.user import User

log = logging.getLogger(__name__)


saml = Blueprint("saml", __name__)


def get_blueprints():
    return [saml]


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

    if config.log_last_saml_response():
        utils.log_saml_response(
            {
                "errors": errors,
                "error_reason": auth.get_last_error_reason(),
                "user_attributes": auth.get_attributes(),
                "is_authenticated": auth.is_authenticated(),
                "idp_data": auth.get_settings().get_idp_data(),
                "sp_data": auth.get_settings().get_sp_data(),
            }
        )

    if errors:
        log.error("{}".format(errors))
        error_tpl = config.get_error_template()

        if error_tpl:
            return tk.render(error_tpl, {"errors": errors})

        h.flash_error("Login failed.")
        return h.redirect_to(h.url_for("saml.saml_login"))

    log.debug("User succesfully logged in the IdP. Extracting NAMEID.")
    nameid = auth.get_nameid()

    if not nameid:
        log.error(
            "Something went wrong, no NAMEID was found, "
            "redirecting back to the login page."
        )
        return h.redirect_to(h.url_for("user.login"))

    mapped_data = {}
    attr_mapper = tk.h.saml_get_attribute_mapper()

    for key, value in attr_mapper.items():
        field = auth.get_attribute(value)
        if field:
            mapped_data[key] = field

    for item in plugins.PluginImplementations(ICKANSAML):
        item.after_mapping(mapped_data, auth)

    log.debug("Client data: %s", attr_mapper)
    log.debug("Mapped data: %s", mapped_data)
    log.debug(
        "If you are experiencing login issues, make sure that email is present"
        " in the mapped data"
    )

    saml_user = model.Session.query(User).filter(User.name_id == nameid).first()

    if not saml_user:
        log.debug("No User with NAMEID '{0}' was found. Creating one.".format(nameid))

        try:
            email = nameid if config.use_nameid_as_email() else mapped_data["email"][0]

            log.debug('Check if User with "{0}" email already exists.'.format(email))
            user_exist = (
                model.Session.query(model.User)
                .filter(sql_func.lower(model.User.email) == sql_func.lower(email))
                .first()
            )

            if user_exist:
                log.debug(
                    'Found User "{0}" that has same email.'.format(user_exist.name)
                )
                new_user = user_exist.as_dict()
                log_message = (
                    "User is being detected with such NameID, adding to Saml2 table..."
                )
            else:
                user_dict = {
                    "name": _get_random_username_from_email(email),
                    "email": email,
                    "id": str(uuid.uuid4()),
                    "password": str(uuid.uuid4()),
                    "fullname": (
                        mapped_data["fullname"][0]
                        if mapped_data.get("fullname")
                        else ""
                    ),
                }

                log.debug(
                    "Trying to create User with name '{0}'".format(user_dict["name"])
                )

                new_user = tk.get_action("user_create")(
                    {"ignore_auth": True}, user_dict
                )
                log_message = "User succesfully created. Authorizing..."

            # Make sure that User ID is not already in saml2_user table
            saml_user = (
                model.Session.query(User).filter(User.id == new_user["id"]).first()
            )

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
        except Exception:
            log.exception("Cannot create SAML2 user")
            return h.redirect_to(h.url_for("user.login"))
    else:
        user = model.User.get(saml_user.id)

    user_dict = user.as_dict()
    saml_user.attributes = mapped_data

    # Compare User data if update is needed.
    check_fields = ["fullname"]
    update_dict = {}

    for field in check_fields:
        if mapped_data.get(field):
            updated = True if mapped_data[field][0] != user_dict[field] else False
            if updated:
                update_dict[field] = mapped_data[field][0]

    if user_dict["state"] == "deleted":
        if config.reactivate_deleted_account():
            update_dict["state"] = "active"
            log.debug("Restore deleted user %s", user_dict["name"])

        else:
            log.warning("Blocked login attempt for deleted user %s", user_dict["name"])

            h.flash_error(
                tk._(
                    "Your account was deleted. Please, contact the"
                    " administrator if you want to restore it"
                )
            )
            return tk.abort(403)

    if update_dict:
        for item in update_dict:
            user_dict[item] = update_dict[item]

        tk.get_action("user_update")({"ignore_auth": True}, user_dict)

    model.Session.commit()

    # Roles and Organizations
    for item in plugins.PluginImplementations(ICKANSAML):
        item.roles_and_organizations(mapped_data, auth, user)

    tk.login_user(user, duration=timedelta(milliseconds=config.get_session_ttl()))

    if relay_state := req["post_data"].get("RelayState"):
        log.info('Redirecting to "%s"', relay_state)
        return h.redirect_to(relay_state)

    return tk.redirect_to(_destination())


@saml.route("/saml/metadata")
def metadata():
    try:
        tk.check_access(
            "sysadmin",
            cast(
                types.Context,
                {
                    "model": model,
                    "user": tk.current_user.name,
                    "auth_user_obj": tk.current_user,
                },
            ),
        )
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
    except Exception as e:
        h.flash_error("SAML: An issue appeared while validating settings file.")
        log.error(e)
        return h.redirect_to(h.url_for("user.login"))

    if tk.asbool(tk.request.args.get("sso")) or config.is_unconditional_login_enabled():
        return_to = config.get_relay_state() or _destination()

        if tk.request.args.get("redirect"):
            return_to = tk.request.args.get("redirect")

        log.info("Redirect to SAML IdP.")
        return h.redirect_to(auth.login(return_to=return_to))
    else:
        log.warning(
            "No arguments been provided in this URL. If you want to make"
            " auth request to SAML IdP point, please provide '?sso=true'"
            " at the end of the URL."
        )

    return h.redirect_to(h.url_for("user.login"))


def _destination() -> str:
    dynamic = tk.request.args.get("came_from", "")
    static = tk.config.get("ckan.route_after_login", "dashboard.index")
    return dynamic or static


saml.add_url_rule(config.get_slo_path(), view_func=post_logout)
saml.add_url_rule(config.get_sso_path(), view_func=post_login, methods=["POST"])
