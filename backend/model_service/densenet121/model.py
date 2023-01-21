import io
import os
import json
import torch
import base64
import copy
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import (
    request, jsonify, send_file, Response
)
from xai_backend_central_dev.flask_manager import ExecutorBluePrint

import numpy as np

basedir = os.path.abspath(os.path.dirname(__file__))

# Download this file <https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json>_ as imagenet_class_index.json
imagenet_class_index = json.load(
    open(os.path.join(basedir, "static", 'imagenet_class_index.json')))

# model
model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([
        # transforms.Resize(255),
        # transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.485, 0.456, 0.406],
            [0.229, 0.224, 0.225])
    ])
    image = Image.open(io.BytesIO(image_bytes))
    # image.show()
    return my_transforms(image)


ebp = ExecutorBluePrint(
    'densenet121', __name__, component_path=__file__, url_prefix='/densenet121')


def get_prediction(imgs):
    tensor = torch.tensor(np.array([
        transform_image(x).numpy()
        for x in imgs
    ]))
    outputs = model(tensor).detach().numpy()
    return outputs


@ebp.route('/', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        files = request.files
        imgs = files.getlist('image')
        file_name = [img.filename for img in imgs]
        imgs = [i.read() for i in imgs]
        prediction = get_prediction(imgs)

        rs = {}
        for i in range(len(file_name)):
            rs[file_name[i]] = [round(d, 6) for d in prediction[i].tolist()]

        return jsonify(rs)

    elif request.method == 'GET':
        state_dict_file_path = os.path.join(
            basedir, 'static', 'model.pt')
        torch.save(model.state_dict(), state_dict_file_path)
        return send_file(state_dict_file_path, as_attachment=True)
