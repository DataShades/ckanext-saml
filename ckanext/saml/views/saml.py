from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from urllib.parse import urlparse

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan.logic.action.create import _get_random_username_from_email
from flask import Blueprint, make_response, session
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from sqlalchemy import func as sql_func

from ckanext.saml.interfaces import ICKANSAML
from ckanext.saml.model.user import User

CONFIG_DYNAMIC = "ckanext.saml.settings.dynamic"
DEFAULT_DYNAMIC = False

log = logging.getLogger(__name__)
use_https = tk.config.get("ckan.saml_use_https", "off")
use_nameid_as_email = tk.config.get("ckan.saml_use_nameid_as_email", False)

saml_details = ["samlUserdata", "samlNameIdFormat", "samlNameId", "samlCKANuser"]

saml = Blueprint("saml", __name__)


def prepare_from_flask_request():
    url_data = urlparse(tk.request.url)

    req_path = tk.request.path
    if tk.asbool(tk.config.get("ckan.saml_use_root_path", False)):
        # FIX FOR ROOT_PATH REMOVED IN request.path
        root_path = tk.config.get("ckan.root_path", None)
        if root_path:
            root_path = re.sub("/{{LANG}}", "", root_path)
            req_path = root_path + req_path

    return {
        "https": use_https,
        "http_host": tk.request.host,
        "server_port": url_data.port,
        "script_name": req_path,
        "get_data": tk.request.args.copy(),
        "post_data": tk.request.form.copy(),
    }


@saml.route("/saml/", methods=["GET", "POST"])
@saml.route("/sso/post", methods=["GET", "POST"])
def index():
    if tk.request.method == "POST":
        req = prepare_from_flask_request()
        auth = _make_auth(req)

        request_id = None
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()

        if len(errors) == 0:
            log.debug("User succesfully logged in the IdP. Extracting NAMEID.")

            nameid = auth.get_nameid()

            if not nameid:
                log.error(
                    (
                        "Something went wrong, no NAMEID was found, "
                        "redirecting back to to login page."
                    )
                )
                return h.redirect_to(h.url_for("user.login"))
            else:
                mapped_data = {}
                attr_mapper = tk.h.saml_attr_mapper()
                if attr_mapper:
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
                        "If you are experiencing login issues, make sure that email is present in the mapped data"
                    )
                    saml_user = (
                        model.Session.query(User)
                        .filter(User.name_id == nameid)
                        .first()
                    )

                    if not saml_user:
                        log.debug(
                            (
                                "No User with NAMEID '{0}' was found. "
                                "Creating one.".format(nameid)
                            )
                        )

                        try:
                            if use_nameid_as_email:
                                email = nameid
                            else:
                                email = mapped_data["email"][0]

                            log.debug(
                                'Check if User with "{0}" email already exists.'.format(
                                    email
                                )
                            )
                            user_exist = (
                                model.Session.query(model.User)
                                .filter(
                                    sql_func.lower(model.User.email)
                                    == sql_func.lower(email)
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
                                log_message = "User is being detected with such NameID, adding to Saml2 table..."
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
                                    (
                                        "Trying to create User with name '{0}'".format(
                                            user_dict["name"]
                                        )
                                    )
                                )

                                new_user = tk.get_action("user_create")(
                                    {"ignore_auth": True}, user_dict
                                )
                                log_message = "User succesfully created. Authorizing..."
                            if new_user:
                                # Make sure that User ID is not already in saml2_user table
                                existing_row = (
                                    model.Session.query(User)
                                    .filter(User.id == new_user["id"])
                                    .first()
                                )
                                if existing_row:
                                    log.debug(
                                        "Found existing row with such User ID, updating NAMEID..."
                                    )
                                    existing_row.name_id = nameid
                                else:
                                    model.Session.add(
                                        User(id=new_user["id"], name_id=nameid, attributes=mapped_data)
                                    )
                                model.Session.commit()
                                log.debug(log_message)
                            user = model.User.get(new_user["name"])
                        except Exception as e:
                            print(e)
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
                                    True
                                    if mapped_data[field][0] != user_dict[field]
                                    else False
                                )
                                if updated:
                                    update_dict[field] = mapped_data[field][0]

                        if update_dict:
                            for item in update_dict:
                                user_dict[item] = update_dict[item]
                            tk.get_action("user_update")(
                                {"ignore_auth": True}, user_dict
                            )
                        model.Session.commit()
                        log.info("User already created. Authorizing...")
                else:
                    log.error(
                        'User mapping is empty, please set "ckan.saml_custom_attr_map" param in config.'
                    )
                    return h.redirect_to(h.url_for("user.login"))

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
        else:
            h.flash_error("SAML: Errors appeared while logging process.")
            log.error("{}".format(errors))

    return h.redirect_to(h.url_for("saml.saml_login"))


@saml.route("/saml/metadata")
def metadata():
    try:
        context = dict(model=model, user=tk.g.user, auth_user_obj=tk.g.userobj)
        tk.check_access(u'sysadmin', context)
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))

    req = prepare_from_flask_request()
    auth = _make_auth(req)

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
    req = prepare_from_flask_request()
    try:
        auth = _make_auth(req)

        if tk.asbool(tk.request.args.get("sso")):
            saml_relaystate = tk.config.get("ckan.saml_relaystate", None)
            redirect = (
                saml_relaystate if saml_relaystate else h.url_for("dashboard.index")
            )
            if tk.request.args.get("redirect"):
                redirect = tk.request.args.get("redirect")
            log.info("Redirect to SAML IdP.")
            return h.redirect_to(auth.login(return_to=redirect))
        else:
            log.warning(
                (
                    "No arguments been provided in this URL. If you want to make "
                    "auth request to SAML IdP point, please provide '?sso=true' at "
                    "the end of the URL."
                )
            )
    except Exception as e:
        h.flash_error("SAML: An issue appeared while validating settings file.")
        log.error("{}".format(e))

    return h.redirect_to(h.url_for("user.login"))


def _make_auth(req) -> OneLogin_Saml2_Auth:
    for p in plugins.PluginImplementations(ICKANSAML):
        Auth = p.saml_auth_class()
        if Auth:
            break
    else:
        Auth = OneLogin_Saml2_Auth

    if tk.asbool(tk.config.get(CONFIG_DYNAMIC, DEFAULT_DYNAMIC)):
        return Auth(req, old_settings=tk.h.saml_settings())

    custom_folder = tk.h.saml_folder_path()
    return Auth(req, custom_base_path=custom_folder)
