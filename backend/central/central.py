import os
import json
from flask import (
    Blueprint, request, jsonify, send_file
)

from xai_backend_central_dev.task_manager import TaskPublisher

bp = Blueprint('central_task_publisher', __name__,
               url_prefix='/task_publisher')

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.path.join(basedir, 'tmp')

task_publisher_name = 'central'

tp = TaskPublisher(task_publisher_name)


@bp.route('/executor', methods=['GET', 'POST'])
def executor():
    if request.method == 'GET':
        return jsonify(tp.get_executor())
    else:
        # executor register
        form_data = request.form
        endpoint_url = form_data['endpoint_url']
        exector_info = json.loads(form_data['executor_info'])
        exector_id = tp.register_executor_endpoint(endpoint_url, exector_info)
        return jsonify({
            'executor_id': exector_id
        })


@bp.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        # request a task info
        task_ticket = request.args.get('task_ticket')
        with_status = False if request.args.get('with_status') == None else (
            False if request.args.get('with_status') != '1' else True)
        print(with_status)
        return jsonify(tp.get_ticker_info(task_ticket, with_status))
    else:
        return ""


@bp.route('/ticket', methods=['GET', 'POST'])
def ticket():
    if request.method == 'GET':
        return ""
    else:
        # request a ticket
        form_data = request.form
        executor_id = form_data['executor_id']
        task_info = json.loads(form_data['task_info'])
        tk = tp.gen_task_ticket(executor_id, task_info)
        return jsonify({
            'task_ticket': tk
        })
