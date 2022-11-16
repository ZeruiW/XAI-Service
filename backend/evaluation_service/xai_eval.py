from . import task_manager as tm
import zipfile
from base64 import encodebytes
import io
import os
import base64
import json
import sys
from flask import (
    Blueprint, request, jsonify
)
from PIL import Image
import numpy as np
import requests
import torchvision.transforms as T

import torch
from torchvision import models

#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#print(device)
device = torch.device("cpu")

create_and_add_process = tm.create_and_add_process
terminate_process = tm.terminate_process
thread_holder_str = tm.thread_holder_str

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.path.join(basedir, 'tmp')

bp = Blueprint('evaluation', __name__, url_prefix='/evaluation/')


def inference(model, img):
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


def eval_task(xai_service_url, model_service_url, db_service_url, task_name):
    task_time, model_name, method_name, data_set_name, data_set_group_name = task_name.split(
        '|')

    print('# get exp from cam')
    exp_zip_path = os.path.join(tmpdir, f"{task_name}.zip")
    response = requests.get(f'{xai_service_url}?task_name={task_name}')
    with open(exp_zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(exp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(tmpdir, task_name))

    os.remove(exp_zip_path)

    print('# get image data')
    response = requests.get(
        db_service_url, params={
            'img_group': data_set_group_name,
            'with_img_data': 1,
        })
    # print(response)
    img_data = json.loads(response.content.decode('utf-8'))

    print('# get model pt')
    model_pt_path = os.path.join(tmpdir, f"{model_name}.pth")
    response = requests.get(
        model_service_url)
    with open(model_pt_path, "wb") as f:
        f.write(response.content)

    # load model

    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.eval()
    model.to(device)
    model.load_state_dict(torch.load(model_pt_path))

    # for igd in img_data:
    #     dcode = base64.b64decode(igd[2])
    #     img = Image.open(io.BytesIO(dcode))
    #     img.show()
    #     break

    print('# get original pred')
    original_pred = {}
    i = 0
    for img in img_data:
        sys.stdout.write(f'\r{i + 1} / {len(img_data)}')
        imgg = Image.open(io.BytesIO(base64.b64decode(img[2]))).convert('RGB')
        # imgg.show()
        rs = inference(model, imgg)[0].cpu().detach().numpy()
        original_pred[img[1]] = rs
        i += 1

    print('# mask pred')

    def get_cam_data(img_name):
        # print(os.path.join(tmpdir, task_name, f'{img_name}.npy'))
        with open(os.path.join(tmpdir, task_name, f'{img_name}.npy'), 'rb') as f:
            d = np.load(f)
            # print(d.shape)
            return d

    pred_data = {}

    cam_method_name = ['grad-cam']

    for cam_method in cam_method_name:
        pred_data[cam_method] = []
        for i in range(len(img_data)):
            img = img_data[i]
            sys.stdout.write(f'\r{i + 1} / {len(img_data)}')
            # print(img_path)
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
            # new_img.show()

            rs2 = inference(model, new_img)[0].cpu().detach().numpy()

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
        score_save_path = os.path.join(tmpdir, task_name,
                                       f'{cam_method}-rs.npy')
        np.save(score_save_path, pred_data[cam_method])

    prediction_change = {}
    prediction_change_distance = {}

    for cam_method in cam_method_name:
        score_save_path = os.path.join(tmpdir, task_name,
                                       f'{cam_method}-rs.npy')
        pc_save_path = os.path.join(tmpdir, task_name,
                                    f'{cam_method}-predictionchange.npy')
        pcd_save_path = os.path.join(tmpdir, task_name,
                                     f'{cam_method}-predictionchangedistance.npy')
        prediction_change[cam_method] = []
        prediction_change_distance[cam_method] = []
        with open(score_save_path, 'rb') as f:
            data = np.load(f, allow_pickle=True)
            for d in data:
                file_name = d[0]
                ground_truth_label_idx = d[1]
                original_pred = d[2]
                mask_pred = d[3]

                score_in_original = original_pred[ground_truth_label_idx]
                score_in_mask = mask_pred[ground_truth_label_idx]

                prediction_change[cam_method].append(
                    abs((score_in_original - score_in_mask) / score_in_original * 100))

        n = len(prediction_change[cam_method])
        for i in range(n):
            for j in range(i + 1, n):
                dis = abs(prediction_change[cam_method][i]
                          - prediction_change[cam_method][j])
                prediction_change_distance[cam_method].append(dis)

        np.save(pc_save_path, prediction_change[cam_method])
        np.save(pcd_save_path,
                prediction_change_distance[cam_method])


@bp.route('/', methods=['POST'])
def eval():
    if request.method == 'POST':
        explanation_task_name = request.form['task_name']
        eval_task_name = f'{explanation_task_name}|eval'

        xai_service_url = request.form['xai_service_url']
        model_service_url = request.form['model_service_url']
        db_service_url = request.form['db_service_url']

        process = create_and_add_process(eval_task_name,
                                         eval_task, (xai_service_url, model_service_url, db_service_url, explanation_task_name))
        process.start()
        return jsonify({
            'task_name': eval_task_name
        })
    return "done"


@bp.route('/stability', methods=['GET'])
def stability():
    if request.method == 'GET':
        explanation_task_name = request.args['task_name']
        task_time, model_name, method_name, data_set_name, data_set_group_name = explanation_task_name.split(
            '|')
        pcd_save_path = os.path.join(
            tmpdir, explanation_task_name, f'{method_name}-predictionchangedistance.npy')
        with open(pcd_save_path, 'rb') as f:
            rs = list(np.load(f))
    return jsonify(rs)


@ bp.route('/task', methods=['GET', 'POST'])
def list_task():
    if request.method == 'GET':
        tl = thread_holder_str()
        return jsonify(tl)
    else:
        act = request.args['act']
        if act == 'stop':
            task_name = request.args['task_name']
            terminate_process(task_name)
            # print(thread_holder_str())
    return ""
