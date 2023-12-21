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
    "https://www.googleapis.com/auth/drive.readonly",
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
            print(all_tasks)
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
    google_tasks_service = build("tasks", "v1", credentials=get_credentials())
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
            items.append(f"Task: {task['title']}\tID:{task['id']}")
        all_tasks[task_list["title"]] = {"items": items, "id": task_list["id"]}
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
    session["userdisplayname"] = str(
        db.users_collection.find_one({"email": session["email"]})["name"]
    )

    return redirect("/")


@app.route("/add_task", methods=["POST"])
def add_task():
    task_title = request.form.get("task_title")
    task_list_id = request.form.get("task_list_id")
    if task_title:
        try:
            task = {"title": task_title}
            task_list_id = task_list_id
            google_tasks_service = build(
                "tasks", "v1", credentials=get_credentials()
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
        credentials = get_credentials()
        doclist = get_document_id(credentials)
        total_items = []
        for item in doclist:
            document_id, docname = item
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

                items = process_comments(
                    comments_result,
                    session["email"],
                    session["userdisplayname"],
                    docname,
                )

                total_items.extend(items)

            except Exception as e:
                print(f"Error fetching comments: {e}")
                return f"An error occurred: {e}"

        update_database_with_comments(total_items, session["_user_id"])
        return redirect("/")

    return redirect("/")


def process_comments(comments, user_email, user_displayname, docname):
    items = []

    for comment in comments:
        comment_id = comment["id"]
        comment_content = comment["content"]
        created_time = comment["createdTime"]
        author_displayname = comment.get("author", {}).get("displayName", "")
        made_by_user = False
        if user_email in comment_content.lower():
            items.append(
                (
                    created_time,
                    comment_id,
                    create_comment_dict(
                        comment_id,
                        created_time,
                        docname,
                        comment_content,
                        comment,
                    ),
                )
            )

        if author_displayname.lower() == user_displayname.lower():
            made_by_user = True

        for reply in comment.get("replies", []):
            # someone responded to you and you haven't responded back
            print()
            if (
                reply.get("author", {}).get("displayName", "bad")
                != user_displayname
                and made_by_user
                and not reply.get("replies", [])
            ):
                print("HERE", reply)
                items.append(
                    (
                        reply.get("createdTime", ""),
                        comment_id,
                        create_comment_dict(
                            comment_id,
                            reply.get("createdTime", ""),
                            docname,
                            reply.get("content", ""),
                            reply,
                        ),
                    )
                )
            # you got tagged
            elif user_email in reply.get("content", "").lower():
                items.append(
                    (
                        reply.get("createdTime", ""),
                        comment_id,
                        create_comment_dict(
                            comment_id,
                            reply.get("createdTime", ""),
                            docname,
                            reply.get("content", ""),
                            reply,
                        ),
                    )
                )
            # you are waiting for response
            elif reply.get("author", {}).get(
                "displayName", ""
            ).lower() == user_displayname and not reply.get("replies", []):
                items.append(
                    (
                        reply.get("createdTime", ""),
                        comment_id,
                        create_comment_dict(
                            comment_id,
                            reply.get("createdTime", ""),
                            docname,
                            reply.get("content", ""),
                            reply,
                        ),
                    )
                )

    return items


def create_comment_dict(
    comment_id, created_time, docname, comment_content, comment_data
):
    return {
        "id": comment_id,
        "created": created_time[:-5],
        "docname": docname,
        "content": comment_content,
        "author": comment_data.get("author", {}).get(
            "displayName", "Unknown Author"
        ),
    }


def update_database_with_comments(items, user_id):
    items.sort(reverse=True)

    old = {}
    for _, _, item in items[:20]:
        comment_id = item["id"]
        old[comment_id] = item
    print(old)
    db.users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"notifications": old}},
    )


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

    return [(files[i]["id"], files[i]["name"]) for i in range(len(files))]


@app.route("/delete_task", methods=["POST"])
def delete_task():
    if "google_token" not in session:
        return redirect(url_for("login"))

    try:
        task_list_id = request.form.get("task_list_id")
        task_id = request.form.get("task_id")

        if not task_list_id or not task_id:
            return "Task list ID and task ID are required", 400

        tasks_service = build("tasks", "v1", credentials=get_credentials())

        tasks_service.tasks().delete(
            tasklist=task_list_id, task=task_id
        ).execute()
        return redirect("/fetch_tasks")
    except Exception as e:
        print(f"Error deleting task: {e}")
        return f"An error occurred: {e}"


def get_credentials():
    token = session["google_token"]
    return Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=token["scope"],
    )


if __name__ == "__main__":
    app.run(debug=False, port=8000)
