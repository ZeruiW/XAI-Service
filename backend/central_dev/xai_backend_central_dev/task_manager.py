import time
import multiprocessing
import json
import random
import string
import requests
import copy
import os
import sys
from tinydb import TinyDB, Query


class TaskPublisher():

    def __init__(self, publisher: str, db_path: str) -> None:
        self.publisher = publisher

        if not os.path.exists(db_path):
            os.mkdir(db_path)

        c_db_path = os.path.join(db_path, 'central_db.json')
        self.db = TinyDB(c_db_path)
        self.ticket_info_map_tb = self.db.table('ticket_info_map')
        self.executor_registration_tb = self.db.table('executor_registration')

        # print(self.ticket_info_map_tb.all())
        # print(self.executor_registration_tb.all())

    def __get_random_string__(self, length):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def __get_random_string_no_low__(self, length):
        letters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def __feed_info__(self, task_info: dict):
        task_info['publisher'] = self.publisher
        if task_info.get('__time_tail__') == None:
            task_info['__time_tail__'] = str(time.time()).split('.')[1]
        return task_info

    def get_executor(self):
        return self.executor_registration_tb.all()

    def gen_task_name(self, task_info: dict):
        task_info = self.__feed_info__(task_info)
        return '#'.join(list(task_info.values()))

    def gen_task_ticket(self, executor_id: str, task_info: dict):
        if self.if_executor_registered(executor_id):
            task_info = self.__feed_info__(task_info)
            task_ticket = self.__get_random_string__(
                15) + '.' + task_info['__time_tail__'] + '.' + executor_id
            task_info.pop('task_ticket', None)

            executor_ticket_info = self.ticket_info_map_tb.search(
                Query().executor_id == executor_id)
            if len(executor_ticket_info) == 0:
                self.ticket_info_map_tb.insert({
                    'executor_id': executor_id,
                    'ticket_infos': {}
                })

            executor_ticket_info = self.ticket_info_map_tb.search(
                Query().executor_id == executor_id)[0]

            executor_ticket_info['ticket_infos'][task_ticket] = dict(
                # task_ticket=task_ticket,
                task_info=task_info,
                request_time=time.time()
            )

            self.ticket_info_map_tb.update(
                executor_ticket_info, Query().executor_id == executor_id)

            return task_ticket
        else:
            return "executor not register"

    def get_ticket_info(self, target_ticket: str, with_status: bool):
        all_ticket_info = self.ticket_info_map_tb.all()

        all_ticket_info_tmp = {}
        for executor_ticket_info in all_ticket_info:
            executor_id = executor_ticket_info['executor_id']
            ticket_infos = executor_ticket_info['ticket_infos']
            all_ticket_info_tmp[executor_id] = ticket_infos

        all_ticket_info = all_ticket_info_tmp

        # print(self.ticket_info_map_tb.all())

        if target_ticket == None:
            if with_status:
                for executor_id, ticket_infos in all_ticket_info.items():
                    # TODO: what if unknow executor_id
                    executor_info = self.executor_registration_tb.search(
                        Query().executor_id == executor_id)[0]

                    executor_endpoint_url = executor_info['endpoint_url']
                    response = requests.get(
                        executor_endpoint_url + '/task')
                    executor_tasks_status = json.loads(
                        response.content.decode('utf-8'))
                    for executor_task_status in executor_tasks_status:
                        current_task_ticket = executor_task_status['task_ticket']
                        if all_ticket_info[executor_id].get(current_task_ticket) != None:
                            executor_task_status.pop('task_ticket', None)
                            all_ticket_info[executor_id][current_task_ticket]['task_status'] = executor_task_status

            formated_all_ticket_info = {}
            for executor_id, ticket_infos in all_ticket_info.items():
                executor_info = self.executor_registration_tb.search(
                    Query().executor_id == executor_id)[0]

                formated_all_ticket_info[executor_id] = dict(
                    executor=executor_info,
                    ticket_infos=ticket_infos
                )

            return formated_all_ticket_info
        else:
            find_target_task_ticket = None
            find_target_task_ticket_info = None
            find_target_task_ticket_executor_id = None
            for executor_id, ticket_infos in all_ticket_info.items():
                for current_task_ticket, ticket_info in ticket_infos.items():
                    if current_task_ticket == target_ticket:
                        find_target_task_ticket = target_ticket
                        find_target_task_ticket_info = ticket_info
                        find_target_task_ticket_executor_id = executor_id
                        break
            if find_target_task_ticket_executor_id != None:
                executor_info = self.executor_registration_tb.search(
                    Query().executor_id == find_target_task_ticket_executor_id)[0]
                if with_status:

                    executor_endpoint_url = executor_info['endpoint_url']
                    response = requests.get(
                        executor_endpoint_url + '/task',
                        params={
                            'task_ticket': find_target_task_ticket,
                        })
                    executor_task_status = json.loads(
                        response.content.decode('utf-8'))
                    executor_task_status.pop('task_ticket', None)
                    find_target_task_ticket_info['task_status'] = executor_task_status
                find_target_task_ticket_info['executor'] = executor_info
                find_target_task_ticket_info['task_ticket'] = find_target_task_ticket
                return find_target_task_ticket_info
            else:
                return

    def register_executor_endpoint(self, executor_endpoint_url: str,
                                   executor_info: dict,
                                   publisher_endpoint_url: str):
        existed_executor_id = None
        all_executor_registration_info = self.executor_registration_tb.all()
        print(all_executor_registration_info)
        for e_rg_info in all_executor_registration_info:
            if e_rg_info['executor_info'] == executor_info:
                existed_executor_id = e_rg_info['executor_id']
                break

        _id = None
        if existed_executor_id != None:
            self.executor_registration_tb.update({
                'executor_id': existed_executor_id,
                'executor_info': executor_info,
                'endpoint_url': executor_endpoint_url,
            }, Query().executor_id == existed_executor_id)
            _id = existed_executor_id
        else:
            executor_id = self.__get_random_string_no_low__(10)
            self.executor_registration_tb.insert({
                'executor_id': executor_id,
                'executor_info': executor_info,
                'endpoint_url': executor_endpoint_url,
            })
            _id = executor_id

        # send reg info to executor service
        requests.post(
            executor_endpoint_url + '/task',
            data={
                'act': 'reg',
                'executor_id': _id,
                'executor_endpoint_url': executor_endpoint_url,
                'executor_info': json.dumps(executor_info),
                'publisher_endpoint_url': publisher_endpoint_url
            }
        )

        return _id

    def if_executor_registered(self, executor_id: str):
        return len(self.executor_registration_tb.search(Query().executor_id == executor_id)) > 0


