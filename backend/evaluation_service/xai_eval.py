import os
from flask import (
    Blueprint, request, jsonify
)
import numpy as np
import time
import subprocess
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
from xai_backend_central_dev.constant import TaskInfo
from . import task_func

task_executor_info = {
    'executor_name': 'evaluation_service',
    'create_time': time.time()
}

ebp = ExecutorBluePrint(
    'evaluation', __name__, component_path=__file__, url_prefix='/evaluation')
te = ebp.get_task_executor()
te.define_task_func_map('default', task_func.eval_task)


@ebp.route('/stability', methods=['GET'])
def stability():
    if request.method == 'GET':
        task_ticket = request.args['task_ticket']
        staticdir = os.environ.get('COMPONENT_STATIC_DIR')
        # prediction change difference
        pcd_save_path = os.path.join(
            staticdir, 'rs', task_ticket, f'prediction_change_distance.npy')
        pc_save_path = os.path.join(
            staticdir, 'rs', task_ticket, f'prediction_change.npy')
        sm_save_path = os.path.join(
            staticdir, 'rs', task_ticket, f'score_map.npy')

        with open(pcd_save_path, 'rb') as f:
            pcd_rs = list(np.load(f))
        pcd_rs = np.array(pcd_rs)

        with open(pc_save_path, 'rb') as f:
            pc_rs = list(np.load(f))
        pc_rs = np.array(pc_rs)

        with open(sm_save_path, 'rb') as f:
            sm_rs = np.load(f, allow_pickle=True).item()
        # subprocess.call("$(pwd)/evaluation_service/copy_result.sh", shell=True)
    return jsonify({
        'stability': np.mean(np.abs(pcd_rs)),
        'prediction_change_distance': list(pcd_rs),
        'prediction_change': list(pc_rs),
        'score_map': sm_rs
    })
