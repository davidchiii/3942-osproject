import os
import pymongo as pm

client = "unset"
db_name = "default"
db = None
users_collection = None


def connect_db(testing=False):
    global client, db, users_collection, db_name
    if client == "unset":
        if os.environ.get("testing") == "false":
            password = os.environ.get("M_PASS")
            username = os.environ.get("M_USER")
            mongo_url = os.environ.get("M_URL")
            if not password:
                raise ValueError("set M_PASS and M_USER")
            url = f"mongodb+srv://{username}:{password}@{mongo_url}"
            url = url + "/?retryWrites=true&w=majority"
            client = pm.MongoClient(url.format(password, username))
            db = client[db_name]

            users_collection = db.users
            try:
                print(users_collection)
            except Exception as e:
                print(e)
        else:
            print("Connecting to Mongo locally.")
            password = "example"
            username = "root"
            client = pm.MongoClient()
            # if not testing:
            db = client[db_name]
            users_collection = db.users
