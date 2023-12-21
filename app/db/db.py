import os
import pymongo as pm

client = "unset"
db_name = "flaskdb"
db = None
users_collection = None


def connect_db(testing=False):
    global client, db, users_collection, db_name
    if client == "unset":
        if os.environ.get("testing") == "false":
            username = os.environ.get("MONGODB_USERNAME")
            password = os.environ.get("MONGODB_PASSWORD")
            mongo_host = os.environ.get("MONGODB_HOSTNAME")
            mongo_db = db_name
            if not password:
                raise ValueError("set M_PASS and M_USER")
            uri = f"mongodb://root:password@{mongo_host}:27017/{mongo_db}"
            # url = url + "/?retryWrites=true&w=majority"
            client = pm.MongoClient("mongodb://root:password@mongodb:27017/")
            db = client[db_name]
            users_collection = db.users
            try:
                print(users_collection)
            except Exception as e:
                print(e)
        else:
            print("Connecting to Mongo locally.")
            password = "password"
            username = "root"
            client = pm.MongoClient(
                f"mongodb://{username}:{password}@mongodb:27017/flaskdb"
            )
            if not testing:
                db = client[db_name]
                users_collection = db.users
