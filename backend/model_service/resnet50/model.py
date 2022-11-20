import io
import os
import json
import torch
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import (
    Blueprint, request, jsonify, send_file
)
import numpy as np

basedir = os.path.abspath(os.path.dirname(__file__))

# print(basedir)

# Download this file <https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json>_ as imagenet_class_index.json
imagenet_class_index = json.load(
    open(os.path.join(basedir, "static", 'imagenet_class_index.json')))

# model
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
# model = models.resnet50(pretrained=True)
model.eval()
#target_layers = model.layer4[-1]

# preprocess for transform


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image)


bp = Blueprint('resnet50', __name__, url_prefix='/resnet50')


def get_prediction(imgs):
    tensor = torch.tensor(np.array([
        transform_image(x).numpy()
        for x in imgs
    ]))
    outputs = model(tensor).detach().numpy()
    return outputs


@bp.route('/', methods=['GET', 'POST'])
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
