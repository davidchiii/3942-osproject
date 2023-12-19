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
from bson.objectid import ObjectId

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
        db.connect_db()
        try:
            tasks_display = "<h2>Task Lists:</h2><ul>"
            user_data = db.users_collection.find_one(
                {"_id": ObjectId(session["_user_id"])}
            )
            all_tasks = user_data["tasks"]
            all_notif = user_data["notifications"]
            notif_rows = [[all_notif[id] for id in all_notif]]
            return render_template(
                "cards.html",
                title="NewNotes",
                tasks=all_tasks,
                notification_rows=notif_rows,
            )

        except Exception as e:
            print(e)
            tasks_display = "<p>Error fetching tasks.</p>"
        return tasks_display + '<br><a href="/logout">Logout</a>'
    else:
        return render_template("login.html")


@app.route("/fetch_tasks")
def fetch_tasks():
    db.connect_db()
    token = session["google_token"]
    credentials = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=token["scope"],
    )
    google_tasks_service = build("tasks", "v1", credentials=credentials)
    task_lists = google_tasks_service.tasklists().list().execute()
    all_tasks = {}
    for task_list in task_lists.get("items", []):
        tasks = (
            google_tasks_service.tasks()
            .list(tasklist=task_list["id"])
            .execute()
        )
        items = []
        for task in tasks.get("items", []):
            items.append(f"{task['title']}")
        all_tasks[task_list["title"]] = items
    db.users_collection.update_one(
        {"_id": ObjectId(session["_user_id"])}, {"$set": {"tasks": all_tasks}}
    )
    return redirect("/")


@app.route("/login")
def login():
    res = google.authorize_redirect(
        url_for("authorize", _external=True), prompt="select_account"
    )
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
    session["email"] = user_info["email"].lower()
    session["google_token"] = token

    db.connect_db()
    existing_user = db.users_collection.find_one({"email": session["email"]})
    if not existing_user:
        new_user = {
            "email": user_info["email"],
            "name": user_info.get("name", ""),
            "notifications": {},
            "tasks": {},
        }
        db.users_collection.insert_one(new_user)
    session["_user_id"] = str(
        db.users_collection.find_one({"email": session["email"]})["_id"]
    )

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
        db.connect_db()
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
        print(docname)
        if document_id is None:
            return "<h2>Not Working</h2><ul>'"
        try:
            drive_service = build("drive", "v3", credentials=credentials)

            comments_result = (
                drive_service.comments()
                .list(fileId=document_id, fields="*")
                .execute()["comments"]
            )

            items = [
                (i["id"], i["content"], i["createdTime"])
                for i in comments_result
                if f'@{session["email"]}' in i["content"].lower()
            ]

            old = db.users_collection.find_one(
                {"_id": ObjectId(session["_user_id"])}
            )["notifications"]
            for id, content, created_time in items:
                if id not in old:
                    old[id] = {
                        "created": created_time[:-5],
                        "docname": docname,
                        "content": content,
                    }

            db.users_collection.update_one(
                {"_id": ObjectId(session["_user_id"])},
                {"$set": {"notifications": old}},
            )

            return redirect("/")

        except Exception as e:
            print(f"Error fetching comments: {e}")
            return f"An error occurred: {e}"

    return redirect("/")


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
