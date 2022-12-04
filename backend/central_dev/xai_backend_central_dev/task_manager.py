import time
import multiprocessing
import json
import random
import string


class TaskPublisher():

    def __init__(self, publisher: str) -> None:
        self.process_holder = {}
        self.ticket_info_map = {}
        self.publisher = publisher

    def __get_random_string__(self, length):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def __feed_info__(self, task_info: dict):
        task_info['publisher'] = self.publisher
        task_info['__time_tail__'] = str(time.time()).split('.')[1]
        return task_info

    def gen_task_name(self, task_info: dict):
        task_info = self.__feed_info__(task_info)
        return '#'.join(list(task_info.values()))

    def get_ticket(self, task_info: dict):
        task_info = self.__feed_info__(task_info)
        for tk in self.ticket_info_map.keys():
            info = self.ticket_info_map[tk]
            if info == task_info:
                return tk
        return None

    def gen_ticket(self, task_info: dict):
        task_info = self.__feed_info__(task_info)
        tk = self.__get_random_string__(15) + '.' + task_info['__time_tail__']
        self.ticket_info_map[tk] = task_info
        return tk

    def get_info(self, ticket: str):
        return self.ticket_info_map.get(ticket)

    def start_a_task(self, task_ticket, func, *args, **kwargs):
        p = self.create_and_add_process(task_ticket, func, *args, **kwargs)
        p.start()
        return task_ticket

    def thread_holder_str(self):
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

    def create_and_add_process(self, task_ticket, func, *args, **kwargs):
        process = multiprocessing.Process(
            target=func, args=[*args], kwargs={**kwargs})
        self.process_holder[task_ticket] = {
            'start_time': time.time(),
            'process': process
        }
        return process

    def terminate_process(self, task_ticket):
        if self.process_holder.get(task_ticket) != None:
            self.process_holder[task_ticket]['process'].terminate(
            )
