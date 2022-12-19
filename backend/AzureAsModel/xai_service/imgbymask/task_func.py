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

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
tmpdir = os.environ.get('COMPONENT_TMP_DIR')

if torch.backends.mps.is_built() and torch.backends.mps.is_available():
    device = torch.device("mps")

print("Pytorch device: ")
print(device)


def getmap(img_data):
    
    # plt.imshow(img_data)
    # plt.show()

    # model_pt_path = os.path.join(f"model.pt")

    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.eval()
    model.to(device)

    # model.load_state_dict(torch.load(model_pt_path))

    target_layers = [model.layer4]

    preprocessing = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    ])

    i = 0

    # explanation save dir
    e_save_dir = 'tmpdir'
    if not os.path.isdir(e_save_dir):
        os.makedirs(e_save_dir)


    for imgd in img_data:
        i += 1
        input_tensor = torch.tensor(np.array([
            preprocessing(imgd).numpy()])).to(device)

        

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
        
        np.save(os.path.join(e_save_dir, f'{filenames[i]}.npy'), grayscale_cam)
        plt.imsave(os.path.join(e_save_dir, f'{filenames[i]}.png'), grayscale_cam)

    # shutil.make_archive(os.path.join(tmpdir, task_ticket), 'zip', e_save_dir)
    # shutil.rmtree(e_save_dir)


def getmaskimg(img_data):
    cam_list = []
    e_save_dir = 'tmpdir'
    for file in os.listdir(e_save_dir):
        if file.endswith(".npy"):
            camnp = np.load(os.path.join(e_save_dir, file))
            cam_list.append(camnp)

    for imgd in img_data:
        img_data_array = np.array(imgd)
        h = img_data_array.shape[0]
        w = img_data_array.shape[1]

        
    
    for x in range(len(cam_list)):
        cam = cam_list[x]
        for i in range(h):
            for j in range(w):
                cam_on_pixel = cam[i][j]
                img_data_array[i][j] = img_data_array[i][j] * cam_on_pixel
    
# TODO: return masked image


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


def getdifference(img_data):
# TODO: get score difference







def bytes_to_pil_image(b):
    return Image.open(io.BytesIO(base64.b64decode(b))).convert(
        'RGB')


imagetest = Image.open('imgbymask\Car (289).jpeg')
image_array_tests = np.array(imagetest)

filenames = os.listdir('imgbymask\cars')
images = []
# Iterate over the filenames
for filename in filenames:
    # Check if the file is a JPEG image
    if filename.endswith('.jpeg'):
        # Open the image file
        image = Image.open('imgbymask\cars/' + filename)
        # Add the image to the list
        images.append(image)

#getmap(images)
getmaskimg(images)