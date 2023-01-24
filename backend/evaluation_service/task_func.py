import io
import os
import gc
import time
import base64
import json
from PIL import Image
import requests
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm

from xai_backend_central_dev.constant import TaskStatus


def image_to_byte_array(image: Image) -> bytes:
    # BytesIO is a fake file stored in memory
    imgByteArr = io.BytesIO()
    # image.save expects a file as a argument, passing a bytes io ins
    image.save(imgByteArr, format="JPEG")
    # Turn the BytesIO object back into a bytes object
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

# ANCHOR: this method is discard


def plot(all_data, save_fig_name, xl='', yl='', xa=['Grad-CAM']):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(2, 5), dpi=200)

    # plot box plot
    # ax.boxplot(all_data,
    #             showfliers=True,
    #             showmeans=True)

    parts = ax.violinplot(all_data, showmeans=False, showmedians=False,
                          showextrema=False,)

    for pc in parts['bodies']:
        # pc.set_facecolor('#029386')
        # pc.set_edgecolor('black')
        pc.set_alpha(0.4)

    quartile1, medians, quartile3 = np.percentile(
        all_data, [25, 50, 75], axis=1)
    # ax.set_title(f'Box Plot of {fi}')

    inds = np.arange(1, len(medians) + 1)
    average = np.mean(all_data, axis=1)
    stdd = np.std(all_data, ddof=1, axis=1)

    # ax.scatter(inds, medians, marker='_', color='#f97306', s=1500, zorder=3, alpha=1)
    ax.scatter(inds, average, marker='_',
               color='green', s=2000, zorder=3, alpha=1)
    for i, txt in enumerate(average):
        ax.annotate(round(average[i], 4), (inds[i],
                    average[i] + (max(average) * 0.03)))
    # ax.scatter(inds, stdd, marker='_', color='blue', s=2000, zorder=3, alpha=1)
    ax.vlines(inds, quartile1, quartile3, color='#f79fef',
              linestyle='-', lw=10, zorder=1)

    plt.yticks(fontsize=12)
    # plt.ylim([-5, 100])
    ax.yaxis.grid(True)

    plt.xticks([y + 1 for y in range(len(all_data))],
               xa,
               fontsize=12,
               #    rotation=-20,
               # weight='560'
               )
    ax.set_ylabel(yl, fontsize=14)

    plt.savefig(save_fig_name, bbox_inches='tight')


