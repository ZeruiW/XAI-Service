import plotly.io as pio
pio.renderers.default = "png"

import io
import os
import json
import sklearn
import xgboost
import base64
import copy
import numpy as np
import pandas as pd
from omnixai.data.tabular import Tabular
from omnixai.preprocessing.tabular import TabularTransform
from omnixai.explainers.tabular import ShapTabular
import random
import pickle

from flask import (
    request, jsonify, send_file, Response
)
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
import requests


basedir = os.path.abspath(os.path.dirname(__file__))

ebp = ExecutorBluePrint(
    'xgb', __name__, component_path=__file__, url_prefix='/xgb')


# Load data
feature_names = [
    "Age", "Workclass", "fnlwgt", "Education",
    "Education-Num", "Marital Status", "Occupation",
    "Relationship", "Race", "Sex", "Capital Gain",
    "Capital Loss", "Hours per week", "Country", "label"
]

data = np.genfromtxt(os.path.join(basedir, "static", "adult.data"), delimiter=', ', dtype=str)

tabular_data = Tabular(
    data,
    feature_columns=feature_names,
    categorical_columns=[feature_names[i] for i in [1, 3, 5, 6, 7, 8, 9, 13]],
    target_column='label'
)



# Train model
np.random.seed(1)
transformer = TabularTransform().fit(tabular_data)
class_names = transformer.class_names
x = transformer.transform(tabular_data)
train, test, labels_train, labels_test = \
    sklearn.model_selection.train_test_split(x[:, :-1], x[:, -1], train_size=0.80)
# print('Training data shape: {}'.format(train.shape))
# print('Test data shape:     {}'.format(test.shape))

gbtree = xgboost.XGBClassifier(n_estimators=300, max_depth=5)
gbtree.fit(train, labels_train)
print('Test accuracy: {}'.format(
    sklearn.metrics.accuracy_score(labels_test, gbtree.predict(test))))

predict_function=lambda z: gbtree.predict_proba(transformer.transform(z))


def get_tabular_data(index):
    #print(tabular_data)
    testsample = tabular_data[index]
    return testsample


def get_prediction(index):
    test_instances = transformer.invert(test)
    test_x = test_instances[index]
    return predict_function(test_x)

def save_model():
    # save the model to disk
    file_path_name = 'finalized_model.sav'
    pickle.dump(gbtree, open(os.path.join(basedir, "static", file_path_name), 'wb'))


@ebp.route('/', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        index = request.form.get('index')
        index = int(index)

        rs = get_prediction(index)

        # rs = {}
        # for i in range(len(file_name)):
        #     rs[file_name[i]] = [round(d, 6) for d in prediction[i]]
        
        return str(rs)

    elif request.method == 'GET':
        # return tabular data
        save_model()
        file_path_name = 'finalized_model.sav'
        return send_file(os.path.join(basedir, "static", file_path_name), as_attachment=True)


