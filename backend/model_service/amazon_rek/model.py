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
#amazon
import boto3
from PIL import ImageDraw, ExifTags, ImageColor, ImageFont

basedir = os.path.abspath(os.path.dirname(__file__))


ebp = ExecutorBluePrint(
    'amazon_rek', __name__, component_path=__file__, url_prefix='/amazon_rek')

api_conf_path = os.path.join(os.environ['COMPONENT_TMP_DIR'], 'amazon.json')
#"amazon_rek_storage/tmp/amazon.json"
#

if not os.path.exists(api_conf_path):
    print(f'Please provide api key at: ', api_conf_path)
    exit(1)

with open(api_conf_path) as f:
    api_conf = json.load(f)



bucket = api_conf['bucket']
model = api_conf['model']
service_type = api_conf['service_type']
region_name = api_conf['region_name']
aws_access_key_id = api_conf['aws_access_key_id']
aws_secret_access_key = api_conf['aws_secret_access_key']


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

def show_custom_labels(model, bucket, photo_bytes, min_confidence):
    client = boto3.client('rekognition', region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Decode image data and get image format
    image = Image.open(io.BytesIO(photo_bytes))
    image_format = image.format

    # Check image format
    if image_format not in ['JPEG', 'PNG']:
        raise ValueError(f"Invalid file format. Supply a jpeg or png format file")

    # Convert image to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image_format)
    image_bytes = image_bytes.getvalue()    

    # Call DetectCustomLabels
    response = client.detect_custom_labels(
        Image={'Bytes': image_bytes},
        MinConfidence=min_confidence,
        ProjectVersionArn=model
    )

    return response

# Load image file into memory
# with open("n01498041_849.JPEG", "rb") as f:
#     file_content = f.read()

# Call show_custom_labels function with image data

def get_pred_score(service_response):
    for class_p in service_response:
        class_p['class_idx'] = class_names.index(class_p['Name'])

    service_response = sorted(service_response, key=lambda x: x['class_idx'])
    return [x['Confidence'] for x in service_response]


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
            p = show_custom_labels(
                model,
                bucket,
                photo_bytes=img,
                min_confidence=0
            ).get('CustomLabels')

            #print(p)
            scores = get_pred_score(p)
            prediction.append(scores)

        #print(prediction)

        rs = {}
        for i in range(len(file_name)):
            rs[file_name[i]] = [round(d, 6) for d in prediction[i]]

        return jsonify(rs)

    elif request.method == 'GET':
        # ANCHOR: no model parameters return
        return Response("It is a cloud model!", status=400)
