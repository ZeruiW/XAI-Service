import datetime
import os
import base64
#timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
import numpy as np
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
from bson.objectid import ObjectId
# Connect to the MongoDB instance
connection_string = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(connection_string)

# Select the database and collection
databasestr = os.getenv("MONGO_DATABASE")
collectionstr = os.getenv("MONGO_COLLECTION")
collectionstr_XAI = os.getenv("MONGO_XAI_COLLECTION")
database = client[databasestr]
collection = database[collectionstr]
collection_XAI = database[collectionstr_XAI]


npydoc = collection_XAI.find_one({
            "task_ticket": "j8qJCqyM2lW2cFa.0814936.J47PX0K8G0",
            "index" : 4})
binary_image_data = npydoc['image']

from PIL import Image

#input task ticket and index, get the heatmap
def find_heatmap_with_task_ticket(task_ticket, index):
    cam_data = collection_XAI.find_one({
            "task_ticket": task_ticket,
            "index" : index            
        })
    image_data = cam_data['image']
    #show the image
    with open('image2.png', 'wb') as f:
        f.write(image_data)
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    return encoded_image


# show the image
