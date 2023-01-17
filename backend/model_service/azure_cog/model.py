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

basedir = os.path.abspath(os.path.dirname(__file__))

# Download this file <https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json>_ as imagenet_class_index.json
# imagenet_class_index = json.load(
#     open(os.path.join(basedir, "static", 'imagenet_class_index.json')))

# # model
# model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
# model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image)


ebp = ExecutorBluePrint(
    'azure_cog', __name__, component_path=__file__, url_prefix='/azure_cog')


api_key_path = os.path.join(os.environ['COMPONENT_TMP_DIR'], 'api_key')

if not os.path.exists(api_key_path):
    print(f'Please provide api key at: ', api_key_path)
    exit(1)

with open(api_key_path) as f:
    api_key = f.readlines()[0]

# def get_prediction(imgs):
#     tensor = torch.tensor(np.array([
#         transform_image(x).numpy()
#         for x in imgs
#     ]))
#     outputs = model(tensor).detach().numpy()
#     return outputs


class_names = [
    # 'n01443537',    # goldfish
    # 'n01608432',    # kite (kind of bird)
    # 'n01882714',    # koala
    # 'n02091635',    # otterhound (ko dog)
    # 'n02123159'     # tiger_cat
]

staticdir = os.environ.get('COMPONENT_STATIC_DIR')
class_map_path = os.path.join(staticdir, 'imagenet_class_index.json')
with open(class_map_path, 'r') as f:
    mapp = json.load(f)
    pair = []
    for k, v in mapp.items():
        pair.append((int(k), v[0]))

    pair = sorted(pair, key=lambda a: a[0])
    for p in pair:
        class_names.append(p[1])


def sendRequestCV(img):
    # api_url = 'https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/95d4b387-c987-498e-8db1-4b3208c67132/classify/iterations/Iteration1/image'
    # api_url = 'https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/d4a22cfc-8f99-4172-8409-9b9c780bfbb3/classify/iterations/Iteration1/image'
    api_url = 'https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/cfee6c8a-e2d1-467a-b559-3fe0a9db4ae5/classify/iterations/Iteration1/image'
    headers = {
        # requests won't add a boundary if this header is set when you pass files=
        # 'Content-Type': 'multipart/form-data',
        'Prediction-Key': api_key,
        # requests won't add a boundary if this header is set when you pass files=
        # 'Content-type': 'application/octet-stream',
    }

    files = {
        '<image file>': img,
    }

    response = requests.post(
        api_url,
        headers=headers,
        files=files,
    )

    return json.loads(response.text)


def get_pred_score(service_response):
    for class_p in service_response['predictions']:
        class_p['class_idx'] = class_names.index(class_p['tagName'])

    service_response['predictions'] = sorted(
        service_response['predictions'], key=lambda a: a['class_idx'])
    return [x['probability'] for x in service_response['predictions']]


@ebp.route('/', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        files = request.files
        imgs = files.getlist('image')
        file_name = [img.filename for img in imgs]

        imgs = [i.read() for i in imgs]

        prediction = []

        for img in imgs:
            p = sendRequestCV(img)
            # print(p)
            scores = get_pred_score(p)
            prediction.append(scores)

        # print(prediction)

        rs = {}
        for i in range(len(file_name)):
            rs[file_name[i]] = [round(d, 6) for d in prediction[i]]

        return jsonify(rs)

    elif request.method == 'GET':
        # ANCHOR: no model parameters return
        return Response("", status=400)
