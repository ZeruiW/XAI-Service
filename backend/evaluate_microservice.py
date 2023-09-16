import os
import requests
import time
import pandas as pd
from radon.raw import analyze
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from mccabe import get_code_complexity

def evaluate_microservice(microservice_path, microservice_url, task_volumes):
    # 收集性能数据
    performance_data = []

    for volume in task_volumes:
        start_time = time.time()
        response = requests.get(f"{microservice_url}/tasks/{volume}")
        end_time = time.time()

        duration = end_time - start_time
        performance_data.append({"volume": volume, "duration": duration})

    performance_df = pd.DataFrame(performance_data)

    # 使用 radon 和 mccabe 库评估代码质量
    with open(microservice_path, "r") as file:
        code = file.read()

    raw_metrics = analyze(code)
    cc_metrics = list(cc_visit(code))
    mi_metrics = mi_visit(code, raw_metrics.multi) 

    # 在这里，您需要实现从碳排放数据库获取排放因子的代码
    emission_factor = 0.5  # 假设为 0.5 kg CO2e/kWh

    # 计算碳足迹指标
    # ...（根据您的实际情况计算）

    return {
        "performance": performance_df,
        "raw_metrics": raw_metrics,
        "cc_metrics": cc_metrics,
        "mi_metrics": mi_metrics,
    }

# 定义 microservice 列表
microservices = [
    {
        "path": "backend/central/central.py",
        "url": "http://127.0.0.1:5006",
    },
    {
        "path": "backend/xai_service/pytorch_cam/xai_cam.py",
        "url": "http://127.0.0.1:5003",
    },
    # ... 更多 microservices
]

task_volumes = [10, 50, 100, 200]
results = []

# 遍历每个 microservice 并收集度量
for microservice in microservices:
    result = evaluate_microservice(microservice["path"], microservice["url"], task_volumes)
    results.append(result)

print(results)
# 汇总度量以评估整个系统
# ...（根据您的实际需求汇总和分析度量）
