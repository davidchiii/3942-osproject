import os
import pymongo as pm

# from bson.objectid import ObjectId

client = "unset"
db_name = "TASK_USERS"


def connect_db():
    global client
    if client == "unset":
        if os.environ.get("testing") == "true":
            password = os.environ.get("M_PASS")
            username = os.environ.get("M_USER")
            mongo_url = os.environ.get("M_URL")
            if not password:
                raise ValueError("set M_PASS and M_USER")
            url = f"mongodb+srv://{username}:{password}@{mongo_url}"
            url = url + "/?retryWrites=true&w=majority"
            client = pm.MongoClient(url.format(password, username))
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()
