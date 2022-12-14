import os
import json
from flask import (
    Blueprint, request, jsonify, send_file
)

from xai_backend_central_dev.task_manager import TaskPublisher

bp = Blueprint('central', __name__,
               url_prefix='/task_publisher')

task_publisher_name = 'central'
tp = TaskPublisher(task_publisher_name, component_path=__file__)


@bp.route('/executor', methods=['GET', 'POST'])
def executor():
    if request.method == 'GET':
        return jsonify(tp.get_executor())
    else:
        # executor register
        form_data = request.form
        executor_endpoint_url = form_data['executor_endpoint_url']
        exector_info = json.loads(form_data['executor_info'])
        publisher_endpoint_url = form_data['publisher_endpoint_url']
        exector_id = tp.register_executor_endpoint(
            executor_endpoint_url, exector_info, publisher_endpoint_url)
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
        # print(with_status)
        return jsonify(tp.get_ticket_info(task_ticket, with_status))
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


@bp.route('/pipeline', methods=['GET', 'POST'])
def pipeline():
    if request.method == 'GET':
        pipeline_id = request.args.get('pipeline_id')
        rs = tp.pipeline.get_pipeline(pipeline_id)
        return jsonify(rs)
    else:
        form_data = request.form
        act = form_data['act']
        if act == 'create':
            pipeline_name = form_data['pipeline_name']
            pipeline_info = tp.pipeline.create_pipeline(pipeline_name)
            return jsonify(pipeline_info)
        if act == 'add_task_sheet':
            pipeline_id = form_data['pipeline_id']
            task_sheet_id = form_data['task_sheet_id']
            code = tp.pipeline.add_task_sheet_to_pipeline(
                pipeline_id, task_sheet_id)
            return jsonify(code)
        if act == 'run':
            pipeline_id = form_data['pipeline_id']
            pipeline_info = tp.pipeline.run_pipeline(pipeline_id)
            return jsonify(pipeline_info)

        if act == 'duplicate':
            pipeline_id = form_data['pipeline_id']
            pipeline_info = tp.pipeline.duplicate_pipeline(pipeline_id)
            return jsonify(pipeline_info)


@bp.route('/task_sheet', methods=['GET', 'POST'])
def task_sheet():
    if request.method == 'GET':
        task_sheet_ids = request.args.get('task_sheet_ids')
        if task_sheet_ids != None:
            task_sheet_ids = json.loads(task_sheet_ids)
        rs = tp.pipeline.get_task_sheet(task_sheet_ids)
        return jsonify(rs)
    else:
        form_data = request.form
        task_type = form_data['task_type']
        payload = json.loads(form_data['payload'])
        task_sheet_id = tp.pipeline.create_task_sheet(task_type, payload)
        return jsonify({
            'task_sheet_id': task_sheet_id
        })
