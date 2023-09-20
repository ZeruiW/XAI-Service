#evaluation section
import time
import os
import json
import psutil
import torch
from functools import wraps
from flask import request, jsonify, Response
from radon.complexity import cc_rank, cc_visit
from radon.raw import analyze
from flask import make_response
from functools import wraps
from codecarbon import EmissionsTracker
from codecarbon.core.emissions import Emissions

api_call_count = 0

def save_to_file(data, directory, calling_filename):
    file_path = os.path.join(directory, f'{calling_filename}_performance_metrics.txt')

    with open(file_path, 'a') as f:
        f.write(json.dumps(data) + '\n')

        
def get_code_complexity(source_code):
    funcs = cc_visit(source_code)
    complexity = sum(func.complexity for func in funcs)
    return complexity

def performance_metrics(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        global api_call_count
        api_call_count += 1
        tracker = EmissionsTracker()
        tracker.start()
        # 获取开始时的资源占用和系统状态
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        start_cpu = psutil.cpu_percent()
        start_disk_io = psutil.disk_io_counters()
        start_net_io = psutil.net_io_counters()
        start_gpu_memory = torch.cuda.memory_allocated()

        # 执行被装饰的函数
        result = f(*args, **kwargs)

        # 计算响应时间
        response_time = time.time() - start_time

        # 获取结束时的资源占用和系统状态
        end_memory = psutil.virtual_memory().used
        end_cpu = psutil.cpu_percent()
        end_disk_io = psutil.disk_io_counters()
        end_net_io = psutil.net_io_counters()
        end_gpu_memory = torch.cuda.memory_allocated()

        emissions = tracker.stop()

        # 计算操作复杂度
        with open(__file__, 'r') as source_code_file:
            source_code = source_code_file.read()
            complexity = get_code_complexity(source_code)
        
        function_name = f.__name__  # 获取被装饰函数的名称

        local_variables = f.__code__.co_varnames
        variable_values = {}
        for var_name in ['data_set_name', 'data_set_group_name', 'task_ticket', 'task_parameters']:
            if var_name in local_variables:
                variable_values[var_name] = locals().get(var_name)

        performance_data = {
            'function_name': function_name,
            'response_time': response_time,
            'carbon_emissions': emissions,
            'memory_delta': end_memory - start_memory,
            'api_call_count': api_call_count,
            'cpu_usage': end_cpu - start_cpu,
            'gpu_memory_delta': end_gpu_memory - start_gpu_memory,
            'complexity': complexity,
        }
        performance_data.update(variable_values)

        calling_file_path = os.path.abspath(f.__globals__['__file__'])
        calling_directory = os.path.dirname(calling_file_path)
        calling_filename = os.path.splitext(os.path.basename(calling_file_path))[0]
                # 保存性能数据到文件
        save_to_file(performance_data, calling_directory, calling_filename)
                     
        return result

    return wrapper