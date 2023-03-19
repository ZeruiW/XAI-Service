import io
import os
import json
import torch
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import (
    request, jsonify, send_file, Response
)
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
import requests
import numpy as np
import base64
from typing import Sequence, Union
#alibaba_ml

basedir = os.path.abspath(os.path.dirname(__file__))

ebp = ExecutorBluePrint(
    'alibaba_ml', __name__, component_path=__file__, url_prefix='/alibaba_ml')

api_conf_path = os.path.join(os.environ['COMPONENT_TMP_DIR'], 'alibaba.json')
#"amazon_rek_storage/tmp/amazon.json"
#

if not os.path.exists(api_conf_path):
    print(f'Please provide api key at: ', api_conf_path)
    exit(1)

with open(api_conf_path) as f:
    api_conf = json.load(f)

url = api_conf['url']
headers = api_conf['headers']


class_names = [
    # 'n01443537',    # goldfish
    # 'n01608432',    # kite (kind of bird)
    # 'n01882714',    # koala
    # 'n02091635',    # otterhound (ko dog)
    # 'n02123159'     # tiger_cat
]
staticdir = os.environ.get('COMPONENT_STATIC_DIR')
class_map_path = os.path.join(staticdir, 'imagenet_class_index.json')
#class_map_path = os.path.join('static/imagenet_class_index.json')

with open(class_map_path, 'r') as f:
    mapp = json.load(f)
    pair = []
    for k, v in mapp.items():
        pair.append((int(k), v[0]))

    pair = sorted(pair, key=lambda a: a[0])
    for p in pair:
        class_names.append(p[1])



def get_response(url, headers, input_img):

    encoded_data = base64.b64encode(input_img).decode("utf-8")
    request_body = {
        "dataArray": [
            {
                "type": "stream",
                "name": "image",
                "body": encoded_data,
            }
        ]
    }

    response = requests.post(url, headers=headers, json=request_body)
    return response.json()



def get_pred_score(service_response):
    for class_p in service_response:
        class_p['class_idx'] = class_names.index(class_p['label'])

    service_response = sorted(service_response, key=lambda x: x['class_idx'])
    return [x['conf'] for x in service_response]


#Server

@ebp.route('/', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        files = request.files
        imgs = files.getlist('image')
        file_name = [img.filename for img in imgs]

        imgs = [i.read() for i in imgs]

        prediction = []

        for img in imgs:
            p = get_response(
                url,
                headers,
                img
            )
            body_list = p['result']['output'][0]['body']


            scores = get_pred_score(body_list)
            prediction.append(scores)


        rs = {}
        for i in range(len(file_name)):
            rs[file_name[i]] = [round(d, 6) for d in prediction[i]]

        return jsonify(rs)

    elif request.method == 'GET':
        # ANCHOR: no model parameters return
        return Response("It is a cloud model!", status=400)
