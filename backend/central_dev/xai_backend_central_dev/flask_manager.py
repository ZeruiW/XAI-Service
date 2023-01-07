from dotenv import load_dotenv, dotenv_values
import glob
import os
import json
from flask import (
    Blueprint, request, jsonify, Response, send_file, Flask
)
from xai_backend_central_dev.task_executor import TaskExecutor
import xai_backend_central_dev.constant.ExecutorRegInfo as ExecutorRegInfo
import xai_backend_central_dev.constant.TaskInfo as TaskInfo
import xai_backend_central_dev.constant.TaskSheet as TaskSheet

from flask_cors import CORS


def create_tmp_dir(service_init_path):
    basedir = os.path.abspath(os.path.dirname(service_init_path))
    tmpdir = os.path.join(basedir, 'tmp')
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)


def load_env(app: Flask):
    # cors
    CORS(app, resources={r"/*": {"origins": "*"}})

    print('App Mode: ' + 'dev' if app.debug else 'prod')

    env_file = f".env.{'dev' if app.debug else 'prod'}"
    for f in glob.glob(os.path.join(os.getcwd(), '**', env_file), recursive=True):
        env_file = f

    if app.debug:
        config = dotenv_values(env_file)
        for k in config.keys():
            if os.getenv(k) == None:
                os.environ[k] = config[k]
    else:
        load_dotenv(env_file)


class ExecutorBluePrint(Blueprint):

    def __init__(self, name, import_name, component_path, *args, **kwargs) -> None:

        self.context_path = kwargs['url_prefix']

        self.te = TaskExecutor(
            executor_name=name, component_path=component_path, context_path=self.context_path)

        super().__init__(name, import_name, *args, **kwargs)

        self.tmp_path = self.te.tmp_path

        @self.route('/reset', methods=['GET'])
        def reset():
            self.te.reset()
            return ""

        @self.route('/task_result', methods=['GET'])
        def task_result():
            if request.method == 'GET':
                task_ticket = request.args['task_ticket']
                file_name = os.path.join(self.tmp_path, f'{task_ticket}.zip')
                if os.path.exists(file_name):
                    return send_file(file_name, as_attachment=True)
                else:
                    # TODO: should follow the restful specification
                    return "no such task"

        @self.route('/task_result_present', methods=['GET'])
        def task_result_present():
            if request.method == 'GET':
                task_ticket = request.args['task_ticket']
                pre = self.te.get_task_rs_presentation(task_ticket)
                return jsonify(pre)
            return ""

        @self.route('/task', methods=['GET', 'POST'])
        def task():
            if request.method == 'GET':
                # get task status
                task_ticket = request.args.get(TaskInfo.task_ticket)
                tl = self.te.process_holder_str(task_ticket)
                return jsonify(tl)
            else:
                form_data = request.form
                act = form_data['act']
                # stop a task
                if act == 'stop':
                    task_ticket = form_data[TaskInfo.task_ticket]
                    self.te.terminate_process(task_ticket)

                # create a task info which assigned by the central
                if act == 'create':
                    task_ticket = form_data[TaskInfo.task_ticket]
                    task_name = form_data[TaskInfo.task_name]
                    task_function_key = form_data[TaskSheet.task_function_key]
                    print(form_data[TaskSheet.task_parameters])
                    task_parameters = dict(json.loads(
                        form_data[TaskSheet.task_parameters]))

                    rs = self.te.create_a_task_with_from_central(
                        task_ticket,
                        task_name,
                        task_function_key,
                        task_parameters
                    )

                    if not rs:
                        return Response("", status=400)

                # run a task which assigned by the central
                if act == 'run':
                    task_ticket = form_data[TaskInfo.task_ticket]
                    self.te.run_the_task(task_ticket)
                    return jsonify({
                        TaskInfo.task_ticket: task_ticket
                    })

                # run a task which create by the executor
                if act == 'run_in_self':
                    pass

            return ""

        @self.route('/executor', methods=['POST'])
        def exe():
            if request.method == 'POST':
                # register executor
                form_data = request.form
                act = form_data['act']
                if act == 'reg' or act == 'update':
                    executor_id = form_data[ExecutorRegInfo.executor_id]
                    endpoint_type = form_data[ExecutorRegInfo.executor_type]
                    endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
                    executor_info = form_data[ExecutorRegInfo.executor_info]
                    publisher_endpoint_url = form_data[ExecutorRegInfo.publisher_endpoint_url]
                    executor_id = self.te.keep_reg_info(
                        executor_id, endpoint_type, endpoint_url, executor_info, publisher_endpoint_url)
                    return jsonify({
                        ExecutorRegInfo.executor_id: executor_id
                    })

            return ""

    def get_task_executor(self):
        return self.te
