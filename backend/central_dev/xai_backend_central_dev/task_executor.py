import time
import multiprocessing
import json
import requests
import os
from tinydb import TinyDB, Query

from xai_backend_central_dev.constant import ExecutorRegInfo
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.task_manager import TaskComponent


class TaskExecutor(TaskComponent):

    # TODO: executor process db
    def __init__(self, executor_name: str, component_path: str) -> None:
        super().__init__(executor_name, component_path)

        self.process_holder = {}

        c_db_path = os.path.join(
            self.db_path, f'executor_{executor_name}_db.json')
        self.db = TinyDB(c_db_path)
        print(executor_name, c_db_path)
        self.executor_reg_info_tb = self.db.table('executor_info')

    def __create_and_add_process__(self, task_ticket, func, *args, **kwargs):
        process = multiprocessing.Process(
            # WARNNING: task_ticket will be the first two arguments of the func
            target=func, args=[task_ticket, *args], kwargs={**kwargs})
        self.process_holder[task_ticket] = {
            'start_time': time.time(),
            'process': process
        }
        return process

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
    def request_task_ticket(self, task_info: dict):
        if self.get_publisher_endpoint_url() == None or self.get_executor_id() == None:
            print('Executor not register')
            return None
        else:
            response = requests.post(
                self.get_publisher_endpoint_url() + '/task_publisher/ticket',
                data={
                    'executor_id': self.get_executor_id(),
                    'task_info': json.dumps(task_info)
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

    def start_a_task(self, task_ticket, func, *args, **kwargs):
        p = self.__create_and_add_process__(task_ticket, func, *args, **kwargs)
        p.start()
        return task_ticket

    def terminate_process(self, task_ticket):
        if self.process_holder.get(task_ticket) != None:
            self.process_holder[task_ticket]['process'].terminate(
            )

    def get_task_status(self, tk):
        p = self.process_holder.get(tk)
        if p == None:
            return -1   # task not exist
        else:
            return 0 if p['process'].is_alive() else 1

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
        if task_ticket != None and self.process_holder.get(task_ticket) != None:
            status = TaskStatus.running if self.process_holder[task_ticket]['process'].is_alive(
            ) else TaskStatus.stopped
            # rs.append(f"({tk}, {status})")
            return {
                TaskInfo.task_ticket: task_ticket,
                'status': status,
                'formated_start_time': time.strftime("%m/%d/%Y, %H:%M:%S",
                                                     time.localtime(self.process_holder[task_ticket]['start_time'])),
                'start_time': self.process_holder[task_ticket]['start_time'],
            }
        else:
            rs = []
            for task_ticket in self.process_holder.keys():
                status = TaskStatus.running if self.process_holder[task_ticket]['process'].is_alive(
                ) else TaskStatus.stopped
                # rs.append(f"({tk}, {status})")
                rs.append({
                    TaskInfo.task_ticket: task_ticket,
                    'status': status,
                    'formated_start_time': time.strftime("%m/%d/%Y, %H:%M:%S",
                                                         time.localtime(self.process_holder[task_ticket]['start_time'])),
                    'start_time': self.process_holder[task_ticket]['start_time'],
                })
            return rs

    def request_ticket_and_start_task(self, task_info: dict, func, *func_args, **func_kwargs):
        task_ticket = self.request_task_ticket(task_info)
        print(f'{self.get_executor_id()} requested a ticket: {task_ticket}')
        if task_ticket != None:
            # WARNNING: executor and task_ticket will be the first two arguments of the func
            self.start_a_task(
                task_ticket, func, *func_args, **func_kwargs)
            return task_ticket
