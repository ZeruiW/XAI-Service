from pytorch_grad_cam import GradCAM
from PIL import Image
import torchvision.transforms as T
import torch
from torchvision import models
import shutil
import requests
import numpy as np
from flask import (
    request, jsonify, send_file
)
import json
import io
import time
import base64
import os
import matplotlib.pyplot as plt
import platform
from xai_backend_central_dev.flask_manager import ExecutorBluePrint

task_executor_info = {
    'executor_name': 'xai_service:pt_cam'
}

ebp = ExecutorBluePrint(
    'pt_cam', __name__, task_executor_info=task_executor_info, url_prefix='/xai/pt_cam')
te = ebp.get_task_executor()

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.path.join(basedir, 'tmp')

# device = torch.device("cpu")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.backends.mps.is_built() and torch.backends.mps.is_available():
    device = torch.device("mps")

print('--------')
print('Platform:')
print(platform.platform())
print("Pytorch device: ")
print(device)
print('--------')


def cam_task(task_ticket, form_data):
    print(form_data)
    print(task_ticket)

    print('# get image data')
    response = requests.get(
        form_data['db_service_url'], params={
            'img_group': form_data['data_set_group_name'],
            'with_img_data': 1,
        })
    # print(response)
    img_data = json.loads(response.content.decode('utf-8'))

    # for igd in img_data:
    #     dcode = base64.b64decode(igd[2])
    #     img = Image.open(io.BytesIO(dcode))
    #     img.show()

    print('# get model pt')
    model_pt_path = os.path.join(tmpdir, f"{form_data['model_name']}.pth")
    response = requests.get(
        form_data['model_service_url'])
    with open(model_pt_path, "wb") as f:
        f.write(response.content)

    # load model

    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.eval()
    model.to(device)

    model.load_state_dict(torch.load(model_pt_path))

    target_layers = [model.layer4]

    preprocessing = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    ])

    print("# cam gen")
    i = 0

    # explanation save dir
    e_save_dir = os.path.join(tmpdir, form_data['model_name'], form_data['method_name'],
                              form_data['data_set_name'], form_data['data_set_group_name'], task_ticket)
    if not os.path.isdir(e_save_dir):
        os.makedirs(e_save_dir, exist_ok=True)

    for imgd in img_data:
        print(i, imgd[1])
        i += 1
        rgb_img = bytes_to_pil_image(imgd[2])

        input_tensor = torch.tensor(np.array([
            preprocessing(x).numpy()
            for x in [rgb_img]
        ])).to(device)

        cam = GradCAM(model=model,
                      target_layers=target_layers,
                      use_cuda=torch.cuda.is_available())

        cam.batch_size = 32

        # AblationCAM and ScoreCAM have batched implementations.
        # You can override the internal batch size for faster computation.
        grayscale_cam = cam(input_tensor=input_tensor,
                            targets=None,
                            aug_smooth=True,
                            eigen_smooth=False)[0]

        np.save(os.path.join(e_save_dir, f'{imgd[1]}.npy'), grayscale_cam)
        plt.imsave(os.path.join(e_save_dir, f'{imgd[1]}.png'), grayscale_cam)
    shutil.make_archive(os.path.join(tmpdir, task_ticket), 'zip', e_save_dir)
    shutil.rmtree(e_save_dir)


def bytes_to_pil_image(b):
    return Image.open(io.BytesIO(base64.b64decode(b))).convert(
        'RGB')


@ebp.route('/', methods=['POST', 'GET'])
def cam_func():
    if request.method == 'GET':
        task_ticket = request.args['task_ticket']
        file_name = os.path.join(tmpdir, f'{task_ticket}.zip')
        if os.path.exists(file_name):
            # np.load in tmp folder
            # cam_array_file = os.path.join(basedir, 'tmp\' + task_name + '.zip')
            # cam_array = np.load(cam_array_file)
            # for i in range(len(cam_array)):
            return send_file(file_name, as_attachment=True)
        else:
            # TODO: should follow the restful specification
            return "no such task"

    if request.method == "POST":
        form_data = request.form
        # task_info = f"{str(time.time()).split('.')[1]}#{form_data['model_name'].lower()}#{form_data['method_name'].lower()}#{form_data['data_set_name'].lower()}#{form_data['data_set_group_name'].lower()}"
        task_info = dict(
            model_name=form_data['model_name'].lower(),
            method_name=form_data['method_name'].lower(),
            data_set_name=form_data['data_set_name'].lower(),
            data_set_group_name=form_data['data_set_group_name'].lower(),
        )
        task_ticket = ebp.request_ticket_and_start_task(
            task_info, cam_task, form_data)
        if task_ticket == None:
            return "Can not request a task ticket"
        else:
            return jsonify({
                'task_ticket': task_ticket
            })
