# This default renderer is used for sphinx docs only. Please delete this cell in IPython.
import plotly.io as pio
pio.renderers.default = "png"

import torch
import sklearn
import xgboost
import numpy as np
import pandas as pd
from omnixai.data.tabular import Tabular
from omnixai.preprocessing.tabular import TabularTransform
from omnixai.explainers.tabular import ShapTabular
import random
import matplotlib.pyplot as plt
import shutil
import requests
import joblib

import json
import io
import gc
import time
import base64
import os
import matplotlib.pyplot as plt
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.performance_metrics import performance_metrics
from tqdm import tqdm

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.backends.mps.is_built() and torch.backends.mps.is_available():
    device = torch.device("mps")

print("Pytorch device: ")
print(device)

basedir = os.path.abspath(os.path.dirname(__file__))

# response = requests.get(
#     'http://127.0.0.1:5009/azure_blob', params={
#         'data_set_name': 'income',
#         'data_set_group_name': 'all',
#         'with_content': 0,
#     })
# response_rs = json.loads(response.content.decode('utf-8'))
# data_content = response_rs[0]['content']
# data = base64.b64decode(data_content)

# with open('data_file.data', 'wb') as f:
#     f.write(data)




@performance_metrics
def shap_task(task_ticket, publisher_endpoint_url, task_parameters):

    #index = int(task_parameters['index'])
    print('# get tabular data and model')
    response = requests.get(
        task_parameters[TaskInfo.db_service_url], params={
            'data_set_name': task_parameters['data_set_name'],
            'data_set_group_name': 'all',
            'with_content': 1,
        })
    response_rs = json.loads(response.content.decode('utf-8'))
    data_content = response_rs[0]['content']
    data_content = base64.b64decode(data_content)
    data = np.genfromtxt(io.BytesIO(data_content), delimiter=', ', dtype=str)

    if task_parameters['data_set_group_name'] == 'all':
        index = slice(None)
    else: 
        try:
            index = int(task_parameters['data_set_group_name'])
        except ValueError:
            try:
                start, end = task_parameters['data_set_group_name'].split(":")
                index = slice(int(start), int(end) + 1)
                index_range = range(int(start), int(end) + 1)
            except ValueError:
                raise ValueError("Invalid value for index")

    #index = task_parameters['data_set_group_name']
    #data_path = 'backend/xai_service/shap_tabular/tmpdir/adult.data'
    #data = np.genfromtxt(os.path.join(data_path), delimiter=', ', dtype=str)
    # data = np.genfromtxt(decoded_content, delimiter=', ', dtype=str)
    # #save the response to a file
    # with open('backend/xai_service/shap_tabular/2adult.data', 'wb') as f:
    #     f.write(response.content[1])
    # testmodel_path = os.path.join(tmpdir, f"{task_parameters['model_name']}.txt")
    # with open(testmodel_path, "wb") as f:
    #     f.write(testmodel_path)

    model_path = os.path.join(basedir, "tmpdir", f"{task_parameters['model_name']}.sav")
    response_model = requests.get(
        task_parameters[TaskInfo.model_service_url])

    with open(model_path, "wb") as f:
        f.write(response_model.content)

    #model_path = 'backend/xai_service/shap_tabular/tmpdir/finalized_model.sav'
    feature_names = [
        "Age", "Workclass", "fnlwgt", "Education",
        "Education-Num", "Marital Status", "Occupation",
        "Relationship", "Race", "Sex", "Capital Gain",
        "Capital Loss", "Hours per week", "Country", "label"
    ]

    
    model = joblib.load(model_path)

    tabular_data = Tabular(
        data,
        feature_columns=feature_names,
        categorical_columns=[feature_names[i] for i in [1, 3, 5, 6, 7, 8, 9, 13]],
        target_column='label'
    )

    print(tabular_data)

    np.random.seed(1)
    transformer = TabularTransform().fit(tabular_data)
    class_names = transformer.class_names
    x = transformer.transform(tabular_data)
    train, test, labels_train, labels_test = \
        sklearn.model_selection.train_test_split(x[:, :-1], x[:, -1], train_size=0.80)
    print('Test accuracy: {}'.format(
        sklearn.metrics.accuracy_score(labels_test, model.predict(test))))
    
    predict_function=lambda z: model.predict_proba(transformer.transform(z))
    explainer = ShapTabular(
        training_data=tabular_data,
        predict_function=predict_function
        #nsamples=100
    )

    test_instances = transformer.invert(test)
    
    if index == slice(None):
        index_range = range(len(test_instances))
    elif isinstance(index, int):
        index_range = [index]
    index_bar = tqdm(index_range)
    for index in index_bar:
        test_x = test_instances[index]
        explanations = explainer.explain(test_x)

        local_exp_save_dir = os.path.join('backend/xai_service/shap_tabular/static', 'rs', task_ticket, 'local')
        os.makedirs(local_exp_save_dir, exist_ok=True)
        #plot_path = os.path.join(local_exp_save_dir, f'{task_ticket}plot_{index}.png')

        np.save(os.path.join(local_exp_save_dir, f'{task_ticket}_{index}.npy'), explanations)
        # with open(os.path.join(local_exp_save_dir, f'{task_ticket}_{index}.json'), 'w') as f:
        #     json.dump(explanations, f)
        plot_exp_save_dir = os.path.join('backend/xai_service/shap_tabular/static', 'rs', task_ticket, 'local', f'{task_ticket}_{index}.png')
        explanations.plot(index=0, class_names=class_names).savefig(plot_exp_save_dir)

    print("# saved")
    return TaskStatus.finished



def cf(task_ticket):
    local_exp_save_dir = os.path.join(os.environ.get(
        'COMPONENT_STATIC_DIR'), 'rs', task_ticket)
    if os.path.exists(local_exp_save_dir):
        shutil.rmtree(local_exp_save_dir)

#example of how to call the task function
#shap_task('task_ticket', 'http://127.0.0.1:5008/xgb', 27)