import os
import json
from flask import (
    Blueprint, request, jsonify, send_file
)

from xai_backend_central_dev.task_publisher import TaskPublisher
from xai_backend_central_dev.constant import Pipeline
from xai_backend_central_dev.constant import PipelineRun
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import ExecutorRegInfo
from tqdm import tqdm

bp = Blueprint('central', __name__,
               url_prefix='/task_publisher')

task_publisher_name = 'central'
tp = TaskPublisher(task_publisher_name,
                   component_path=__file__, import_name=__name__, context_path='/task_publisher')


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
        act = form_data['act']
        if act == 'reg':
            executor_endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
            executor_type = form_data[ExecutorRegInfo.executor_type]
            exector_info = json.loads(form_data[ExecutorRegInfo.executor_info])
            # publisher_endpoint_url = form_data['publisher_endpoint_url']
            exector_id = tp.register_executor_endpoint(
                executor_type,
                executor_endpoint_url,
                exector_info)
            return jsonify({
                'executor_id': exector_id
            })
        if act == 'update':
            executor_id = form_data[ExecutorRegInfo.executor_id]
            executor_endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
            exector_info = json.loads(form_data[ExecutorRegInfo.executor_info])
            # publisher_endpoint_url = form_data['publisher_endpoint_url']
            exector_id = tp.update_executor_endpoint(
                executor_id, executor_endpoint_url, exector_info)
            return jsonify({
                'executor_id': exector_id
            })

        if act == 'delete':
            executor_id = form_data[ExecutorRegInfo.executor_id]
            tp.delete_executor_endpoint(executor_id)
            return ""


@bp.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        # request a task info
        task_ticket = request.args.get('task_ticket')
        if task_ticket != None:
            with_status = False if request.args.get('with_status') == None else (
                False if request.args.get('with_status') != '1' else True)
            # print(with_status)
            return jsonify(tp.get_ticket_info(task_ticket, with_status))

        task_sheet_id = request.args.get('task_sheet_id')

        if task_sheet_id != None:
            return jsonify(tp.get_task_info_by_task_sheet_id(task_sheet_id))

        return jsonify(tp.get_all_task())
    else:
        form_data = request.form
        act = form_data['act']
        if act == 'stop':
            task_ticket = form_data['task_ticket']
            tp.pipeline.stop_a_task(task_ticket)
        if act == 'delete':
            task_ticket = form_data['task_ticket']
            tp.pipeline.delete_task(task_ticket)

        if act == 'update_task_status':
            task_ticket = form_data[TaskInfo.task_ticket]
            task_status = form_data[TaskInfo.task_status]
            running_info = form_data[TaskInfo.running_info]
            tp.pipeline.update_task_status(
                task_ticket, task_status, json.loads(running_info))

        return ""


@bp.route('/task_result', methods=['GET', 'POST'])
def task_result():
    if request.method == 'GET':
        task_ticket = request.args.get('task_ticket')
        return jsonify(tp.pipeline.get_task_presentation(task_ticket))
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


@bp.route('/pipeline_run', methods=['GET', 'POST'])
def pipeline_run():
    if request.method == 'GET':
        pipeline_id = request.args.get(Pipeline.pipeline_id)
        rs = tp.pipeline.get_pipeline_run(pipeline_id)
        return jsonify(rs)
    else:
        form_data = request.form
        act = form_data['act']
        if act == 'delete':
            pipeline_run_ticket = form_data[PipelineRun.pipeline_run_ticket]
            tp.pipeline.delete_pipeline_run(pipeline_run_ticket)

        if act == 'stop':
            pipeline_run_ticket = form_data[PipelineRun.pipeline_run_ticket]
            tp.pipeline.stop_pipeline_run(pipeline_run_ticket)
    return ""


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
            xai_task_sheet_id = form_data[Pipeline.xai_task_sheet_id]
            evaluation_task_sheet_id = form_data[Pipeline.evaluation_task_sheet_id]
            pipeline_info = tp.pipeline.create_pipeline(
                pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id)
            return jsonify(pipeline_info)
        if act == 'run':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.run_pipeline(pipeline_id)
            return jsonify(pipeline_info)

        if act == 'duplicate':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.duplicate_pipeline(pipeline_id)
            return jsonify(pipeline_info)

        if act == 'delete':
            # TODO: unable to delete when tasks are not deleted
            pipeline_id = form_data[Pipeline.pipeline_id]
            tp.pipeline.delete_pipeline(pipeline_id)

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
        act = form_data['act']
        if act == 'create':
            payload = dict(form_data)
            task_sheet_id = tp.pipeline.create_task_sheet(payload)
            return jsonify({
                'task_sheet_id': task_sheet_id
            })
        if act == 'run':
            task_sheet_id = form_data[TaskSheet.task_sheet_id]
            return jsonify({
                'task_ticket': tp.pipeline.run_task_sheet_directly(task_sheet_id)
            })
        if act == 'delete':
            # TODO: unable to delete when tasks are not deleted
            task_sheet_id = form_data[TaskSheet.task_sheet_id]
            tp.pipeline.delete_task_sheet(task_sheet_id)
            return ""


@bp.route('/provenance', methods=['GET', 'POST'])
def provenance():
    if request.method == 'GET':
        return jsonify(tp.get_provenance())


@bp.route('/reset', methods=['GET'])
def reset():
    tp.reset_all_data()
    return ""


@bp.route('/az_blob', methods=['GET', 'POST'])
def blob():
    if request.method == 'GET':
        data_set_name = request.args.get('data_set_name')
        data_set_group_name = request.args.get('data_set_group_name')
        with_content = request.args.get('with_content')

        return jsonify(tp.az.get_blobs(data_set_name, data_set_group_name, with_content != None))

    if request.method == 'POST':
        act = request.form.get('act')
        if act == 'delete':
            name_starts_with = request.form.get('name_starts_with')
            tp.az.delete_blobs(name_starts_with)
        if act == 'upload':
            files = request.files
            samples = files.getlist('samples')
            data_set_name = request.form.get('data_set_name')
            data_set_group_name = request.form.get('data_set_group_name')
            sample_metadata = files.get('sample_metadata')

            # read sample metadata
            read_sample_metadata = {}
            if sample_metadata != None and sample_metadata.content_type == 'application/json':
                read_sample_metadata = json.load(sample_metadata)

            # upload sample to blob
            for i in tqdm(range(len(samples))):
                sample = samples[i]

                blob_file_name = os.path.join(
                    data_set_name, data_set_group_name, sample.filename)

                tp.az.upload_blob(sample.stream, blob_file_name,
                                  read_sample_metadata.get(sample.filename))

    return ""
