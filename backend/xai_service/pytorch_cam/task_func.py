# device = torch.device("cpu")
from pytorch_grad_cam import GradCAM, \
    HiResCAM, \
    ScoreCAM, \
    GradCAMPlusPlus, \
    AblationCAM, \
    XGradCAM, \
    EigenCAM, \
    EigenGradCAM, \
    LayerCAM, \
    FullGrad, \
    GradCAMElementWise

from PIL import Image
import torchvision.transforms as T
import torch
from torchvision import models
import shutil
import requests
import numpy as np

import json
import io
import gc
import time
import base64
import os
import matplotlib.pyplot as plt
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskStatus
from tqdm import tqdm
from GPUtil import showUtilization as gpu_usage

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.backends.mps.is_built() and torch.backends.mps.is_available():
    device = torch.device("mps")

print("Pytorch device: ")
print(device)
gpu_usage()


def cam_task(task_ticket, publisher_endpoint_url, task_parameters):
    tmpdir = os.environ.get('COMPONENT_TMP_DIR')

    # print(task_ticket, publisher_endpoint_url)
    # print(task_parameters)

    print('# get image data')
    response = requests.get(
        task_parameters[TaskInfo.db_service_url], params={
            'data_set_name': task_parameters['data_set_name'],
            'data_set_group_name': task_parameters['data_set_group_name'],
            'with_content': 1,
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

    if task_parameters['model_name'].lower().startswith('resnet'):
        print('  use resnet50')
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        target_layers = [model.layer4]
    if task_parameters['model_name'].lower().startswith('densenet'):
        print('  use densenet121')
        model = models.densenet121(
            weights=models.DenseNet121_Weights.IMAGENET1K_V1)
        target_layers = [model.features[-1]]

    if model == None:
        raise Exception("Not support model: ", task_parameters['model_name'])

    model.eval()
    model.to(device)

    model.load_state_dict(torch.load(model_pt_path))

    preprocessing = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    ])

    print("# cam gen")
    i = 0

    # explanation save dir
    local_exp_save_dir = os.path.join(tmpdir, 'rs', task_ticket, 'local')

    if not os.path.isdir(local_exp_save_dir):
        os.makedirs(local_exp_save_dir, exist_ok=True)

    cam_method = os.environ['cam_method']

    cam_kws = {
        'model': model,
        'target_layers': target_layers,
        'use_cuda': torch.cuda.is_available()
    }

    if cam_method == None or cam_method == 'grad-cam':
        cam = GradCAM(**cam_kws)

    if cam_method == 'hirescam':
        cam = HiResCAM(**cam_kws)

    if cam_method == 'scorecam':
        cam = ScoreCAM(**cam_kws)

    if cam_method == 'grad-campp':
        cam = GradCAMPlusPlus(**cam_kws)

    if cam_method == 'ablationcam':
        cam = AblationCAM(**cam_kws)

    if cam_method == 'xgrad-cam':
        cam = XGradCAM(**cam_kws)

    if cam_method == 'eigencam':
        cam = EigenCAM(**cam_kws)

    if cam_method == 'eigengrad-cam':
        cam = EigenGradCAM(**cam_kws)

    if cam_method == 'layercam':
        cam = LayerCAM(**cam_kws)

    if cam_method == 'fullgrad':
        cam = FullGrad(**cam_kws)

    if cam_method == 'grad-camew':
        cam = GradCAMElementWise(**cam_kws)

    cam.batch_size = 8

    # batch_size = 3
    # for batch_idx in tqdm(range(0, len(img_data), batch_size)):
    # # process one batch at a time
    #     batch_data = img_data[batch_idx:batch_idx + batch_size]

    #     for imgd in batch_data:
    #         file_name = imgd['name']
    #         sample_exp_path = os.path.join(local_exp_save_dir, file_name)
    #         if not os.path.isdir(sample_exp_path):
    #             os.makedirs(sample_exp_path, exist_ok=True)

    #         rgb_img = bytes_to_pil_image(imgd['content'])

    #         input_tensor = torch.tensor(np.array([
    #             preprocessing(x).numpy()
    #             for x in [rgb_img]
    #         ])).to(device)

    #         grayscale_cam = cam(input_tensor=input_tensor,
    #                             targets=None,
    #                             aug_smooth=True,
    #                             eigen_smooth=False)[0]

    #         np.save(os.path.join(sample_exp_path,
    #                 f'{file_name}.npy'), grayscale_cam)
    #         plt.imsave(os.path.join(sample_exp_path,
    #                 f'{file_name}.png'), grayscale_cam)

    #         del input_tensor
    #         del grayscale_cam

    #         gc.collect()
    #         torch.cuda.empty_cache()

    for i in tqdm(range(len(img_data))):
        imgd = img_data[i]
        file_name = imgd['name']
        sample_exp_path = os.path.join(local_exp_save_dir, file_name)
        if not os.path.isdir(sample_exp_path):
            os.makedirs(sample_exp_path, exist_ok=True)

        i += 1
        rgb_img = bytes_to_pil_image(imgd['content'])

        input_tensor = torch.tensor(np.array([
            preprocessing(x).numpy()
            for x in [rgb_img]
        ])).to(device)

        # AblationCAM and ScoreCAM have batched implementations.
        # You can override the internal batch size for faster computation.
        grayscale_cam = cam(input_tensor=input_tensor,
                            targets=None,
                            aug_smooth=True,
                            eigen_smooth=False)[0]

        np.save(os.path.join(sample_exp_path,
                f'{file_name}.npy'), grayscale_cam)
        plt.imsave(os.path.join(sample_exp_path,
                   f'{file_name}.png'), grayscale_cam)

        del input_tensor
        del grayscale_cam

        gc.collect()
        gpu_usage()
        torch.cuda.empty_cache()

    print("# cam gen done")

    return TaskStatus.finished


def bytes_to_pil_image(b):
    return Image.open(io.BytesIO(base64.b64decode(b))).convert(
        'RGB')


def cf(task_ticket):
    local_exp_save_dir = os.path.join(os.environ.get(
        'COMPONENT_STATIC_DIR'), 'rs', task_ticket)
    if os.path.exists(local_exp_save_dir):
        shutil.rmtree(local_exp_save_dir)
