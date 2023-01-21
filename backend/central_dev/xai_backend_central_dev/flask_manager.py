from dotenv import dotenv_values
import glob
import os
import json
import shutil
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


def load_env(mode, **kwargs):
    os.environ['ENV'] = mode
    print('App Mode: ', os.environ['ENV'])
    env_file = f".env.{os.environ['ENV']}"
    for f in glob.glob(os.path.join(os.getcwd(), '**', env_file), recursive=True):
        env_file = f

    for k, v in kwargs.items():
        os.environ[k] = v

    config = dotenv_values(env_file)
    for k in config.keys():
        if os.getenv(k) == None:
            os.environ[k] = config[k]


def set_app(app: Flask):
    # cors
    CORS(app, resources={r"/*": {"origins": "*"}})


class ExecutorBluePrint(Blueprint):

    def __init__(self, name, import_name, component_path, *args, mongo=True, **kwargs) -> None:

        self.context_path = kwargs['url_prefix']

        self.te = TaskExecutor(
            executor_name=name, component_path=component_path, context_path=self.context_path, mongo=mongo)

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
                exp_rs_path = os.path.join(
                    self.te.static_path, 'rs', task_ticket)

                zip_path = os.path.join(
                    self.te.static_path, 'rs', f'{task_ticket}.zip')

                if not os.path.exists(zip_path):
                    shutil.make_archive(os.path.join(self.te.static_path, 'rs', task_ticket),
                                        'zip', exp_rs_path)

                if os.path.exists(zip_path):
                    return send_file(zip_path, as_attachment=True)
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

        @self.route('/task_status', methods=['GET', 'POST'])
        def task_status():
            if request.method == 'GET':
                task_ticket = request.args['task_ticket']
                return jsonify({
                    TaskInfo.task_status: self.te.get_task_actual_staus(
                        task_ticket)
                })

        @self.route('/task', methods=['GET', 'POST'])
        def task():
            if request.method == 'GET':
                pass
            else:
                form_data = request.form
                act = form_data['act']
                # stop a task
                if act == 'stop':
                    task_ticket = form_data[TaskInfo.task_ticket]
                    self.te.terminate_process(task_ticket)

                # run a task which assigned by the central
                if act == 'run':
                    task = json.loads(form_data['task'])
                    self.te.run_the_task(task)

                if act == 'delete':
                    task_ticket = form_data[TaskInfo.task_ticket]
                    self.te.delete_the_task(task_ticket)

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
                    sys_info = self.te.keep_reg_info(
                        executor_id, endpoint_type, endpoint_url, executor_info, publisher_endpoint_url)
                    return jsonify(sys_info)

            return ""

    def get_task_executor(self):
        return self.te
