# device = torch.device("cpu")
from pytorch_grad_cam import GradCAM
from PIL import Image
import torchvision.transforms as T
import torch
from torchvision import models
import shutil
import requests
import numpy as np

import json
import io
import time
import base64
import os
import matplotlib.pyplot as plt
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskStatus

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.backends.mps.is_built() and torch.backends.mps.is_available():
    device = torch.device("mps")

print("Pytorch device: ")
print(device)


def cam_task(task_ticket, publisher_endpoint_url, task_parameters):
    tmpdir = os.environ.get('COMPONENT_TMP_DIR')
    staticdir = os.environ.get('COMPONENT_STATIC_DIR')

    # print(task_ticket, publisher_endpoint_url)
    # print(task_parameters)

    print('# get image data')
    response = requests.get(
        task_parameters[TaskInfo.db_service_url], params={
            'img_group': task_parameters['data_set_group_name'],
            'with_img_data': 1,
        })
    # print(response)
    img_data = json.loads(response.content.decode('utf-8'))

    # for igd in img_data:
    #     dcode = base64.b64decode(igd[2])
    #     img = Image.open(io.BytesIO(dcode))
    #     img.show()

    print('# get model pt')
    model_pt_path = os.path.join(
        tmpdir, f"{task_parameters['model_name']}.pth")
    response = requests.get(
        task_parameters[TaskInfo.model_service_url])
    with open(model_pt_path, "wb") as f:
        f.write(response.content)

    # load model
    # TODO: generalize this part for different models

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
    e_save_dir = os.path.join(staticdir, 'rs', task_ticket)

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

        # TODO: generalize this part for different cam method
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

    # TODO: keep this at static for now
    # shutil.rmtree(e_save_dir)

    return TaskStatus.finished


def bytes_to_pil_image(b):
    return Image.open(io.BytesIO(base64.b64decode(b))).convert(
        'RGB')


def cf(task_ticket):
    e_save_dir = os.path.join(os.environ.get(
        'COMPONENT_STATIC_DIR'), task_ticket)
    if os.path.exists(e_save_dir):
        shutil.rmtree(e_save_dir)
