import os
from flask import (
    Blueprint, request, jsonify
)
import numpy as np
import time
import subprocess
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
from . import task_func

task_executor_info = {
    'executor_name': 'evaluation_service',
    'create_time': time.time()
}

ebp = ExecutorBluePrint(
    'evaluation', __name__, component_path=__file__, url_prefix='/evaluation')
te = ebp.get_task_executor()


@ebp.route('/', methods=['POST'])
def eval():
    if request.method == 'POST':
        explanation_task_ticket = request.form['explanation_task_ticket']
        print('# get task info')
        explanation_ticket_info = te.get_ticket_info_from_central(
            explanation_task_ticket)
        eval_task_info = dict(
            task_desc="evaluate for cam explanation",
            explanation_task_ticket=explanation_task_ticket,
        )
        xai_service_url = request.form['xai_service_url']
        model_service_url = request.form['model_service_url']
        db_service_url = request.form['db_service_url']

        # eval_task_ticket = te.gen_ticket(eval_task_info)

        # # process = create_and_add_process(eval_task_name,
        # #                                  eval_task, (xai_service_url, model_service_url, db_service_url, explanation_task_name))
        # # process.start()
        # task_ticket = te.start_a_task(eval_task_ticket,
        #                               eval_task, xai_service_url, model_service_url, db_service_url, explanation_task_ticket)
        # return jsonify({
        #     'task_ticket': task_ticket
        # })
        task_ticket = te.request_ticket_and_start_task(
            eval_task_info, task_func.eval_task, xai_service_url, model_service_url, db_service_url, explanation_ticket_info)
        if task_ticket == None:
            return "Can not request a task ticket"
        else:
            return jsonify({
                'task_ticket': task_ticket
            })
    return "done"


@ebp.route('/stability', methods=['GET'])
def stability():
    if request.method == 'GET':
        explanation_task_ticket = request.args['explanation_task_ticket']
        pcd_save_path = os.path.join(
            ebp.tmp_path, explanation_task_ticket, f'prediction_change_distance.npy')
        with open(pcd_save_path, 'rb') as f:
            rs = list(np.load(f))
        rs = np.array(rs)
        # subprocess.call("$(pwd)/evaluation_service/copy_result.sh", shell=True)
    return jsonify({
        'stability': np.mean(np.abs(rs)),
        'prediction_change_distance': list(rs)
    })
