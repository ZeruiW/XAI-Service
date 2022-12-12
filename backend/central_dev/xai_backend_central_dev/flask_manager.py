from dotenv import load_dotenv, dotenv_values
import glob
import os
from flask import (
    Blueprint, request, jsonify,
)
from . import task_manager


def create_tmp_dir(service_init_path):
    basedir = os.path.abspath(os.path.dirname(service_init_path))
    tmpdir = os.path.join(basedir, 'tmp')
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)


def load_env(app):
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

        self.te = task_manager.TaskExecutor(
            executor_name=name, component_path=component_path)

        super().__init__(name, import_name, *args, **kwargs)

        self.tmp_path = self.te.tmp_path

        @self.route('/task', methods=['GET', 'POST'])
        def task():
            if request.method == 'GET':
                # get task status
                task_ticket = request.args.get('task_ticket')
                tl = self.te.process_holder_str(task_ticket)
                return jsonify(tl)
            else:
                # get stop a task or register executor
                form_data = request.form
                act = form_data['act']
                if act == 'stop':
                    task_ticket = form_data['task_ticket']
                    self.te.terminate_process(task_ticket)
                    # print(process_holder_str())
                if act == 'reg':
                    executor_id = form_data['executor_id']
                    endpoint_url = form_data['executor_endpoint_url']
                    executor_info = form_data['executor_info']
                    publisher_endpoint_url = form_data['publisher_endpoint_url']
                    executor_id = self.te.keep_reg_info(
                        executor_id, endpoint_url, executor_info, publisher_endpoint_url)
                    return jsonify({
                        'executor_id': executor_id
                    })
            return ""

        @self.route('/executor', methods=['POST'])
        def exe():
            if request.method == 'POST':
                # get stop a task or register executor
                form_data = request.form
                act = form_data['act']
                if act == 'reg':
                    executor_id = form_data['executor_id']
                    endpoint_url = form_data['executor_endpoint_url']
                    executor_info = form_data['executor_info']
                    publisher_endpoint_url = form_data['publisher_endpoint_url']
                    executor_id = self.te.keep_reg_info(
                        executor_id, endpoint_url, executor_info, publisher_endpoint_url)
                    return jsonify({
                        'executor_id': executor_id
                    })
            return ""

    def get_task_executor(self):
        return self.te
