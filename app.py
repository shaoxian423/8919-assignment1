import os
import json
import logging
from datetime import datetime
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
from functools import wraps
import sys  # Ensure sys module is imported

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY") or "default-secret-key"  # Default value for development

# Configure logging, output to stdout for Azure compatibility
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validate environment variables
if not all([env.get("AUTH0_DOMAIN"), env.get("AUTH0_CLIENT_ID"), env.get("AUTH0_CLIENT_SECRET"), env.get("APP_SECRET_KEY")]):
    logger.error("Startup error: Missing required environment variables")
    raise ValueError("Missing required environment variables: AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, or APP_SECRET_KEY")

# Configure Auth0
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# General logging function to emit structured JSON logs
def log_event(event_type, **kwargs):
    log_data = {"event": event_type, "timestamp": datetime.utcnow().isoformat(), "ip_address": request.remote_addr, **kwargs}
    level = logging.INFO if event_type not in ["unauthorized_access", "login_failed"] else logging.WARNING
    logger.log(level, json.dumps(log_data))

@app.route("/")
def home():
    return render_template("home.html", session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4))

@app.route("/login")
def login():
    try:
        return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))
    except Exception as e:
        log_event("login_error", error=str(e), path=request.path)
        if "invalid_redirect_uri" in str(e).lower():
            return "Invalid callback URL configured", 500
        return "Login initiation failed", 500

@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        userinfo = token.get("userinfo", {})
        log_event("user_login", user_id=userinfo.get("sub", "unknown"), email=userinfo.get("email", "unknown"))
        return redirect("/")
    except Exception as e:
        error_msg = str(e)
        if "mismatching_state" in error_msg.lower():
            log_event("login_failed", user_id="unknown", email="unknown", error="CSRF state mismatch", path=request.path)
        else:
            log_event("login_failed", user_id="unknown", email="unknown", error=error_msg, path=request.path)
        return redirect(url_for("home", error="Login failed: " + error_msg))

@app.route("/logout")
def logout():
    user_id = session.get("user", {}).get("userinfo", {}).get("sub", "unknown") if "user" in session else "unknown"
    log_event("user_logout", user_id=user_id)
    session.clear()
    return redirect("https://" + env.get("AUTH0_DOMAIN") + "/v2/logout?" + urlencode({"returnTo": url_for("home", _external=True), "client_id": env.get("AUTH0_CLIENT_ID")}, quote_via=quote_plus))

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            log_event("unauthorized_access", path=request.path)
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/protected")
@requires_auth
def protected():
    userinfo = session["user"]["userinfo"]
    log_event("protected_route_access", user_id=userinfo.get("sub", "unknown"), email=userinfo.get("email", "unknown"), path=request.path)
    return render_template("protected.html", user=userinfo)

# WSGI entry point (required for Azure)
application = app  # Expose app to WSGI server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))  # Only for local testing