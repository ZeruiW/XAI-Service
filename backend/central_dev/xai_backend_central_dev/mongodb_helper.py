import glob
import pymongo
import os
import json
import traceback
from bson import json_util
from dotenv import dotenv_values


class Mon:

    def __init__(self) -> None:

        MONGO_CONF_STR = os.environ.get('MONGO_CONF_STR')

        if MONGO_CONF_STR is None:
            print(
                f"Please have MONGO_CONF_STR settings in for environment for mongodb settings.")
            exit(1)

        try:
            print(f"Try to connect the mongodb server: {MONGO_CONF_STR}")
            client = pymongo.MongoClient(
                MONGO_CONF_STR, serverSelectionTimeoutMS=5000)
            server_info = client.server_info()
        except Exception as e:
            print(
                f"**** Mongo: unable to connect to the server: {MONGO_CONF_STR}")
            MONGO_CONF_STR = "mongodb://root:example@localhost:27017"
            try:
                print(f"Try to connect the mongodb server: {MONGO_CONF_STR}")
                client = pymongo.MongoClient(
                    MONGO_CONF_STR, serverSelectionTimeoutMS=5000)
                server_info = client.server_info()
            except Exception as e2:
                print(
                    f"**** Mongo: unable to connect to the server: {MONGO_CONF_STR}")
                traceback.print_exc()
                exit(1)

        print(
            f"Mongo: connect to server at version {server_info['version']}")

        self.client = client
        self.xaidb = client.xaidb

    def col(self, col_name):
        return self.xaidb.get_collection(col_name)

    def insert_one(self, col_name, doc):
        return self.col(col_name).insert_one(doc)

    def parse_json(self, data):
        return json.loads(json_util.dumps(data))

    def find(self, col_name, filter):
        return self.parse_json(self.col(col_name).find(filter))

    def find_one(self, col_name, filter):
        return self.parse_json(self.col(col_name).find_one(filter))

    def update_one(self, col_name, filter, update):
        return self.col(col_name).update_one(filter, update)

    def update_many(self, col_name, filter, update):
        return self.col(col_name).update_many(filter, update)

    def delete_one(self, col_name, filter):
        return self.col(col_name).delete_one(filter)

    def deleet_many(self, col_name, filter):
        return self.col(col_name).delete_many(filter)
