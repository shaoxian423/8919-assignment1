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

# 加载环境变量
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = app.logger

# 配置 Auth0
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# 通用日志函数
def log_event(event_type, **kwargs):
    log_data = {"event": event_type, "timestamp": datetime.utcnow().isoformat(), "ip_address": request.remote_addr, **kwargs}
    level = logging.INFO if event_type not in ["unauthorized_access", "login_failed"] else logging.WARNING
    logger.log(level, json.dumps(log_data))

@app.route("/")
def home():
    return render_template("home.html", session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))

@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        userinfo = token.get("userinfo", {})
        log_event("user_login", user_id=userinfo.get("sub", "unknown"), email=userinfo.get("email", "unknown"))
        return redirect("/")
    except Exception as e:
        log_event("login_failed", user_id="unknown", email="unknown", error=str(e), path=request.path)
        return redirect(url_for("home", error="Login failed: " + str(e)))

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))