class TaskExecutor():

    # TODO: executor process db
    def __init__(self, db_path: str) -> None:
        self.process_holder = {}

        if not os.path.exists(db_path):
            os.mkdir(db_path)

        c_db_path = os.path.join(db_path, 'microservice_instance_db.json')
        self.db = TinyDB(c_db_path)
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
            return executor_reg_info[0]['executor_info']
        return

    def get_publisher_endpoint_url(self):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0]['publisher_endpoint_url']
        return

    def get_executor_id(self):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            return executor_reg_info[0]['executor_id']
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
            return json.loads(response.content)['task_ticket']

    # should register executor to publisher
    def keep_reg_info(self, executor_id,  endpoint_url: str, executor_info, publisher_endpoint_url: str):
        executor_reg_info = self.executor_reg_info_tb.all()
        if len(executor_reg_info) > 0:
            # remove exicting reg info
            # one service instance, one record in reg info db
            self.executor_reg_info_tb.truncate()

        self.executor_reg_info_tb.insert({
            'executor_id': executor_id,
            'endpoint_url': endpoint_url,
            'executor_info': json.loads(executor_info),
            'publisher_endpoint_url': publisher_endpoint_url,
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
                    'task_ticket': target_ticket,
                }
            )
            return json.loads(response.content)

    def process_holder_str(self, task_ticket=None):
        if task_ticket != None and self.process_holder.get(task_ticket) != None:
            status = 'Running' if self.process_holder[task_ticket]['process'].is_alive(
            ) else "Stoped"
            # rs.append(f"({tk}, {status})")
            return {
                'task_ticket': task_ticket,
                'status': status,
                'formated_start_time': time.strftime("%m/%d/%Y, %H:%M:%S",
                                                     time.localtime(self.process_holder[task_ticket]['start_time'])),
                'start_time': self.process_holder[task_ticket]['start_time'],
            }
        else:
            rs = []
            for tk in self.process_holder.keys():
                status = 'Running' if self.process_holder[tk]['process'].is_alive(
                ) else "Stoped"
                # rs.append(f"({tk}, {status})")
                rs.append({
                    'task_ticket': tk,
                    'status': status,
                    'formated_start_time': time.strftime("%m/%d/%Y, %H:%M:%S",
                                                         time.localtime(self.process_holder[tk]['start_time'])),
                    'start_time': self.process_holder[tk]['start_time'],
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
