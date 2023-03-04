import shutil
import sys
import time
import multiprocessing
import json
import requests
import os
from tinydb import TinyDB, Query
import torch.multiprocessing
import traceback
import glob


from xai_backend_central_dev.constant import ExecutorRegInfo
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.task_manager import TaskComponent
from xai_backend_central_dev.task_func import task_fun_eng_emission_wrapper

import platform
import json
import psutil
import logging
import pandas as pd


def getSystemInfo():
    try:
        info = {}
        info['platform'] = platform.system()
        info['platform-release'] = platform.release()
        info['platform-version'] = platform.version()
        info['architecture'] = platform.machine()
        info['processor'] = platform.processor()
        info['ram'] = str(
            round(psutil.virtual_memory().total / (1024.0 ** 3)))+" GB"
        return info
    except Exception as e:
        logging.exception(e)


class TaskExecutor(TaskComponent):

    # TODO: executor process db
    def __init__(self, executor_name: str, component_path: str, context_path: str,  mongo=True) -> None:
        super().__init__(executor_name, component_path, context_path, mongo)

        self.process_holder = {}

        self.db = TinyDB(self.executor_db_file_path)
        self.executor_reg_info_tb = self.db.table('executor_info')

        # this keep the task and function mapping in memory
        self.task_func_map = {}
        self.em_tracker = {}

    def get_executor_info(self):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0][ExecutorRegInfo.executor_info]
        return

    def get_publisher_endpoint_url(self) -> str:
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0][ExecutorRegInfo.publisher_endpoint_url]
        return ""

    def get_executor_id(self):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0][ExecutorRegInfo.executor_id]
        return

    # should request task ticket from publisher
    def request_task_ticket(self, task_name):
        if self.get_publisher_endpoint_url() == None or self.get_executor_id() == None:
            print('Executor not register')
            return None
        else:
            response = requests.post(
                self.get_publisher_endpoint_url() + '/task_publisher/ticket',
                data={
                    'executor_id': self.get_executor_id(),
                    'task_name': task_name,
                    # 'task_sheet_id': task_sheet_id
                }
            )
            return json.loads(response.content)[TaskInfo.task_ticket]

    # should register executor to publisher
    def keep_reg_info(self, executor_id,  executor_type: str, executor_endpoint_url: str, executor_info, publisher_endpoint_url: str):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            # remove exicting reg info
            # one service instance, one record in reg info db
            self.executor_reg_info_tb.truncate()

        self.executor_reg_info_tb.insert({
            ExecutorRegInfo.executor_id: executor_id,
            ExecutorRegInfo.executor_type: executor_type,
            ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
            ExecutorRegInfo.executor_info: json.loads(executor_info),
            ExecutorRegInfo.publisher_endpoint_url: publisher_endpoint_url,
        })

        return getSystemInfo()

    def update_task_status_to_central(self, task_ticket, task_status, running_info={}):

        task_result_save_path = os.path.join(
            self.tmp_path, 'rs', task_ticket)

        task_tmp_save_path = os.path.join(
            self.tmp_path, task_ticket)

        # if os.path.exists(task_result_save_path):
        #     files = []
        #     for filename in glob.iglob(task_result_save_path + '**/**', recursive=True):
        #         if os.path.isfile(filename):
        #             just_file_name = filename.replace(
        #                 os.path.join(self.tmp_path, 'rs') + '/', '')
        #             files.append((
        #                 'samples', (just_file_name, open(
        #                     filename, 'rb'), 'application/octet-stream')
        #             ))

            # resp = requests.post(
            #     self.get_publisher_endpoint_url() + '/task_publisher/az_blob',
            #     data={
            #         'act': 'upload',
            #         'data_set_name': 'task_execution',
            #         'data_set_group_name': 'result',
            #     },
            #     files=files
            # )

            # if resp.status_code == 200:
            #     shutil.rmtree(task_result_save_path)
            #     if os.path.exists(task_tmp_save_path):
            #         shutil.rmtree(task_tmp_save_path)

        emissions = pd.read_csv(os.path.join(
            self.storage_path, 'emissions.csv'))
        emission_info = emissions.loc[emissions['project_name'] == task_ticket].to_dict(
            'records')

        if len(emission_info) > 0:
            running_info['emission_info'] = emission_info[0]

        requests.post(
            self.get_publisher_endpoint_url() + '/task_publisher/task',
            data={
                'act': 'update_task_status',
                TaskInfo.task_ticket: task_ticket,
                TaskInfo.task_status: task_status,
                TaskInfo.running_info: json.dumps(running_info)
            }
        )

    def execution_call_back(self, task_status, task_ticket, process):
        process.close()
        self.update_task_status_to_central(task_ticket, task_status)

    def error_call_back(self, err, task_ticket, process):
        process.close()
        print(f'Error occurs for task_ticket: ' + task_ticket)
        error_stack_tracking = ''.join(
            traceback.TracebackException.from_exception(err).format())
        print(error_stack_tracking)
        self.update_task_status_to_central(task_ticket, TaskStatus.error, {
            'error_stack_tracking': error_stack_tracking
        })

    def __file_present__(self, rs_files, task_ticket, scope, sample=None):
        pre = []
        for rs_file in rs_files:
            ext = rs_file.split('.')[-1].lower()
            if ext in ['png', 'jpeg']:
                pre.append({
                    'file_name': rs_file,
                    'address': f'/static/rs/{task_ticket}/{scope}/{rs_file}',
                    'file_type': 'img'
                })
            elif ext in ['npy']:
                pre.append({
                    'file_name': rs_file,
                    'address': f'/static/rs/{task_ticket}/{scope}/{rs_file}',
                    'file_type': 'npy',
                    'content': 'todo'
                })
        return pre

    def get_task_rs_presentation(self, task_ticket):
        local_task_rs_save_dir = os.path.join(
            self.static_path, 'rs', task_ticket, 'local')
        local_task_rs_pre = {}
        if os.path.exists(local_task_rs_save_dir):
            samples = os.listdir(local_task_rs_save_dir)
            for sample in samples:
                rs_files = [
                    f'{sample}/{f}' for f in os.listdir(os.path.join(local_task_rs_save_dir, sample))]
                local_task_rs_pre[sample] = self.__file_present__(
                    rs_files, task_ticket, 'local')

        global_task_rs_save_dir = os.path.join(
            self.static_path, 'rs', task_ticket, 'global')
        global_task_rs_pre = []

        if os.path.exists(global_task_rs_save_dir):
            rs_files = os.listdir(global_task_rs_save_dir)
            global_task_rs_pre.extend(
                self.__file_present__(rs_files, task_ticket, 'global'))

        return {
            'local': local_task_rs_pre,
            'global': global_task_rs_pre,
        }

    def start_a_task(self, task_ticket, function, task_paramenters):

        use_pytorch_multiprocess = False
        if task_paramenters.get('executor_config') is not None:
            if task_paramenters.get('executor_config').get('use_pytorch_multiprocess') is not None:
                use_pytorch_multiprocess = True

        if use_pytorch_multiprocess:
            try:
                torch.multiprocessing.set_start_method('spawn')
            except RuntimeError:
                pass
            process = torch.multiprocessing.Pool()
        else:
            try:
                multiprocessing.set_start_method('spawn')
            except RuntimeError:
                pass
            process = multiprocessing.Pool()

        as_rs = process.apply_async(
            task_fun_eng_emission_wrapper,
            args=[
                function, os.path.join(
                    self.storage_path), task_ticket, self.get_publisher_endpoint_url(), task_paramenters
            ],
            callback=lambda status: self.execution_call_back(
                status, task_ticket, process),
            error_callback=lambda err: self.error_call_back(err, task_ticket, process))
        st = time.time()

        self.process_holder[task_ticket] = {
            'start_time': st,
            'process': process,
            'as_rs': as_rs
        }

        return task_ticket

    def get_task_actual_staus(self, task_ticket):
        if self.process_holder.get(task_ticket) == None:
            return TaskStatus.not_exist_in_executor_process_holder
        else:
            rs = self.process_holder.get(task_ticket)
            as_rs = rs['as_rs']

            # for ready()
            # false when task is running
            # true when task is done

            # for successful()
            # raise error when task is running
            # true when task is done and not error raised
            # false when task is done and error raised
            if as_rs.ready():
                return TaskStatus.finished if as_rs.successful() else TaskStatus.error
            else:
                return TaskStatus.running

    # set cleaning function when terminating a task

    def set_clean_task_function(self, cf):
        self.cf = cf

    def terminate_process(self, task_ticket):
        if self.process_holder.get(task_ticket) != None:
            self.process_holder[task_ticket]['process'].terminate(
            )
        print('\n', 'teriminate ', task_ticket)
        self.update_task_status_to_central(task_ticket, TaskStatus.stopped)
        if hasattr(self, 'cf') and callable(self.cf):
            try:
                self.cf(task_ticket)
            except Exception:
                print('clean function error ', task_ticket)
                traceback.print_exc()

    def get_ticket_info_from_central(self, target_ticket: str):
        if self.get_publisher_endpoint_url() == None or self.get_executor_id() == None:
            print('Executor not register')
            return None
        else:
            response = requests.get(
                self.get_publisher_endpoint_url() + '/task_publisher/task',
                params={
                    TaskInfo.task_ticket: target_ticket,
                }
            )
            return json.loads(response.content)

    def define_task_func_map(self, key, func):
        self.task_func_map[key] = func
        return self

    # run the task created by central
    def run_the_task(self, task):
        self.start_a_task(
            task[TaskInfo.task_ticket],
            self.task_func_map[task[TaskSheet.task_function_key]],
            task[TaskSheet.task_parameters]
        )

    def delete_the_task(self, task_ticket):
        task_rs_path = os.path.join(self.static_path, 'rs', task_ticket)
        if os.path.exists(task_rs_path):
            shutil.rmtree(task_rs_path)

        task_rs_zip_path = os.path.join(
            self.static_path, 'rs', f'{task_ticket}.zip')
        if os.path.exists(task_rs_zip_path):
            os.remove(task_rs_zip_path)

    def request_ticket_and_start_task(self, task_name, task_function_key, task_parameters):
        pass

    def reset(self):
        self.executor_reg_info_tb.truncate()

        # remove all files in tmp
        shutil.rmtree(self.tmp_path)
        # remove all files in static/rs
        shutil.rmtree(os.path.join(self.static_path, 'rs'))

        os.mkdir(self.tmp_path)
        os.mkdir(os.path.join(self.static_path, 'rs'))
