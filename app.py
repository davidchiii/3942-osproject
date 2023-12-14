from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

# import googleapiclient.discovery
from google.oauth2.credentials import Credentials
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["APP_KEY"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
CLIENT_ID = os.environ["CLIENT_ID"]


oauth = OAuth(app)


google = oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        "scope": "openid email profile https://www.googleapis.com/auth/tasks"
    },
)


@app.route("/")
def home():
    if "google_token" in session:
        token = session["google_token"]
        credentials = Credentials(
            token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=token["scope"],
        )
        credentials
        return "HELLO WORLD" + '<br><a href="/logout">Logout</a>'
    else:
        return '<a href="/login">Login with Google</a>'


@app.route("/login")
def login():
    res = google.authorize_redirect(url_for("authorize", _external=True))
    return res


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    resp = google.get("https://www.googleapis.com/oauth2/v3/userinfo")
    user_info = resp.json()
    session["email"] = user_info["email"]
    session["google_token"] = token
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
