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

#google
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from typing import Sequence, Union


basedir = os.path.abspath(os.path.dirname(__file__))

# Download this file <https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json>_ as imagenet_class_index.json
# imagenet_class_index = json.load(
#     open(os.path.join(basedir, "static", 'imagenet_class_index.json')))

# # model
# model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
# model.eval()


# def transform_image(image_bytes):
#     my_transforms = transforms.Compose([transforms.Resize(255),
#                                         transforms.CenterCrop(224),
#                                         transforms.ToTensor(),
#                                         transforms.Normalize(
#                                             [0.485, 0.456, 0.406],
#                                             [0.229, 0.224, 0.225])])
#     image = Image.open(io.BytesIO(image_bytes))
#     return my_transforms(image)

ebp = ExecutorBluePrint(
    'google_image_class', __name__, component_path=__file__, url_prefix='/google_image_class')

api_conf_path = os.path.join(os.environ['COMPONENT_TMP_DIR'], 'googlecloud.json')

if not os.path.exists(api_conf_path):
    print(f'Please provide api key at: ', api_conf_path)
    exit(1)

with open(api_conf_path) as f:
    api_conf = json.load(f)

#credebtials_path = os.path.join(os.environ['static'], 'googlecloud.json')
#staticdir = os.environ.get('COMPONENT_STATIC_DIR')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_conf_path

# if not os.path.exists(credebtials_path):
#     print(f'Please provide api key at: ', credebtials_path)
#     exit(1)

# with open(credebtials_path) as f:
#     api_conf = json.load(f)

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
#class_map_path = os.path.join('static/imagenet_class_index.json')

with open(class_map_path, 'r') as f:
    mapp = json.load(f)
    pair = []
    for k, v in mapp.items():
        pair.append((int(k), v[0]))

    pair = sorted(pair, key=lambda a: a[0])
    for p in pair:
        class_names.append(p[1])

def prepare_service_response(tag_names, probabilities):
    predictions = [{'tagName': tag_names[i], 'probability': probabilities[i]} for i in range(len(tag_names))]
    return {'predictions': predictions}


def predict_image_classification_sample(
    project: str,
    endpoint_id: str,
    file_content,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)


    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
    parameters = predict.params.ImageClassificationPredictionParams(
        #confidence_threshold=0.5, max_predictions=5,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )

    #print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
    #predictions = response.predictions
    
    # print(" predictions:", predictions)
    # for prediction in predictions:
    #     print(" prediction:", dict(prediction))


    # Create a dictionary with the predictions.

    # Convert the predictions object to a list of dictionaries.
    predictions = []
    for prediction in response.predictions:
        predictions.append(dict(prediction))
    
    # Return the predictions as a JSON-encoded string.

    labels = predictions[0]['displayNames']
    scores = predictions[0]['confidences']


    service_response = prepare_service_response(labels, scores)
    return service_response


# with open("n01491361_234.JPEG", "rb") as f:
#     file_content = f.read()

# run the sample



def get_pred_score(service_response):
    #print(class_names)
    for class_p in service_response['predictions']:
        class_p['class_idx'] = class_names.index(class_p['tagName'])


    service_response['predictions'] = sorted(
        service_response['predictions'], key=lambda a: a['class_idx'])
    return [x['probability'] for x in service_response['predictions']]


# p = predict_image_classification_sample(
#     project="537600793262",
#     endpoint_id="2606726565177851904",
#     location="us-central1",
#     file_content=file_content,
# )
# scores = get_pred_score(p)
# print(scores)

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
            p = predict_image_classification_sample(
                project="537600793262",
                endpoint_id="2606726565177851904",
                location="us-central1",
                file_content=img,
            )
            scores = get_pred_score(p)
            prediction.append(scores)
        rs = {}
        for i in range(len(file_name)):
            rs[file_name[i]] = [round(d, 6) for d in prediction[i]]

        return jsonify(rs)

    elif request.method == 'GET':
        # ANCHOR: no model parameters return
        return Response("It is a cloud model!", status=400)
