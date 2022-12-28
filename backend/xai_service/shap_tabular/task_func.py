# This default renderer is used for sphinx docs only. Please delete this cell in IPython.
import plotly.io as pio
pio.renderers.default = "png"


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

import json
import io
import time
import base64
import os
import matplotlib.pyplot as plt
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskStatus
import joblib

# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# if torch.backends.mps.is_built() and torch.backends.mps.is_available():
#     device = torch.device("mps")

# print("Pytorch device: ")
# print(device)


def shap_task(task_ticket, publisher_endpoint_url, task_parameters):
    #tmpdir = os.environ.get('COMPONENT_TMP_DIR')

    # get data set TODO: generalize this part for different data sets
    # response = requests.get(
    #     task_parameters[TaskInfo.db_service_url], params={
    #         'group_name': task_parameters['data_set_group_name']
    #     })


    # response = requests.get(publisher_endpoint_url)
    # if response.status_code == 200:
    #     # Create a file object in the tmpdir directory
    #     with open('tmpdir//model.sav', 'wb') as f:
    #         # Write the content of the response to the file
    #         f.write(response.content)
    # else:
    #     print('Error: {}'.format(response.status_code))

    model_path = 'shap_tabular\\tmpdir\\finalized_model.sav'
    gbtree = joblib.load(model_path)
    
    data_path = 'shap_tabular\\tmpdir\\adult.data'
    
    feature_names = [
        "Age", "Workclass", "fnlwgt", "Education",
        "Education-Num", "Marital Status", "Occupation",
        "Relationship", "Race", "Sex", "Capital Gain",
        "Capital Loss", "Hours per week", "Country", "label"
    ]
    data = np.genfromtxt(os.path.join(data_path), delimiter=', ', dtype=str)
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
        sklearn.metrics.accuracy_score(labels_test, gbtree.predict(test))))
    
    predict_function=lambda z: gbtree.predict_proba(transformer.transform(z))
    explainer = ShapTabular(
        training_data=tabular_data,
        predict_function=predict_function,
        nsamples=100
    )
    test_instances = transformer.invert(test)
    test_x = test_instances[task_parameters]    
    
    explanations = explainer.explain(test_x)
    plot_path = os.path.join('shap_tabular\\plots', f'{task_ticket}plot_{task_parameters}.png')
    explanations.plot(index=0, class_names=class_names).savefig(plot_path)

    return explanations



def cf(task_ticket):
    e_save_dir = os.path.join(os.environ.get('COMPONENT_TMP_DIR'), task_ticket)
    shutil.rmtree(e_save_dir)


shap_task('task_ticket', 'http://127.0.0.1:5008/xgb', 27)