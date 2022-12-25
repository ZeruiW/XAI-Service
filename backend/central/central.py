import os
import json
from flask import (
    Blueprint, request, jsonify, send_file
)

from xai_backend_central_dev.task_publisher import TaskPublisher
from xai_backend_central_dev.constant import Pipeline
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskSheet

bp = Blueprint('central', __name__,
               url_prefix='/task_publisher')

task_publisher_name = 'central'
tp = TaskPublisher(task_publisher_name,
                   component_path=__file__, import_name=__name__)


@bp.route('/publisher', methods=['GET', 'POST'])
def publisher():
    if request.method == 'GET':
        pass
        # return jsonify(tp.get_executor())
    else:
        form_data = request.form
        publisher_endpoint_url = form_data['publisher_endpoint_url']
        executor_registration_info = tp.activate_publisher(
            publisher_endpoint_url=publisher_endpoint_url)
        return jsonify(executor_registration_info)


@bp.route('/executor', methods=['GET', 'POST'])
def executor():
    if request.method == 'GET':
        return jsonify(tp.get_executor_registration_info())
    else:
        # executor register
        form_data = request.form
        executor_endpoint_url = form_data['executor_endpoint_url']
        exector_info = json.loads(form_data['executor_info'])
        # publisher_endpoint_url = form_data['publisher_endpoint_url']
        exector_id = tp.register_executor_endpoint(
            executor_endpoint_url, exector_info)
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
        task_name = form_data['task_name']
        # task_sheet_id = form_data['task_sheet_id']
        tk = tp.gen_task_ticket(executor_id, task_name)
        return jsonify({
            'task_ticket': tk
        })


@bp.route('/pipeline', methods=['GET', 'POST'])
def pipeline():
    if request.method == 'GET':
        pipeline_id = request.args.get(Pipeline.pipeline_id)
        rs = tp.pipeline.get_pipeline(pipeline_id)
        return jsonify(rs)
    else:
        form_data = request.form
        act = form_data['act']
        if act == 'create':
            pipeline_name = form_data[Pipeline.pipeline_name]
            pipeline_info = tp.pipeline.create_pipeline(pipeline_name)
            return jsonify(pipeline_info)
        if act == 'add_task':
            pipeline_id = form_data[Pipeline.pipeline_id]
            task_name = form_data[TaskInfo.task_name]
            task_sheet_id = form_data[TaskSheet.task_sheet_id]
            code = tp.pipeline.add_task_to_pipeline(
                pipeline_id, task_name, task_sheet_id)
            return jsonify(code)
        if act == 'run':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.run_pipeline(pipeline_id)
            return jsonify(pipeline_info)

        if act == 'duplicate':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.duplicate_pipeline(pipeline_id)
            return jsonify(pipeline_info)

        if act == 'update_task_status':
            task_ticket = form_data[TaskInfo.task_ticket]
            task_status = form_data[TaskInfo.task_status]
            tp.pipeline.update_pipeline_task_status(task_ticket, task_status)

        return ""


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
        payload = dict(form_data)
        task_sheet_id = tp.pipeline.create_task_sheet(payload)
        return jsonify({
            'task_sheet_id': task_sheet_id
        })
