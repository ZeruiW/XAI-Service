import zipfile
import io
import os
import time
import base64
import json
import sys
from PIL import Image
import requests
import torchvision.transforms as T
from torchvision import models
import torch
import numpy as np
import cv2

#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# print(device)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.backends.mps.is_built() and torch.backends.mps.is_available():
    device = torch.device("mps")

print("Pytorch device: ")
print(device)

tmpdir = os.environ.get('COMPONENT_TMP_DIR')


def image_to_byte_array(image: Image) -> bytes:
    # BytesIO is a fake file stored in memory
    imgByteArr = io.BytesIO()
    # image.save expects a file as a argument, passing a bytes io ins
    image.save(imgByteArr, format="JPEG")
    # Turn the BytesIO object back into a bytes object
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

# ANCHOR: this method is discard


def resnet50_prediction(model, img):
    img_transforms = T.Compose(
        [
            T.ToTensor()]
    )
    img = img_transforms(img)
    with torch.no_grad():
        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
        img = img.float()
        img = img.unsqueeze(0).sub_(mean).div_(std)

    batch = torch.cat(
        [img]
    ).to(device)

    return model(batch)


def eval_task(task_ticket, publisher_endpoint_url, task_parameters):

    # print(explanation_ticket_info)

    explanation_task_info = explanation_ticket_info['task_info']
    explanation_task_ticket = explanation_ticket_info['task_ticket']

    model_name = explanation_task_info['model_name']
    method_name = explanation_task_info['method_name']
    data_set_name = explanation_task_info['data_set_name']
    data_set_group_name = explanation_task_info['data_set_group_name']

    # print(task_time, model_name, method_name,
    #       data_set_name, data_set_group_name)

    print('# get exp from cam')
    exp_zip_path = os.path.join(
        tmpdir, f"{explanation_task_ticket}_for_eval.zip")
    response = requests.get(xai_service_url, params={
        'task_ticket': explanation_task_ticket
    })
    with open(exp_zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(exp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(tmpdir, explanation_task_ticket))

    os.remove(exp_zip_path)

    print('# get image data')
    response = requests.get(
        db_service_url, params={
            'with_img_data': 1,
            'img_group': data_set_group_name,
        })
    # print(response)
    img_data = json.loads(response.content.decode('utf-8'))

    # ANCHOR: evaluation doesn't have to do with the model structure
    # print('# get model pt')
    # model_pt_path = os.path.join(tmpdir, f"{model_name}.pth")
    # response = requests.get(
    #     model_service_url)

    # ANCHOR: generalize this part for different models
    def predict_one_img(img):
        # img.show()
        payload = {}
        files = [('image',
                  ('dummy.JPEG',
                   image_to_byte_array(img),
                   'application/octet-stream'))
                 ]
        headers = {}
        response = requests.request(
            "POST", model_service_url, headers=headers, data=payload, files=files)
        return json.loads(response.text)['dummy.JPEG']

    print('# get original pred')
    original_pred = {}
    i = 0
    for img in img_data:
        sys.stdout.write(f'\r{i + 1} / {len(img_data)}')
        img_name = img[1]
        imgg = Image.open(io.BytesIO(base64.b64decode(img[2]))).convert('RGB')
        # imgg.show()
        imgg.save(os.path.join(
            tmpdir, explanation_task_ticket, f'{img_name}_original.png'))
        rs = predict_one_img(imgg)

        original_pred[img[1]] = rs
        i += 1

    print('\r\n# mask pred')

    def get_cam_data(img_name):
        # print(os.path.join(tmpdir, task_name, f'{img_name}.npy'))
        with open(os.path.join(tmpdir, explanation_task_ticket, f'{img_name}.npy'), 'rb') as f:
            d = np.load(f)
            # print(d.shape)
            return d

    pred_data = {}

    cam_method_name = ['pt_cam']

    for cam_method in cam_method_name:
        pred_data[cam_method] = []
        for i in range(len(img_data)):
            img = img_data[i]
            sys.stdout.write(f'\r{i + 1} / {len(img_data)}')
            img_name = img[1]
            ground_truth_label_idx = int(img[4])
            imgg = Image.open(io.BytesIO(
                base64.b64decode(img[2]))).convert('RGB')

            # imgg.show()

            img_array = np.array(imgg)

            rs = original_pred[img_name]
            pred_label = np.argmax(rs)
            pred_score = rs[pred_label]
            # pred_label_key = l_idx_map[pred_label]
            # pred_label_name = kvl_map[pred_label_key]

            # print(pred_label, pred_score, class_names[pred_label])

            cam_data_array = get_cam_data(img_name)

            h, w = img_array.shape[:2]

            img_data_array_copy = img_array.copy()

            for i in range(h):
                for j in range(w):
                    cam_on_pixel = cam_data_array[i][j]
                    img_data_array_copy[i][j] = img_data_array_copy[i][j] * \
                        cam_on_pixel

            new_img = Image.fromarray(img_data_array_copy)
            new_img.save(os.path.join(
                tmpdir, explanation_task_ticket, f'{img_name}_masked.png'))
            # new_img.show()

            rs2 = predict_one_img(new_img)

            pred_label2 = np.argmax(rs2)
            pred_score2 = rs2[pred_label2]
            # pred_label_key2 = l_idx_map[pred_label2]
            # pred_label_name2 = kvl_map[pred_label_key2]

            # print('prediction change to:')
            # print(pred_label2, pred_score2, pred_label_key2, pred_label_name2)
            # print('prediction diff on original label:')

            pred_data[cam_method].append(
                [img_name, ground_truth_label_idx, rs, rs2])

            # break

        pred_data[cam_method] = np.array(pred_data[cam_method], dtype=object)
        print(f'\r\n{cam_method} done')

        # break

    print('# save score')
    for cam_method in cam_method_name:
        score_save_path = os.path.join(tmpdir, explanation_task_ticket,
                                       f'rs.npy')
        np.save(score_save_path, pred_data[cam_method])

    prediction_change = {}
    prediction_change_distance = {}
    score_map = {}

    for cam_method in cam_method_name:
        score_save_path = os.path.join(tmpdir, explanation_task_ticket,
                                       f'rs.npy')
        pc_save_path = os.path.join(tmpdir, explanation_task_ticket,
                                    f'prediction_change.npy')
        pcd_save_path = os.path.join(tmpdir, explanation_task_ticket,
                                     f'prediction_change_distance.npy')

        score_map_path = os.path.join(tmpdir, explanation_task_ticket,
                                      f'score_map.npy')
        prediction_change[cam_method] = []
        prediction_change_distance[cam_method] = []
        score_map[cam_method] = {}
        with open(score_save_path, 'rb') as f:
            data = np.load(f, allow_pickle=True)
            for d in data:
                file_name = d[0]
                ground_truth_label_idx = d[1]
                original_pred = d[2]
                mask_pred = d[3]

                score_in_original = original_pred[ground_truth_label_idx]
                score_in_mask = mask_pred[ground_truth_label_idx]

                diff = abs((score_in_original - score_in_mask) /
                           score_in_original * 100)
                score_map[cam_method][file_name] = {
                    'score_original': score_in_original,
                    'score_masked': score_in_mask,
                    'score_diff': diff,
                }

                prediction_change[cam_method].append(diff)

        n = len(prediction_change[cam_method])
        for i in range(n):
            for j in range(i + 1, n):
                dis = abs(prediction_change[cam_method][i]
                          - prediction_change[cam_method][j])
                prediction_change_distance[cam_method].append(dis)

        np.save(pc_save_path, prediction_change[cam_method])
        np.save(pcd_save_path,
                prediction_change_distance[cam_method])

        np.save(score_map_path, score_map[cam_method])

    # print(score_map)
    # print(prediction_change)
    # print(prediction_change_distance)

    # Image save
    for img in img_data:
        img_name = img[1]

        heatmap = cv2.imread(os.path.join(
            tmpdir, explanation_task_ticket, f'{img_name}.png'))
        original = cv2.imread(os.path.join(
            tmpdir, explanation_task_ticket, f'{img_name}_original.png'))
        masked = cv2.imread(os.path.join(
            tmpdir, explanation_task_ticket, f'{img_name}_masked.png'))

        im_concat = cv2.vconcat([original, heatmap, masked])
        cv2.imwrite(os.path.join(
            tmpdir, explanation_task_ticket, f'{img_name}_concat.png'), im_concat)
