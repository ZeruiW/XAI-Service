
import time
import multiprocessing

process_holder = {}


def thread_holder_str():
    rs = []
    for tk in process_holder.keys():
        status = 'Running' if process_holder[tk]['process'].is_alive(
        ) else "Stoped"
        # rs.append(f"({tk}, {status})")
        rs.append({
            'task_name': tk,
            'status': status,
            'formated_start_time': time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(process_holder[tk]['start_time'])),
            'start_time': process_holder[tk]['start_time'],
        })
    return rs


def create_and_add_process(task_name, func, args):
    process = multiprocessing.Process(
        target=func, args=[*args])
    process_holder[task_name] = {
        'start_time': time.time(),
        'process': process
    }
    return process


def terminate_process(task_name):
    process_holder[task_name]['process'].terminate()
