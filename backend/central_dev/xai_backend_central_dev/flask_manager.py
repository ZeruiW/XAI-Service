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

    def __init__(self, name, import_name, *args, task_executor_info: dict, **kwargs) -> None:

        self.te = task_manager.TaskExecutor(task_executor_info)

        super().__init__(name, import_name, *args, **kwargs)

        @self.route('/task', methods=['GET', 'POST'])
        def task():
            if request.method == 'GET':
                # get task status
                task_ticket = request.args.get('task_ticket')
                tl = self.te.thread_holder_str(task_ticket)
                return jsonify(tl)
            else:
                # get stop a task or register executor
                form_data = request.form
                act = form_data['act']
                if act == 'stop':
                    task_ticket = form_data['task_ticket']
                    self.te.terminate_process(task_ticket)
                    # print(thread_holder_str())
                if act == 'reg':
                    endpoint_url = form_data['endpoint_url']
                    publisher_endpoint = form_data['publisher_endpoint']
                    executor_id = self.te.register_executor_endpoint(
                        endpoint_url, publisher_endpoint)
                    return jsonify({
                        'executor_id': executor_id
                    })
            return ""

    def get_task_executor(self):
        return self.te

    def request_ticket_and_start_task(self, task_info: dict, func, *func_args, **func_kwargs):
        task_ticket = self.te.request_task_ticket(task_info)
        print(f'{self.te.executor_id} requested a ticket: {task_ticket}')
        if task_ticket != None:
            # WARNNING: task_ticket will be the first arguments of the func
            self.te.start_a_task(
                task_ticket, func, *func_args, **func_kwargs)
            return task_ticket
