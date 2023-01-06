import time
import multiprocessing
import json
import requests
import os
from tinydb import TinyDB, Query

from xai_backend_central_dev.constant import ExecutorRegInfo
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.task_manager import TaskComponent


class TaskExecutor(TaskComponent):

    # TODO: executor process db
    def __init__(self, executor_name: str, component_path: str, context_path: str) -> None:
        super().__init__(executor_name, component_path, context_path)

        self.process_holder = {}

        self.db = TinyDB(self.executor_db_path)
        # print(executor_name, c_db_path)
        self.executor_reg_info_tb = self.db.table('executor_info')

        # this keep the task parameters in db
        self.executor_task_info_tb = self.db.table('executor_task_info')
        # this keep the task and function mapping in memory
        self.task_func_map = {}

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
    def keep_reg_info(self, executor_id,  executor_endpoint_url: str, executor_info, publisher_endpoint_url: str):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            # remove exicting reg info
            # one service instance, one record in reg info db
            self.executor_reg_info_tb.truncate()

        self.executor_reg_info_tb.insert({
            ExecutorRegInfo.executor_id: executor_id,
            ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
            ExecutorRegInfo.executor_info: json.loads(executor_info),
            ExecutorRegInfo.publisher_endpoint_url: publisher_endpoint_url,
        })

        return self.get_executor_id()

    def update_task_info_locally(self, task_info):
        self.executor_task_info_tb.update(
            task_info, Query().task_ticket == task_info[TaskInfo.task_ticket])

    def update_task_status_to_central(self, task_ticket, task_status):
        requests.post(
            self.get_publisher_endpoint_url() + '/task_publisher/pipeline',
            data={
                'act': 'update_task_status',
                TaskInfo.task_ticket: task_ticket,
                TaskInfo.task_status: task_status
            }
        )

    def execution_call_back(self, task_status, task_ticket, process):
        process.close()
        et = time.time()
        task_info = self.get_task_info(task_ticket)
        task_info[TaskInfo.task_status] = task_status
        task_info[TaskInfo.end_time] = et
        task_info[TaskInfo.formated_end_time] = time.strftime("%m/%d/%Y, %H:%M:%S",
                                                              time.localtime(et))
        self.update_task_info_locally(task_info)
        self.update_task_status_to_central(task_ticket, task_status)

        # TODO: a callback to send task result to central db

    def __file_present__(self, rs_files, task_ticket):
        pre = []
        for rs_file in rs_files:
            ext = rs_file.split('.')[-1].lower()
            if ext in ['png', 'jpeg']:
                pre.append({
                    'file_name': rs_file,
                    'address': f'/static/rs/{task_ticket}/{rs_file}',
                    'file_type': 'img'
                })
            elif ext in ['npy']:
                pre.append({
                    'file_name': rs_file,
                    'address': f'/static/rs/{task_ticket}/{rs_file}',
                    'file_type': 'text',
                    'content': 'todo'
                })
        return pre

    def get_task_rs_presentation(self, task_ticket):
        local_task_rs_save_dir = os.path.join(
            self.static_path, 'rs', task_ticket, 'local')
        local_task_rs_pre = []
        if os.path.exists(local_task_rs_save_dir):
            rs_files = os.listdir(local_task_rs_save_dir)
            local_task_rs_pre.extend(
                self.__file_present__(rs_files, task_ticket))

        global_task_rs_save_dir = os.path.join(
            self.static_path, 'rs', task_ticket, 'global')
        global_task_rs_pre = []

        if os.path.exists(global_task_rs_save_dir):
            rs_files = os.listdir(global_task_rs_save_dir)
            global_task_rs_pre.extend(
                self.__file_present__(rs_files, task_ticket))

        return {
            'local': local_task_rs_pre,
            'global': global_task_rs_pre,
        }

    def start_a_task(self, task_ticket, function, task_paramenters):
        process = multiprocessing.Pool()

        as_rs = process.apply_async(function, args=[
            task_ticket, self.get_publisher_endpoint_url(), task_paramenters],
            callback=lambda status: self.execution_call_back(status, task_ticket, process))

        st = time.time()

        self.process_holder[task_ticket] = {
            'start_time': st,
            'process': process,
            'as_rs': as_rs
        }

        task_info = self.get_task_info(task_ticket)

        # update info
        task_info[TaskInfo.start_time] = st
        task_info[TaskInfo.formated_start_time] = time.strftime("%m/%d/%Y, %H:%M:%S",
                                                                time.localtime(st))
        task_info[TaskInfo.task_status] = TaskStatus.running

        self.update_task_info_locally(task_info)

        return task_ticket

    # set cleaning function when terminating a task
    def set_clean_task_function(self, cf):
        self.cf = cf

    def terminate_process(self, task_ticket):
        if self.process_holder.get(task_ticket) != None:
            self.process_holder[task_ticket]['process'].terminate(
            )
        print('teriminate ', task_ticket)
        task_info = self.get_task_info(task_ticket)
        task_info[TaskInfo.task_status] = TaskStatus.initialized
        self.update_task_info_locally(task_info)
        self.update_task_status_to_central(task_ticket, TaskStatus.initialized)
        if hasattr(self, 'cf') and callable(self.cf):
            try:
                self.cf(task_ticket)
            except Exception as e:
                print('clean function error ', task_ticket)
                print(e)

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

    def process_holder_str(self, task_ticket=None):
        if task_ticket != None:
            return self.get_task_info(task_ticket)
        else:
            return self.executor_task_info_tb.all()

    def define_task_func_map(self, key, func):
        self.task_func_map[key] = func
        return self

    def get_task_info(self, task_ticket=None):
        query = self.executor_task_info_tb.search(
            Query().task_ticket == task_ticket)
        if len(query) == 1:
            return query[0]
        else:
            return None

    # this keep all the task parameters and which function to be choose in db
    def create_a_task_with_from_central(self, task_ticket, task_name, task_function_key, task_parameters):
        # this function did not map any task function
        if self.task_func_map.get(task_function_key) == None:
            return False
        task_info = self.get_task_info(task_ticket)

        # new task
        if task_info == None:
            self.executor_task_info_tb.insert({
                TaskInfo.task_ticket: task_ticket,
                TaskInfo.task_name: task_name,
                TaskSheet.task_function_key: task_function_key,
                TaskSheet.task_parameters: task_parameters,
                TaskInfo.task_status: TaskStatus.initialized
            })
            return True
        # duplicate creation
        else:
            return False

    # run the task created by central
    def run_the_task(self, task_ticket):
        task_info = self.get_task_info(task_ticket)

        self.start_a_task(
            task_info[TaskInfo.task_ticket],
            self.task_func_map[task_info[TaskSheet.task_function_key]],
            task_info[TaskSheet.task_parameters]
        )

        return task_ticket

    # TODO: run the task created by executor
    def request_ticket_and_start_task(self, task_name, task_function_key, task_parameters):
        task_ticket = self.request_task_ticket(task_name)
        self.create_a_task_with_from_central(
            task_ticket, task_name, task_function_key, task_parameters)
        print(f'{self.get_executor_id()} requested a ticket: {task_ticket}')
        if task_ticket != None:
            # WARNNING: executor and task_ticket will be the first two arguments of the func
            self.run_the_task(task_ticket)
            return task_ticket
