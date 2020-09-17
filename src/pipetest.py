import re
import uuid

import flask
import settings
import requests
import threading
import datetime

from tinydb import TinyDB, Query, operations
from flask import Flask, jsonify, sessions, url_for, request, session
from tinydb.operations import add

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = str(uuid.uuid4().hex)
app.permanent_session_lifetime = datetime.timedelta(days=365)

db = TinyDB("../db/db.json")
users_table = db.table("users")
sessions_table = db.table("sessions")
User = Query()
Session = Query()


@app.route("/health", methods=["GET"])
def heartbeat():
    resp = flask.make_response(jsonify(status="UP"), 200)
    return resp


# Returns all users ever scanned by the app.
@app.route("/getAllScannedUsers", methods=["GET"])
def get_scanned_users():
    all_users_data = users_table.search(User.username.matches(".*"))
    resp_body = []
    for user_entry in all_users_data:
        resp_body.append(user_entry["username"])
    resp = flask.make_response(jsonify(resp_body), 200)
    return resp


# Returns users that are currnetly being scanned
@app.route("/getCurrentlyScannedUsers", methods=["GET"])
def get_currently_scanned_users():
    resp = flask.make_response(jsonify(settings.queried_users), 200)
    return resp


# Returns list of new gists for particular session
@app.route("/getGists", methods=["GET"])
def get_gists():
    all_users_data = users_table.search(User.username.matches(".*"))
    all_gists = []

    # Get all gists for all users from DB
    for user_entry in all_users_data:
        for gist in user_entry["gists"]:
            all_gists.append(gist)

    # Check session
    if "session_id" in session:
        app.logger.info("Found existing session id={}".format(session["session_id"]))

        # Get info about the session from DB
        all_sessions_data = sessions_table.get(Session.session_id.matches(session["session_id"]))

        # Diff all gists and last time shown gists
        new_gists = list(set(all_gists) - set(all_sessions_data["shown_gists"]))

        # Update session info in DB
        sessions_table.update({"shown_gists": all_gists}, Session.session["session_id"] == session["session_id"])
        return flask.make_response(jsonify(new_gists), 200)
    else:
        # Generate and save new session_id in session cookie
        session_id = str(uuid.uuid4().hex)
        session["session_id"] = session_id
        app.logger.info("Created new session id={}".format(session_id))

        # save session in db with
        sessions_table.insert({"session_id":  session["session_id"], "shown_gists": all_gists})
        return flask.make_response(jsonify(all_gists), 200)


# Periodically run
def scan_gists():
    app.logger.info("Scanning gists for users {}".format(settings.queried_users))
    for username in settings.queried_users:

        # Save user in DB and create Pipedrive org if new user
        if users_table.contains(User.username == username) is False:
            register_new_user(username)

        get_gists_request_url = "http://api.github.com/users/{}/gists".format(username)
        app.logger.info("Sent request to GitHub API {}".format(get_gists_request_url))
        get_gists_response = requests.get(get_gists_request_url)
        app.logger.info("Received response from GitHub API {}".format(get_gists_request_url))

        if get_gists_response.status_code != 200:
            app.logger.error("Failed to get GitHub gists for user {}. Response code {}".format(username, get_gists_response.status_code))
        else:
            app.logger.info("Successfully fetched GitHub gists for user {}".format(username))

            for gist in get_gists_response.json():
                user_gists = users_table.get(User.username == username)["gists"]
                if gist["id"] not in user_gists:
                    app.logger.info("New gist id={} found for user {}".format(gist["id"], username))
                    create_new_deal(gist,username,user_gists)

    # Run function periodically
    threading.Timer(int(settings.querying_interval) * 60, scan_gists).start()


def register_new_user(username):
    # Create Org in Pipedrive CRM
    create_organization_url = "https://{}.pipedrive.com/api/v1/organizations?api_token=".format(
        settings.pipedrive_company_name)
    app.logger.info("Sent request to Pipedrive API {}{}".format(create_organization_url,
                                                                mask_sensitive_data(settings.pipedrive_api_token)))
    create_organization_response = requests.post(create_organization_url + settings.pipedrive_api_token,
                                                 data={"name": username})
    app.logger.info("Received response from Pipedrive API {}{}".format(create_organization_url, mask_sensitive_data(
        settings.pipedrive_api_token)))

    # Register user in DB if Org is created successfully
    if create_organization_response.status_code == 201:
        app.logger.info("New organization for user {} is successfully created in Pipedrive CRM".format(username))
        users_table.insert({"username": username, "gists": []})
        app.logger.info("Added new user {} to DB".format(username))
    else:
        app.logger.error(
            "Failed to create organization in Pipedrive CRM for user {}. Response code {} {}".format(username, create_organization_response.status_code, create_organization_response))


# Mask sensitive data
def mask_sensitive_data(string):
    return string[:4] + re.sub(".", "*", string[4:])


# Creates New Deal in Pipedrive CRM
def create_new_deal(gist, username, user_gists):
    # Create new deal in CRM
    create_deal_url = "https://{}.pipedrive.com/api/v1/deals?api_token=".format(settings.pipedrive_company_name)
    app.logger.info(
        "Sent request to Pipedrive API {}{}".format(create_deal_url, mask_sensitive_data(settings.pipedrive_api_token)))
    create_deal_response = requests.post(create_deal_url + settings.pipedrive_api_token,
                                         data={"org_id": username, "title": gist["id"]})
    app.logger.info("Received response from Pipedrive API {}{}".format(create_deal_url, mask_sensitive_data(
        settings.pipedrive_api_token)))

    # Register user in DB if Org is created successfully
    if create_deal_response.status_code == 201:
        app.logger.info("New deal for gist {} is successfully created in Pipedrive CRM".format(gist["id"]))
        user_gists.append(gist["id"])
        users_table.update({"gists": user_gists}, User.username == username)
        app.logger.info("Added gist id={} to DB".format(gist["id"]))
    else:
        app.logger.error(
            "Failed to create organization in Pipedrive CRM for user {}. Response code {} {}".format(username, create_deal_response.status_code, create_deal_response))


# Start scanning GitHub for new gists
scan_gists()
