from __future__ import annotations

import logging
import uuid
from datetime import datetime

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan.logic.action.create import _get_random_username_from_email
from flask import Blueprint, make_response, session

from sqlalchemy import func as sql_func

from ckanext.saml.interfaces import ICKANSAML
from ckanext.saml.model.user import User
from ckanext.saml import utils, config


log = logging.getLogger(__name__)
use_nameid_as_email = tk.config.get("ckan.saml_use_nameid_as_email", False)

saml_details = [
    "samlUserdata",
    "samlNameIdFormat",
    "samlNameId",
    "samlCKANuser",
]

saml = Blueprint("saml", __name__)


def get_bp():
    saml.add_url_rule(config.slo_path(), view_func=post_logout)

    saml.add_url_rule(
        config.sso_path(), view_func=post_login, methods=["POST"]
    )

    return saml


def post_logout():
    if "SAMLResponse" in tk.request.args:
        log.debug(
            "SAML2 Logout response: %s",
            utils.decode_saml_response(tk.request.args["SAMLResponse"])
        )
    return tk.h.redirect_to("user.logout")


def post_login():
    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    request_id = None
    auth.process_response(request_id=request_id)
    errors = auth.get_errors()

    if errors:
        log.error("{}".format(errors))
        error_tpl = config.error_template()
        if error_tpl:
            return tk.render(error_tpl, {"errors": errors})

        h.flash_error("Login failed.")
        return h.redirect_to(h.url_for("saml.saml_login"))

    log.debug("User succesfully logged in the IdP. Extracting NAMEID.")
    nameid = auth.get_nameid()

    if not nameid:
        log.error(
            "Something went wrong, no NAMEID was found, "
            "redirecting back to to login page."
        )
        return h.redirect_to(h.url_for("user.login"))

    mapped_data = {}
    attr_mapper = tk.h.saml_attr_mapper()

    if not attr_mapper:
        log.error(
            'User mapping is empty, please set "ckan.saml_custom_attr_map"'
            " param in config."
        )
        return h.redirect_to(h.url_for("user.login"))

    for key, value in attr_mapper.items():
        field = auth.get_attribute(value)
        if field:
            mapped_data[key] = field
    log.debug("NAMEID: {0}".format(nameid))

    for item in plugins.PluginImplementations(ICKANSAML):
        item.after_mapping(mapped_data, auth)
    log.debug("Client data: %s", attr_mapper)
    log.debug("Mapped data: %s", mapped_data)
    log.debug(
        "If you are experiencing login issues, make sure that email is present"
        " in the mapped data"
    )
    saml_user = (
        model.Session.query(User).filter(User.name_id == nameid).first()
    )

    if not saml_user:
        log.debug(
            "No User with NAMEID '{0}' was found. Creating one.".format(nameid)
        )

        try:
            if use_nameid_as_email:
                email = nameid
            else:
                email = mapped_data["email"][0]

            log.debug(
                'Check if User with "{0}" email already exists.'.format(email)
            )
            user_exist = (
                model.Session.query(model.User)
                .filter(
                    sql_func.lower(model.User.email) == sql_func.lower(email)
                )
                .filter(model.User.state == "active")
                .first()
            )

            if user_exist:
                log.debug(
                    'Found User "{0}" that has same email.'.format(
                        user_exist.name
                    )
                )
                new_user = user_exist.as_dict()
                log_message = (
                    "User is being detected with such NameID, adding to Saml2"
                    " table..."
                )
            else:
                user_dict = {
                    "name": _get_random_username_from_email(email),
                    "email": email,
                    "id": str(uuid.uuid4()),
                    "password": str(uuid.uuid4()),
                    "fullname": mapped_data["fullname"][0]
                    if mapped_data.get("fullname")
                    else "",
                }

                log.debug(
                    "Trying to create User with name '{0}'".format(
                        user_dict["name"]
                    )
                )

                new_user = tk.get_action("user_create")(
                    {"ignore_auth": True}, user_dict
                )
                log_message = "User succesfully created. Authorizing..."

            # Make sure that User ID is not already in saml2_user table
            saml_user = (
                model.Session.query(User)
                .filter(User.id == new_user["id"])
                .first()
            )
            if saml_user:
                log.debug(
                    "Found existing row with such User ID, updating NAMEID..."
                )
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

    # Compare User data if update is needed.
    check_fields = ["fullname"]
    update_dict = {}

    for field in check_fields:
        if mapped_data.get(field):
            updated = (
                True if mapped_data[field][0] != user_dict[field] else False
            )
            if updated:
                update_dict[field] = mapped_data[field][0]

    if user_dict["state"] == "deleted":
        if config.reactivate_deleted_account():
            update_dict["state"] = "active"
        else:
            h.flash_error(
                "Your account was deleted. Please, contact the administrator if you want to restore it"
            )
            return h.redirect_to(h.url_for("user.login"))

    if update_dict:
        for item in update_dict:
            user_dict[item] = update_dict[item]

        tk.get_action("user_update")({"ignore_auth": True}, user_dict)
    model.Session.commit()

    # Roles and Organizations
    for item in plugins.PluginImplementations(ICKANSAML):
        item.roles_and_organizations(mapped_data, auth, user)

    session["samlUserdata"] = auth.get_attributes()
    session["samlNameIdFormat"] = auth.get_nameid_format()
    session["samlNameId"] = nameid
    session["samlCKANuser"] = user.name
    session["samlLastLogin"] = datetime.utcnow()

    tk.g.user = user.name

    if "RelayState" in req["post_data"] and req["post_data"]["RelayState"]:
        log.info('Redirecting to "{0}"'.format(req["post_data"]["RelayState"]))
        return h.redirect_to(req["post_data"]["RelayState"])

    return h.redirect_to(h.url_for("dashboard.index"))


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
            redirect = (
                saml_relaystate
                if saml_relaystate
                else h.url_for("dashboard.index")
            )
            if tk.request.args.get("redirect"):
                redirect = tk.request.args.get("redirect")
            log.info("Redirect to SAML IdP.")
            return h.redirect_to(auth.login(return_to=redirect))
        else:
            log.warning(
                "No arguments been provided in this URL. If you want to make"
                " auth request to SAML IdP point, please provide '?sso=true'"
                " at the end of the URL."
            )
    except Exception as e:
        h.flash_error(
            "SAML: An issue appeared while validating settings file."
        )
        log.error("{}".format(e))

    return h.redirect_to(h.url_for("user.login"))
