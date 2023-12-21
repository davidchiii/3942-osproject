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
            password = os.environ.get("MONGODB_PASSWORD")
            username = os.environ.get("MONGODB_USERNAME")
            mongo_host = os.environ.get("MONGODB_HOSTNAME")
            mongo_db = os.environ.get("MONGODB_DATABASE")
            if not password:
                raise ValueError("set M_PASS and M_USER")
            url = f"mongodb://{username}:{password}@{mongo_host}:27017/{mongo_db}"
            # url = url + "/?retryWrites=true&w=majority"
            client = pm.MongoClient(url)
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
            #     db = client[db_name]
            #     users_collection = db.users
