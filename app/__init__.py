"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

# from http import HTTPStatus
# from bson.objectid import ObjectId
# from flask_restx import Resource, Api, fields

# import werkzeug.exceptions as wz

from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import db.db as db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["APP_KEY"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
CLIENT_ID = os.environ["CLIENT_ID"]


oauth = OAuth(app)
scope = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive",
]

google = oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={"scope": " ".join(scope)},
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
        try:
            google_tasks_service = build(
                "tasks", "v1", credentials=credentials
            )
            task_lists = google_tasks_service.tasklists().list().execute()
            tasks_display = "<h2>Task Lists:</h2><ul>"
            for task_list in task_lists.get("items", []):
                tasks_display += f"<li>{task_list['title']}</li>"
                tasks = (
                    google_tasks_service.tasks()
                    .list(tasklist=task_list["id"])
                    .execute()
                )
                for task in tasks.get("items", []):
                    tasks_display += f"<li>{task['title']}</li>"
            tasks_display += "</ul>"

        except Exception as e:
            print(e)
            tasks_display = "<p>Error fetching tasks.</p>"
        tasks_display = (
            tasks_display
            + """
        <form method="post" action="/add_task">
            <input type="text" name="task_title" placeholder="Enter task title">
            <input type="submit" value="Add Task">
        </form>
        """
        )
        return tasks_display + '<br><a href="/logout">Logout</a>'
    else:
        return render_template("login.html")


@app.route("/login")
def login():
    res = google.authorize_redirect(
        url_for("authorize", _external=True), prompt="select_account"
    )
    db.connect_db()
    return res


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    resp = google.get("https://www.googleapis.com/oauth2/v3/userinfo")
    user_info = resp.json()
    session["email"] = user_info["email"]
    session["google_token"] = token
    return redirect("/")


@app.route("/add_task", methods=["POST"])
def add_task():
    token = session["google_token"]
    credentials = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=token["scope"],
    )
    task_title = request.form.get("task_title")
    if task_title:
        try:
            task = {"title": task_title}
            task_list_id = "@default"
            google_tasks_service = build(
                "tasks", "v1", credentials=credentials
            )
            google_tasks_service.tasks().insert(
                tasklist=task_list_id, body=task
            ).execute()
        except Exception as e:
            print(e)
    return redirect("/")


@app.route("/fetch_comments")
def fetch_comments():
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
        document_id, docname = get_document_id(credentials)
        if document_id is None:
            return "<h2>Joever</h2><ul>'"
        try:
            # Use docs service when interacting w/ docs look at other services
            # docs_service = build('docs', 'v1', credentials=credentials)
            # docs_service = build('docs', 'v1', credentials=credentials)
            # document = docs_service.documents().get(documentId=document_id).execute()
            drive_service = build("drive", "v3", credentials=credentials)

            comments_result = (
                drive_service.comments()
                .list(fileId=document_id, fields="*")
                .execute()["comments"]
            )

            return "<br>".join([str(i) for i in comments_result])

        except Exception as e:
            print(f"Error fetching comments: {e}")
            return f"An error occurred: {e}"

    return redirect(url_for("login"))


def get_document_id(credentials):
    drive_service = build("drive", "v3", credentials=credentials)

    results = (
        drive_service.files()
        .list(
            q="mimeType='application/vnd.google-apps.document'",
            orderBy="modifiedTime desc",
            pageSize=10,
        )
        .execute()
    )

    files = results.get("files", [])

    if not files:
        return None, None

    return files[0]["id"], files[0]["name"]


if __name__ == "__main__":
    app.run(debug=True)
