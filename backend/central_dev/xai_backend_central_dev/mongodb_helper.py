import glob
import pymongo
import os
import json
import traceback
from bson import json_util
from dotenv import dotenv_values


class Mon:

    def __init__(self) -> None:

        mode = os.environ['ENV']

        mongo_conf = f'mongo.{mode}.conf'
        for f in glob.glob(os.path.join(os.getcwd(), '**', mongo_conf), recursive=True):
            mongo_conf = f

        if not os.path.exists(mongo_conf):
            print(f"Please have {mongo_conf} for mongodb settings.")
            exit(1)

        config = dotenv_values(mongo_conf)

        if config.get('conn_str') is None:
            print(f"Please have 'conn_str' for mongodb settings.")
            exit(1)

        conn_str = config.get('conn_str')

        print("Try to connect the mongodb server...")
        client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

        try:
            server_info = client.server_info()
            print(
                f"Mongo: connect to server at version {server_info['version']}")

            self.client = client
            self.xaidb = client.xaidb
        except Exception as e:
            print("Mongo: unable to connect to the server.")
            traceback.print_exc()
            exit(1)

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
