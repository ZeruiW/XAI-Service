import io
import os
import json
import torch
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import (
    request, jsonify, send_file
)
import requests
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
ebp = ExecutorBluePrint(
    'ACSCV', __name__, component_path=__file__, url_prefix='/ACSCV')

import numpy as np
basedir = os.path.abspath(os.path.dirname(__file__))

# Download this file <https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json>_ as imagenet_class_index.json
imagenet_class_index = json.load(
    open(os.path.join(basedir, "static", 'imagenet_class_index.json')))

def sendRequestCV(img):
    headers = {
        # requests won't add a boundary if this header is set when you pass files=
        # 'Content-Type': 'multipart/form-data',
        'Prediction-Key': '528135dfdd2a4ef4b883eea5952998ca',
        # requests won't add a boundary if this header is set when you pass files=
        # 'content-type': 'multipart/form-data',
    }

    files = {
        '<image file>': img,
    }

    response = requests.post(
        'https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/95d4b387-c987-498e-8db1-4b3208c67132/classify/iterations/Iteration1/image',
        headers=headers,
        files=files,
    )

    print(response.text)
    return outputs

# def get_prediction(imgs):
#     tensor = torch.tensor(np.array([
#         transform_image(x).numpy()
#         for x in imgs
#     ]))
#     outputs = model(tensor).detach().numpy()
#     return outputs
def sendRequestCV(img):
    api_url = 'https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/95d4b387-c987-498e-8db1-4b3208c67132/classify/iterations/Iteration1/image'
    headers = {
        # requests won't add a boundary if this header is set when you pass files=
        # 'Content-Type': 'multipart/form-data',
        'Prediction-Key': '528135dfdd2a4ef4b883eea5952998ca',
        # requests won't add a boundary if this header is set when you pass files=
        # 'content-type': 'multipart/form-data',
    }

    files = {
        '<image file>': img,
    }

    response = requests.post(
        api_url,
        headers=headers,
        files=files,
    )
    print(response.text)
    return response.text


rs=[]
@ebp.route('/', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        files = request.files.getlist('image')
        for file in files:
            prediction = sendRequestCV(file)
        rs.append(prediction)

        #prediction = sendRequestCV(img)
        # rs = {}
        # for i in range(len(file_name)):
        #     rs[file_name[i]] = [round(d, 6) for d in prediction[i].tolist()]
        #return jsonify(rs)
        return rs

    elif request.method == 'GET':
        state_dict_file_path = os.path.join(
            basedir, 'static', 'model.pt')
        torch.save(model.state_dict(), state_dict_file_path)
        return send_file(state_dict_file_path, as_attachment=True)
