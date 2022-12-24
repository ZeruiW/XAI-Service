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
    def __init__(self, executor_name: str, component_path: str) -> None:
        super().__init__(executor_name, component_path)

        self.process_holder = {}

        self.db = TinyDB(self.executor_db_path)
        # print(executor_name, c_db_path)
        self.executor_reg_info_tb = self.db.table('executor_info')

        # this keep the task parameters in db
        self.executor_task_list_tb = self.db.table('executor_list_info')
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

    def update_task_status_locally(self, task_ticket, status):
        task = self.executor_task_list_tb.search(
            Query().task_ticket == task_ticket)[0]
        task['status'] = status
        self.executor_task_list_tb.update(
            task, Query().task_ticket == task_ticket)

    def execution_call_back(self, status, task_ticket, process):
        process.close()
        self.update_task_status_locally(task_ticket, status)
        # TODO: send status to central

    def start_a_task(self, task_ticket, function, task_paramenters):
        process = multiprocessing.Pool()

        as_rs = process.apply_async(function, args=[
            task_ticket, self.get_publisher_endpoint_url(), task_paramenters],
            callback=lambda status: self.execution_call_back(status, task_ticket, process))

        self.process_holder[task_ticket] = {
            'start_time': time.time(),
            'process': process,
            'as_rs': as_rs
        }

        self.update_task_status_locally(task_ticket, TaskStatus.running)

        return task_ticket

    def terminate_process(self, task_ticket):
        if self.process_holder.get(task_ticket) != None:
            self.process_holder[task_ticket]['process'].terminate(
            )

    def get_task_status(self, task_ticket):
        query = self.executor_task_list_tb.search(
            Query().task_ticket == task_ticket)

        if len(query) == 0:
            return TaskStatus.undefined
        elif len(query) == 1:
            return query[0]['status']

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

    def gen_task_status_dict(self, task_ticket):
        status = self.get_task_status(task_ticket)
        d = {
            TaskInfo.task_ticket: task_ticket,
            'status': status
        }
        if status not in {TaskStatus.undefined, TaskStatus.initialized}:
            d['formated_start_time'] = time.strftime("%m/%d/%Y, %H:%M:%S",
                                                     time.localtime(self.process_holder[task_ticket]['start_time']))
            d['start_time'] = self.process_holder[task_ticket]['start_time']

        return d

    def process_holder_str(self, task_ticket=None):
        if task_ticket != None:
            return self.gen_task_status_dict(task_ticket)
        else:
            rs = []
            for task_ticket in self.process_holder.keys():
                rs.append(self.gen_task_status_dict(task_ticket))
            return rs

    def define_task_func_map(self, key, func):
        self.task_func_map[key] = func
        return self

    # this keep all the task parameters and which function to be choose in db
    def create_a_task_with_from_central(self, task_ticket, task_name, task_function_key, task_parameters):
        # this function did not map any task function
        if self.task_func_map.get(task_function_key) == None:
            return False
        query = self.executor_task_list_tb.search(
            Query().task_ticket == task_ticket)

        # new task
        if len(query) == 0:
            self.executor_task_list_tb.insert({
                TaskInfo.task_ticket: task_ticket,
                TaskInfo.task_name: task_name,
                TaskSheet.task_function_key: task_function_key,
                TaskSheet.task_parameters: task_parameters,
                TaskSheet.task_parameters: task_parameters,
                'status': TaskStatus.initialized
            })
            return True
        # duplicate creation
        else:
            return False

    # run the task created by central
    def run_the_task(self, task_ticket):
        task = self.executor_task_list_tb.search(
            Query().task_ticket == task_ticket)[0]

        self.start_a_task(
            task[TaskInfo.task_ticket],
            self.task_func_map[task[TaskSheet.task_function_key]],
            task[TaskSheet.task_parameters]
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
