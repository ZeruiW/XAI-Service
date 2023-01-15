import requests
import json
import time

from tinydb import Query
from xai_backend_central_dev.constant import Pipeline
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import ExecutorRegInfo

from xai_backend_central_dev.pipeline_db_helper import PipelineDB


def run_pipeline_tasks(task_ticket, task_parameters):

    xai_ready, eval_ready, pipeline,
    pipeline_db_path, xai_task_sheet, eval_task_sheet,
    executor_registration_infos

    db = PipelineDB(pipeline_db_path)

    pipeline_id = pipeline[Pipeline.pipeline_id]

    # print(xai_ready, eval_ready, pipeline_db_path)
    # print(pipeline)
    # return

    if xai_ready:
        executor_task_ticket = pipeline[Pipeline.xai_task_ticket]
        executor_id = xai_task_sheet[TaskSheet.xai_service_executor_id]
        executor_endpoint_url = __get_url_from_executor_id__(
            executor_registration_infos, executor_id)

        print(executor_task_ticket, executor_id, executor_endpoint_url)

        ticket = run_task_with_sheet(
            executor_task_ticket, executor_endpoint_url)
        pipeline[Pipeline.xai_task_status] = TaskStatus.running
        pipeline[Pipeline.xai_task_ticket] = ticket

        db.pipeline_tb.update(
            pipeline, Query().pipeline_id == pipeline_id)

        # TODO: block the program until the xai task finished
        print('xai sleep')
        time.sleep(10)

    if eval_ready:
        executor_task_ticket = pipeline[Pipeline.evaluation_task_ticket]
        executor_id = xai_task_sheet[TaskSheet.evaluation_service_executor_id]
        executor_endpoint_url = __get_url_from_executor_id__(
            executor_registration_infos, executor_id)
        ticket = run_task_with_sheet(
            executor_task_ticket, executor_endpoint_url)
        pipeline[Pipeline.evaluation_task_status] = TaskStatus.running
        pipeline[Pipeline.evaluation_task_ticket] = ticket

        db.pipeline_tb.update(
            pipeline, Query().pipeline_id == pipeline_id)

        # TODO: block the program until the eval task finished
        print('eval sleep')
        time.sleep(10)


def __get_url_from_executor_id__(executor_registration_infos, executor_id):
    for executor_info in executor_registration_infos:
        if executor_info[ExecutorRegInfo.executor_id] == executor_id:
            return executor_info[ExecutorRegInfo.executor_endpoint_url]


def run_task_with_sheet(task_ticket, executor_endpoint_url):

    payload = {
        'act': 'run',
        'task_ticket': task_ticket
    }

    response = requests.request(
        "POST", f"{executor_endpoint_url}/task", headers={}, data=payload)

    print(response.content)
    task_ticket = json.loads(
        response.content.decode('utf-8'))

    return task_ticket[TaskInfo.task_ticket]
