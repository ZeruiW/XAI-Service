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
collectionstr_EVA = os.getenv("MONGO_EVA_COLLECTION")
database = client[databasestr]
collection = database[collectionstr]
collection_XAI = database[collectionstr_XAI]
collection_EVA = database[collectionstr_EVA]


from PIL import Image

#input xai task ticket and index, get the heatmap
def find_heatmap_with_xai_task_ticket(task_ticket, index):
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



def find_heatmap_with_evaluation_task_ticket(task_ticket, index):
    cam_data = collection_EVA.find_one({
            "task_ticket": task_ticket
        })
    filename = cam_data['cam_documents'][index - 1]['filename']
    #org_img = base64.b64decode(cam_data['cam_documents'][index - 1]['org_img'])
    org_img = np.frombuffer(cam_data['cam_documents'][index - 1]['org_img'], dtype=np.uint8)
    
    print(filename)
    with open('image.png', 'wb') as f:
        f.write(org_img)
    image = Image.open('image.png')
    image.show()
    # image_data = cam_data['image']
    # #show the image
    # with open('image2.png', 'wb') as f:
    #     f.write(image_data)
    # encoded_image = base64.b64encode(image_data).decode('utf-8')
    # return encoded_image

find_heatmap_with_evaluation_task_ticket("qMItgoVUZUCtKrX.3800597.QGEZ5O9FXQ", 1)