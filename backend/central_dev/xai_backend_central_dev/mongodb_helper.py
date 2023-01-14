import pymongo
import os
import traceback


class Mon:

    def __init__(self) -> None:

        mode = os.environ['ENV']

        conn_str = "mongodb://localhost:27017"

        if mode == 'prod':
            conn_str = "mongodb+srv://<username>:<password>@<cluster-address>/test?retryWrites=true&w=majority"

        client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

        try:
            server_info = client.server_info()
            print(
                f"Mongo: connect to server at version {server_info['version']}")
        except Exception as e:
            print("Mongo: unable to connect to the server.")
            traceback.print_exc()