def eval_task(task_ticket, publisher_endpoint_url, task_parameters):

    tmpdir = os.environ.get('COMPONENT_TMP_DIR')

    local_eval_keep_path = os.path.join(tmpdir, 'rs', task_ticket, 'local')

    if not os.path.exists(local_eval_keep_path):
        os.makedirs(local_eval_keep_path, exist_ok=True)

    global_eval_keep_path = os.path.join(
        tmpdir, 'rs', task_ticket, 'global')

    if not os.path.exists(global_eval_keep_path):
        os.makedirs(global_eval_keep_path, exist_ok=True)

    # print(explanation_ticket_info)
    explanation_task_ticket = task_parameters['explanation_task_ticket']

    xai_service_url = task_parameters['xai_service_url']
    db_service_url = task_parameters['db_service_url']
    model_service_url = task_parameters['model_service_url']
    explanation_task_parameters = task_parameters['explanation_task_parameters']

    model_name = explanation_task_parameters['model_name']
    method_name = explanation_task_parameters['method_name']
    data_set_name = explanation_task_parameters['data_set_name']
    data_set_group_name = explanation_task_parameters['data_set_group_name']

    # print(task_time, model_name, method_name,
    #       data_set_name, data_set_group_name)

    explanation_keep_path = os.path.join(
        tmpdir, task_ticket, f'exp_{explanation_task_ticket}')

    if not os.path.exists(explanation_keep_path):
        os.makedirs(explanation_keep_path, exist_ok=True)

    sample_keep_path = os.path.join(
        tmpdir, task_ticket, f'sam_{explanation_task_ticket}')

    if not os.path.exists(sample_keep_path):
        os.makedirs(sample_keep_path, exist_ok=True)

    print('# get exp from cam')
    r1 = requests.get(
        publisher_endpoint_url + '/task_publisher/az_blob',
        params={
            'data_set_name': 'task_execution',
            'data_set_group_name': f'result/{explanation_task_ticket}',
            'with_content': 1
        })

    exp_data = json.loads(r1.content.decode('utf-8'))

    for ed in exp_data:
        decoded_str = str(ed['content'])
        sample_name, exp_file_name = ed['name'].split('/')[-2:]
        exp_of_sample_save_path = os.path.join(
            explanation_keep_path, sample_name)
        if not os.path.exists(exp_of_sample_save_path):
            os.makedirs(exp_of_sample_save_path, exist_ok=True)

        with open(os.path.join(exp_of_sample_save_path, exp_file_name), 'wb') as f:
            f.write(base64.b64decode(decoded_str))

    del exp_data
    gc.collect()

    print('# saved exp at: ', explanation_keep_path)

    def get_cam_data(img_name):
        return np.load(os.path.join(explanation_keep_path, img_name, f'{img_name}.npy'))

    def get_cam_heatmap(img_name):
        return cv2.imread(os.path.join(explanation_keep_path, img_name, f'{img_name}.png'))

    print(
        f'# get image data {db_service_url} {data_set_name} {data_set_group_name}')
    response = requests.get(
        db_service_url, params={
            'data_set_name': data_set_name,
            'data_set_group_name': data_set_group_name,
            'with_content': 1,
        })
    # print(response)
    img_data = json.loads(response.content.decode('utf-8'))

    for ed in img_data:
        decoded_str = str(ed['content'])
        sample_file_name = ed['name']

        with open(os.path.join(sample_keep_path, sample_file_name), 'wb') as f:
            f.write(base64.b64decode(decoded_str))

        del ed['content']

    gc.collect()

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

    print('# get original pred for each img')
    original_pred = {}
    i = 0
    for i in tqdm(range(len(img_data))):
        img = img_data[i]

        img_name = img['name']
        sample_exp_path = os.path.join(local_eval_keep_path, img_name)
        if not os.path.isdir(sample_exp_path):
            os.makedirs(sample_exp_path, exist_ok=True)

        imgg = Image.open(os.path.join(
            sample_keep_path, img_name)).convert('RGB')
        # imgg.show()
        imgg.save(os.path.join(
            sample_exp_path, f'{img_name}_original.png'))
        rs = predict_one_img(imgg)

        original_pred[img_name] = rs
        i += 1

    print('# do mask pred for each img')

    pred_data = {}

    cam_method_name = ['pt_cam']

    for cam_method in cam_method_name:
        pred_data[cam_method] = []
        for i in tqdm(range(len(img_data))):
            img = img_data[i]
            img_name = img['name']
            ground_truth_label_idx = int(img['metadata']['label'])
            imgg = Image.open(os.path.join(
                sample_keep_path, img_name)).convert('RGB')

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

            sample_exp_path = os.path.join(local_eval_keep_path, img_name)
            if not os.path.isdir(sample_exp_path):
                os.makedirs(sample_exp_path, exist_ok=True)

            new_img.save(os.path.join(
                sample_exp_path, f'{img_name}_masked.png'))
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

    print('# save global score')
    for cam_method in cam_method_name:
        score_save_path = os.path.join(global_eval_keep_path,
                                       f'rs.npy')
        np.save(score_save_path, pred_data[cam_method])

    prediction_change = {}
    prediction_change_distance = {}
    score_map = {}

    # global evaluation
    for cam_method in cam_method_name:
        score_save_path = os.path.join(global_eval_keep_path,
                                       f'rs.npy')
        pc_save_path = os.path.join(global_eval_keep_path,
                                    f'prediction_change.npy')
        pcd_save_path = os.path.join(global_eval_keep_path,
                                     f'prediction_change_distance.npy')

        score_map_path = os.path.join(global_eval_keep_path,
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

        plot([prediction_change[cam_method]], os.path.join(
            f'{pc_save_path}.png'), yl='Prediction Change')

        np.save(pcd_save_path,
                prediction_change_distance[cam_method])

        plot([prediction_change_distance[cam_method]], os.path.join(
            f'{pcd_save_path}.png'), yl='Prediction Chang Distance (Stability)')

        np.save(score_map_path, score_map[cam_method])

    # print(score_map)
    # print(prediction_change)
    # print(prediction_change_distance)

    # Image save
    # local evaluation result
    print("# save local result")
    for i in tqdm(range(len(img_data))):
        img = img_data[i]
        img_name = img['name']

        sample_exp_path = os.path.join(local_eval_keep_path, img_name)
        if not os.path.isdir(sample_exp_path):
            os.makedirs(sample_exp_path, exist_ok=True)

        heatmap = get_cam_heatmap(img_name)
        original = cv2.imread(os.path.join(
            sample_exp_path, f'{img_name}_original.png'))
        masked = cv2.imread(os.path.join(
            sample_exp_path, f'{img_name}_masked.png'))

        im_concat = cv2.vconcat([original, heatmap, masked])
        cv2.imwrite(os.path.join(
            sample_exp_path, f'{img_name}_concat.png'), im_concat)

    print("# evaluation done")

    return TaskStatus.finished
