from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth

import googleapiclient.discovery
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
        try:
            google_tasks_service = googleapiclient.discovery.build(
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
        # Add a logout link
        return tasks_display + '<br><a href="/logout">Logout</a>'
    else:
        return (
            '<a href="/login">Login with Google</a>'
            + '<br><a href="/logout">Logout</a>'
        )


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
            task_list_id = "@default"  # Replace with a valid task list ID
            google_tasks_service = googleapiclient.discovery.build(
                "tasks", "v1", credentials=credentials
            )
            google_tasks_service.tasks().insert(
                tasklist=task_list_id, body=task
            ).execute()
        except Exception as e:
            print(e)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
