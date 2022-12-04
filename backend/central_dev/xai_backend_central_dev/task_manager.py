import time
import multiprocessing
import json
import random
import string
import requests
import copy


class TaskPublisher():

    def __init__(self, publisher: str) -> None:
        self.ticket_info_map = {}
        self.executor_registration = {}
        self.publisher = publisher

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
        return copy.deepcopy(self.executor_registration)

    def gen_task_name(self, task_info: dict):
        task_info = self.__feed_info__(task_info)
        return '#'.join(list(task_info.values()))

    def gen_task_ticket(self, executor_id: str, task_info: dict):
        if self.if_executor_registered(executor_id):
            task_info = self.__feed_info__(task_info)
            task_ticket = self.__get_random_string__(
                15) + '.' + task_info['__time_tail__'] + '.' + executor_id
            if self.ticket_info_map.get(executor_id) == None:
                self.ticket_info_map[executor_id] = {}
            self.ticket_info_map[executor_id][task_ticket] = dict(
                task_ticket=task_ticket,
                task_info=task_info,
                request_time=time.time()
            )
            return task_ticket
        else:
            return "executor not register"

    def get_ticker_info(self, target_ticket: str, with_status: bool):
        all_ticket_info = copy.deepcopy(self.ticket_info_map)
        if target_ticket == None:
            if with_status:
                for executor_id, ticket_infos in all_ticket_info.items():
                    executor_endpoint_url = self.executor_registration[
                        executor_id]['endpoint_url']
                    response = requests.get(
                        executor_endpoint_url + '/task')
                    executor_tasks_status = json.loads(
                        response.content.decode('utf-8'))
                    for executor_task_status in executor_tasks_status:
                        current_task_ticket = executor_task_status['task_ticket']
                        if all_ticket_info[executor_id].get(current_task_ticket) != None:
                            all_ticket_info[executor_id][current_task_ticket]['task_status'] = executor_task_status
            return all_ticket_info
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
                if with_status:
                    executor_endpoint_url = self.executor_registration[
                        find_target_task_ticket_executor_id]['endpoint_url']
                    response = requests.get(
                        executor_endpoint_url + '/task',
                        params={
                            'task_ticket': find_target_task_ticket,
                        })
                    find_target_task_ticket_info['task_status'] = json.loads(
                        response.content.decode('utf-8'))
                return find_target_task_ticket_info
            else:
                return

    def register_executor_endpoint(self, endpoint_url: str, executor_info: dict):
        executor_id = self.__get_random_string_no_low__(10)
        existed_executor_id = None
        for e_id, info in self.executor_registration.items():
            if info['executor_info'] == executor_info:
                existed_executor_id = e_id
                break
        if existed_executor_id != None:
            self.executor_registration.pop(existed_executor_id, None)
        self.executor_registration[executor_id] = dict(
            endpoint_url=endpoint_url,
            executor_info=executor_info
        )
        return executor_id

    def if_executor_registered(self, executor_id: str):
        return self.executor_registration.get(executor_id) != None


class TaskExecutor():

    def __init__(self, executor_info: str) -> None:
        self.executor_info = executor_info
        self.process_holder = {}
        self.executor_id = None
        self.publisher_endpoint = None

    def __create_and_add_process__(self, task_ticket, func, *args, **kwargs):
        process = multiprocessing.Process(
            target=func, args=[*args], kwargs={**kwargs})
        self.process_holder[task_ticket] = {
            'start_time': time.time(),
            'process': process
        }
        return process

    # should request task ticket from publisher
    def request_task_ticket(self, task_info: dict):
        if self.publisher_endpoint == None or self.executor_id == None:
            print('Executor not register')
            return None
        else:
            response = requests.post(
                self.publisher_endpoint + '/task_publisher/ticket',
                data={
                    'executor_id': self.executor_id,
                    'task_info': json.dumps(task_info)
                }
            )
            return json.loads(response.content)['task_ticket']

    # should register executor to publisher
    def register_executor_endpoint(self, endpoint_url: str, publisher_endpoint: str):
        self.publisher_endpoint = publisher_endpoint
        response = requests.post(
            self.publisher_endpoint + '/task_publisher/executor',
            data={
                'endpoint_url': endpoint_url,
                'executor_info': json.dumps(self.executor_info)
            }
        )
        self.executor_id = json.loads(response.content)['executor_id']
        return self.executor_id

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

    def thread_holder_str(self, task_ticket=None):
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
