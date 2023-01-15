import time
import os
import json
import requests
from tinydb import TinyDB, Query

from xai_backend_central_dev.task_manager import TaskComponent, __get_random_string__, __get_random_string_no_low__

from xai_backend_central_dev.constant import Pipeline
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import TaskType
from xai_backend_central_dev.constant import ExecutorTicketInfo
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import ExecutorRegInfo
from xai_backend_central_dev.constant import Mongo

from xai_backend_central_dev.pipeline_db_helper import PipelineDB
from bson.json_util import dumps


class TaskPublisher(TaskComponent):

    def __init__(self, publisher_name: str, component_path: str, import_name: str, context_path: str) -> None:

        super().__init__(publisher_name, component_path, context_path=context_path)
        self.publisher_name = publisher_name
        self.import_name = import_name

        c_db_path = os.path.join(self.db_path, 'central_db.json')
        self.db = TinyDB(c_db_path)
        self.central_info_tb = self.db.table('central_info')

        self.pipeline = TaskPipeline(self)

        # recover activation
        central_info = self.central_info_tb.all()
        if len(central_info) == 1:
            self.publisher_endpoint_url = central_info[0]['publisher_endpoint_url']

    def is_activated(self):
        return self.publisher_endpoint_url != None

    def activate_publisher(self, publisher_endpoint_url: str):
        self.publisher_endpoint_url = publisher_endpoint_url
        central_info = self.central_info_tb.all()
        if len(central_info) == 0:
            self.central_info_tb.insert({
                'central_name': self.publisher_name,
                'publisher_endpoint_url': publisher_endpoint_url,
                'activate_time': time.time()
            })
        return self.central_info_tb.all()[0]

    def get_executor_registration_info(self, executor_id=None):
        if executor_id == None:
            return self.mondb.find(
                Mongo.executor_registration_col, {})
        else:
            return self.mondb.find_one(
                Mongo.executor_registration_col, {ExecutorRegInfo.executor_id: executor_id})

    def remove_task_ticket(self, executor_id, task_ticket):
        pass

    def gen_task_ticket(self, executor_id, task_name, task_sheet):
        if not self.is_activated() or not self.if_executor_registered(executor_id):
            return None
        else:
            task_ticket_info = {
                TaskInfo.task_ticket: __get_random_string__(
                    15) + '.' + executor_id,
                TaskInfo.executor_id: executor_id,
                TaskInfo.task_sheet_id: task_sheet[TaskSheet.task_sheet_id],
                TaskInfo.task_status: TaskStatus.initialized,
                TaskInfo.task_name: task_name,
                TaskInfo.publisher: self.publisher_name,
                TaskInfo.request_time: time.time(),
                TaskInfo.start_time: TaskInfo.empty,
                TaskInfo.end_time: TaskInfo.empty,
                TaskInfo.task_function_key: task_sheet[TaskSheet.task_function_key]
            }

            task_parameters = task_sheet[TaskSheet.task_parameters]
            executor_reg_info = self.get_executor_registration_info(
                executor_id)

            # fill executor endpoint url
            task_ticket_info[TaskInfo.executor_endpoint_url] = executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            # fill parameters with executor url
            if task_sheet[TaskSheet.db_service_executor_id] != TaskSheet.empty:
                db_executor_reg_info = self.get_executor_registration_info(
                    executor_id=task_sheet[TaskSheet.db_service_executor_id])
                if type(db_executor_reg_info) is not list:
                    task_parameters[TaskInfo.db_service_url] = db_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            if task_sheet[TaskSheet.model_service_executor_id] != TaskSheet.empty:
                model_executor_reg_info = self.get_executor_registration_info(
                    executor_id=task_sheet[TaskSheet.model_service_executor_id])
                if type(model_executor_reg_info) is not list:
                    task_parameters[TaskInfo.model_service_url] = model_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            if task_sheet[TaskSheet.xai_service_executor_id] != TaskSheet.empty:
                xai_executor_reg_info = self.get_executor_registration_info(
                    executor_id=task_sheet[TaskSheet.xai_service_executor_id])
                if type(xai_executor_reg_info) is not list:
                    task_parameters[TaskInfo.xai_service_url] = xai_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            if task_sheet[TaskSheet.evaluation_service_executor_id] != TaskSheet.empty:
                evaluation_executor_reg_info = self.get_executor_registration_info(
                    executor_id=task_sheet[TaskSheet.evaluation_service_executor_id])
                if type(evaluation_executor_reg_info) is not list:
                    task_parameters[TaskInfo.evaluation_service_url] = evaluation_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

            # add explanation task ticket to param
            if task_sheet[TaskSheet.task_type] == TaskType.evaluation:
                explanation_task_ticket = task_parameters['explanation_task_ticket']
                xai_task_ticket_info = self.get_ticket_info(
                    explanation_task_ticket)
                task_parameters['explanation_task_parameters'] = \
                    xai_task_ticket_info[TaskSheet.task_parameters]

            task_ticket_info[TaskInfo.task_parameters] = task_parameters

            self.mondb.insert_one(Mongo.task_col, task_ticket_info)

            return self.mondb.parse_json(task_ticket_info)

    def get_task_info_by_task_sheet_id(self, task_sheet_id):
        return self.mondb.find(Mongo.task_col, {
            TaskInfo.task_sheet_id: task_sheet_id
        })

    def get_ticket_info(self, target_ticket: str, with_status: bool = False):
        if target_ticket == None:
            return self.mondb.find(Mongo.task_col, {})
        else:
            return self.mondb.find_one(Mongo.task_col, {
                TaskInfo.task_ticket: target_ticket
            })

    def register_executor_endpoint(self,
                                   executor_type: str,
                                   executor_endpoint_url: str,
                                   executor_info: dict,
                                   executor_owner="Jim"):
        existed_executor_id = None
        all_executor_registration_info = self.mondb.find(
            Mongo.executor_registration_col, {})
        # print(all_executor_registration_info)
        for e_rg_info in all_executor_registration_info:
            # if url and type is the same, consider the update
            if e_rg_info[ExecutorRegInfo.executor_endpoint_url] == executor_endpoint_url \
                    and e_rg_info[ExecutorRegInfo.executor_type] == executor_type:
                existed_executor_id = e_rg_info[ExecutorRegInfo.executor_id]
                break

        _id = None
        if existed_executor_id != None:
            _id = existed_executor_id
        else:
            _id = __get_random_string_no_low__(10)

        reg_time = time.time()

        # send reg info to executor service
        resp = requests.post(
            executor_endpoint_url + '/executor',
            data={
                'act': 'reg',
                ExecutorRegInfo.executor_id: _id,
                ExecutorRegInfo.executor_owner: executor_owner,
                ExecutorRegInfo.executor_register_time: reg_time,
                ExecutorRegInfo.executor_type: executor_type,
                ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                ExecutorRegInfo.executor_info: json.dumps(executor_info),
                ExecutorRegInfo.publisher_endpoint_url: self.publisher_endpoint_url
            }
        )

        if resp.status_code == 200:
            if existed_executor_id != None:
                self.mondb.update_one(Mongo.executor_registration_col, {
                    ExecutorRegInfo.executor_id: existed_executor_id
                }, {
                    "$set": {
                        ExecutorRegInfo.executor_info: executor_info,
                    },
                    "$currentDate": {"last_modified": {"$type": "timestamp"}}
                })
            else:
                executor_reg_info = {
                    ExecutorRegInfo.executor_id: _id,
                    ExecutorRegInfo.executor_owner: executor_owner,
                    ExecutorRegInfo.executor_register_time: reg_time,
                    ExecutorRegInfo.executor_type: executor_type,
                    ExecutorRegInfo.executor_info: executor_info,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                }
                self.mondb.insert_one(Mongo.executor_registration_col,
                                      executor_reg_info)
            return _id
        else:
            return None

    def reset_all_data(self):
        # TODO: mongo reset
        pass
        # self.ticket_info_map_tb.truncate()
        # self.pipeline.pipeline_tb.truncate()
        # self.pipeline.xai_task_sheet_tb.truncate()
        # self.pipeline.evaluation_task_sheet_tb.truncate()
        # self.pipeline.prediction_task_sheet_tb.truncate()

        # exe_reg_infos = self.get_executor_registration_info()
        # for exe_reg_info in exe_reg_infos:
        #     try:
        #         requests.get(
        #             exe_reg_info[ExecutorRegInfo.executor_endpoint_url] + '/reset'
        #         )
        #     except Exception:
        #         pass

        # self.executor_registration_tb.truncate()

    def if_executor_registered(self, executor_id: str):
        return self.mondb.find_one(Mongo.executor_registration_col, {
            ExecutorRegInfo.executor_id: executor_id
        }) is not None

    def delete_executor_endpoint(self, executor_id):
        self.mondb.delete_one(Mongo.executor_registration_col, {
                              ExecutorRegInfo.executor_id: executor_id})


class TaskPipeline():

    def __init__(self, task_publisher: TaskPublisher) -> None:

        self.task_publisher = task_publisher
        self.component_name = self.task_publisher.publisher_name
        self.component_path = self.task_publisher.component_path
        self.component_path_parent = os.path.abspath(
            os.path.dirname(self.component_path))

        self.storage_path = os.path.join(
            self.component_path_parent, f'{self.component_name}_storage')
        self.import_name = self.task_publisher.import_name
        self.db_path = os.path.join(self.storage_path, 'db')

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        self.pipeline_db_path = os.path.join(
            self.db_path, 'central_pipeline_db.json')

        self.db = PipelineDB(self.pipeline_db_path)

        self.pipeline_tb = self.db.pipeline_tb

    def create_pipeline(self, pipeline_name: str):
        pipeline_id = __get_random_string_no_low__(18)
        pipeline_info = {
            Pipeline.pipeline_id: pipeline_id,
            Pipeline.created_time: time.time(),
            Pipeline.pipeline_name: pipeline_name,
            Pipeline.xai_task_sheet_id: TaskSheet.empty,
            Pipeline.xai_task_status: TaskStatus.undefined,
            Pipeline.xai_task_ticket: TaskSheet.empty,
            Pipeline.evaluation_task_sheet_id: TaskSheet.empty,
            Pipeline.evaluation_task_status: TaskStatus.undefined,
            Pipeline.evaluation_task_ticket: TaskSheet.empty,
        }

        self.task_publisher.mondb.insert_one(Mongo.pipeline_col, pipeline_info)
        return self.task_publisher.mondb.find_one(Mongo.pipeline_col, {
            Pipeline.pipeline_id: pipeline_id
        })

    def create_task_sheet(self, payload: dict):

        task_type = payload.get(TaskSheet.task_type)

        task_sheet = {
            TaskSheet.task_type: task_type,
            TaskSheet.model_service_executor_id: payload.get(TaskSheet.model_service_executor_id),
            TaskSheet.db_service_executor_id: payload.get(TaskSheet.db_service_executor_id),
            TaskSheet.xai_service_executor_id: payload.get(TaskSheet.xai_service_executor_id),
            TaskSheet.evaluation_service_executor_id: payload.get(TaskSheet.evaluation_service_executor_id),
            TaskSheet.task_sheet_name: payload.get(TaskSheet.task_sheet_name),
            TaskSheet.task_function_key: payload.get(TaskSheet.task_function_key) if payload.get(TaskSheet.task_function_key) != None else 'default',
            TaskSheet.task_parameters: json.loads(payload.get(TaskSheet.task_parameters)),
        }

        task_tb = self.task_publisher.mondb.col(Mongo.task_sheet_col)

        task_sheet[TaskSheet.task_sheet_id] = __get_random_string_no_low__(15)
        task_tb.insert_one(task_sheet)
        return task_sheet[TaskSheet.task_sheet_id]

    def update_task_status(self, task_ticket, task_status):
        self.task_publisher.mondb.update_one(Mongo.task_col, {
            TaskInfo.task_ticket: task_ticket
        }, {
            "$set": {
                TaskInfo.task_status: task_status,
                TaskInfo.end_time: time.time() if task_status == TaskStatus.finished else ''
            },
        })

    def update_pipeline_task_status(self, task_ticket, task_status):
        pipelines = self.get_pipeline()
        find = False
        task_type = None
        for pipeline in pipelines:
            if task_ticket == pipeline[Pipeline.xai_task_ticket]:
                pipeline[Pipeline.xai_task_status] = task_status
                find = True
                task_type = TaskType.xai
            if task_ticket == pipeline[Pipeline.evaluation_task_ticket]:
                pipeline[Pipeline.evaluation_task_status] = task_status
                find = True
                task_type = TaskType.evaluation
            if find:
                pipeline_id = pipeline[Pipeline.pipeline_id]
                print('update pipeline status ', pipeline_id,
                      ' ', task_ticket,  ' ', task_status)
                self.pipeline_tb.update(
                    pipeline, Query().pipeline_id == pipeline_id)
                if task_type == TaskType.xai \
                    and self.__eval_task_ready_for_run__(pipeline) \
                        and pipeline[Pipeline.xai_task_status] == TaskStatus.finished:
                    self.__run_pipeline_with_pipeline__(pipeline)

                break

    def get_pipeline(self, pipeline_id: str = None):
        if pipeline_id == None:
            return self.task_publisher.mondb.find(Mongo.pipeline_col, {})
        else:
            return self.task_publisher.mondb.find_one(Mongo.pipeline_col, {
                Pipeline.pipeline_id: pipeline_id
            })

    def get_task_sheet(self, task_sheet_ids):
        if task_sheet_ids == None:
            return self.task_publisher.mondb.find(Mongo.task_sheet_col, {})

        return self.task_publisher.mondb.find(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: {"$in": task_sheet_ids}
        })

    def add_task_to_pipeline(self, pipeline_id: str, task_name: str, task_sheet_id: str):
        pipeline = self.get_pipeline(pipeline_id)[0]

        task_sheet = self.get_task_sheet([task_sheet_id])[0]
        task_type = task_sheet[TaskSheet.task_type]

        if task_type == TaskType.xai:
            task_sheet_id_key = Pipeline.xai_task_sheet_id
            task_sheet_status_key = Pipeline.xai_task_status
            task_task_ticket_key = Pipeline.xai_task_ticket
            task_executor_id = task_sheet[TaskSheet.xai_service_executor_id]

        elif task_type == TaskType.evaluation:
            task_sheet_id_key = Pipeline.evaluation_task_sheet_id
            task_sheet_status_key = Pipeline.evaluation_task_status
            task_task_ticket_key = Pipeline.evaluation_task_ticket
            task_executor_id = task_sheet[TaskSheet.evaluation_service_executor_id]
        else:
            # the prediction task does not involve in XAI pipeline
            pass

        if pipeline[task_sheet_id_key] != TaskSheet.empty:
            return -1   # xai task already exist
        else:
            required_task = self.task_publisher.gen_task_ticket(
                task_executor_id, task_name, task_sheet)
            if required_task != None:
                pipeline[task_sheet_id_key] = task_sheet_id
                pipeline[task_sheet_status_key] = TaskStatus.initialized
                pipeline[task_task_ticket_key] = required_task[TaskInfo.task_ticket]

        self.pipeline_tb.update(pipeline, Query().pipeline_id == pipeline_id)
        return 1

    def remove_task_sheet_to_pipeline(self, pipeline_id: str, task_sheet_id: str):
        pass

    def __xai_task_ready_for_run__(self, pipeline):
        return pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty and \
            pipeline[Pipeline.xai_task_status] == TaskStatus.initialized

    def __eval_task_ready_for_run__(self, pipeline):
        return pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty and \
            pipeline[Pipeline.evaluation_task_status] == TaskStatus.initialized

    def __get_url_from_executor_id__(self, executor_id):
        for executor_info in self.task_publisher.get_executor_registration_info():
            if executor_info[ExecutorRegInfo.executor_id] == executor_id:
                return executor_info[ExecutorRegInfo.executor_endpoint_url]

    def tell_executor_to_run_task(self, task):

        self.task_publisher.mondb.update_one(Mongo.task_col, {
            TaskInfo.task_ticket: task[TaskInfo.task_ticket]
        }, {
            "$set": {
                TaskInfo.task_status: TaskStatus.running,
                TaskInfo.start_time: time.time()
            }
        })

        payload = {
            'act': 'run',
            'task': json.dumps(task)
        }
        requests.request(
            "POST", f"{task[TaskInfo.executor_endpoint_url]}/task", headers={}, data=payload)

        return task[TaskInfo.task_ticket]

    def delete_task(self, task_ticket):
        task_info = self.task_publisher.mondb.find_one(Mongo.task_col, {
            TaskInfo.task_ticket: task_ticket
        })
        payload = {
            'act': 'delete',
            'task_ticket': task_ticket
        }

        response = requests.request(
            "POST", f"{task_info[TaskInfo.executor_endpoint_url]}/task", headers={}, data=payload)

        if response.status_code == 200:
            self.task_publisher.mondb.delete_one(Mongo.task_col, {
                TaskInfo.task_ticket: task_ticket
            })

    def __run_pipeline_with_pipeline__(self, pipeline):
        pipeline_id = pipeline[Pipeline.pipeline_id]
        pipeline_status = self.get_pipeline_status(pipeline)

        if TaskStatus.initialized in pipeline_status:
            xai_ready = self.__xai_task_ready_for_run__(pipeline=pipeline)
            eval_ready = self.__eval_task_ready_for_run__(pipeline=pipeline)

            if xai_ready:
                task_ticket = pipeline[Pipeline.xai_task_ticket]
                task_status_key = Pipeline.xai_task_status
            elif eval_ready:
                task_ticket = pipeline[Pipeline.evaluation_task_ticket]
                task_status_key = Pipeline.evaluation_task_status

            if xai_ready or eval_ready:
                required_task = self.task_publisher.mondb.find_one(Mongo.task_col, {
                    TaskInfo.task_ticket: task_ticket
                })
                self.tell_executor_to_run_task(required_task)
                pipeline[task_status_key] = TaskStatus.running
                self.pipeline_tb.update(
                    pipeline, Query().pipeline_id == pipeline_id)

        return pipeline

    def run_pipeline(self, pipeline_id):
        pipeline = self.get_pipeline(pipeline_id)[0]
        return self.__run_pipeline_with_pipeline__(pipeline)

    def run_task_sheet_directly(self, task_sheet_id, task_name):
        task_sheet = self.get_task_sheet([task_sheet_id])[0]

        task_sheet = self.get_task_sheet([task_sheet_id])[0]
        task_type = task_sheet[TaskSheet.task_type]

        if task_type == TaskType.xai:
            task_executor_id = task_sheet[TaskSheet.xai_service_executor_id]

        elif task_type == TaskType.evaluation:
            task_executor_id = task_sheet[TaskSheet.evaluation_service_executor_id]
        else:
            # the prediction task does not involve in XAI pipeline
            pass

        required_task = self.task_publisher.gen_task_ticket(
            task_executor_id, task_name, task_sheet)

        if required_task != None:
            return self.tell_executor_to_run_task(required_task)
        else:
            return None

    def duplicate_pipeline(self, pipeline_id):
        src_pipeline = self.get_pipeline(pipeline_id)[0]

        pipeline_id = __get_random_string_no_low__(18)

        has_xai_task_sheet = src_pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty
        has_evaluation_task_sheet = src_pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty

        if has_xai_task_sheet:
            src_task_sheet = self.get_task_sheet(
                [src_pipeline[Pipeline.xai_task_sheet_id]])[0]
            src_task_info = self.task_publisher.get_ticket_info(
                src_pipeline[Pipeline.xai_task_ticket])
            src_task_name = src_task_info[TaskInfo.task_name]
            src_executor_id = src_task_info['executor_id']
            new_xai_task_ticket = self.task_publisher.gen_task_ticket(
                src_executor_id, src_task_name + ' Copied', src_task_sheet)[TaskInfo.task_ticket]

        if has_evaluation_task_sheet:
            src_task_sheet = self.get_task_sheet(
                [src_pipeline[Pipeline.evaluation_task_sheet_id]])[0]
            src_task_info = self.task_publisher.get_ticket_info(
                src_pipeline[Pipeline.evaluation_task_ticket])
            src_task_name = src_task_info[TaskInfo.task_name]
            src_executor_id = src_task_info['executor_id']
            new_evaluation_task_ticket = self.task_publisher.gen_task_ticket(
                src_executor_id, src_task_name + ' Copied', src_task_sheet)[TaskInfo.task_ticket]

        pipeline_info = {
            Pipeline.pipeline_id: pipeline_id,
            Pipeline.created_time: time.time(),
            Pipeline.pipeline_name: src_pipeline[Pipeline.pipeline_name] + ' Copied',
            Pipeline.xai_task_sheet_id: src_pipeline[Pipeline.xai_task_sheet_id],
            Pipeline.xai_task_status: TaskStatus.initialized if has_xai_task_sheet else TaskStatus.undefined,
            Pipeline.xai_task_ticket: new_xai_task_ticket if has_xai_task_sheet else TaskSheet.empty,
            Pipeline.evaluation_task_sheet_id: src_pipeline[Pipeline.evaluation_task_sheet_id],
            Pipeline.evaluation_task_status: TaskStatus.initialized if has_evaluation_task_sheet else TaskStatus.undefined,
            Pipeline.evaluation_task_ticket: new_evaluation_task_ticket if has_evaluation_task_sheet else TaskSheet.empty,
        }

        self.pipeline_tb.insert(pipeline_info)
        return pipeline_info

    def get_pipeline_status(self, pipeline):
        return (pipeline[Pipeline.xai_task_status], pipeline[Pipeline.evaluation_task_status])

    def check_pipeline_status(self, pipeline):
        if pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty:
            task_ticket = pipeline[Pipeline.xai_task_ticket]
            ticket_info = self.task_publisher.get_ticket_info(
                task_ticket, True)
            task_status = ticket_info[TaskInfo.task_status]
            if task_status[TaskInfo.task_status] != pipeline[Pipeline.xai_task_status]:
                pipeline[Pipeline.xai_task_status] = task_status[TaskInfo.task_status]
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline[Pipeline.pipeline_id])
            return pipeline
        if pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty:
            task_ticket = pipeline[Pipeline.evaluation_task_ticket]
            ticket_info = self.task_publisher.get_ticket_info(
                task_ticket, True)
            task_status = ticket_info[TaskInfo.task_status]
            if task_status[TaskInfo.task_status] != pipeline[Pipeline.evaluation_task_status]:
                pipeline[Pipeline.evaluation_task_status] = task_status[TaskInfo.task_status]
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline[Pipeline.pipeline_id])
            return pipeline

    def stop_a_task(self, task_ticket):
        task = self.task_publisher.mondb.find_one(Mongo.task_col, {
            TaskInfo.task_ticket: task_ticket
        })
        requests.post(
            task[TaskInfo.executor_endpoint_url] + '/task',
            data={
                'act': 'stop',
                TaskInfo.task_ticket: task_ticket
            }
        )

    def stop_pipeline(self, pipeline_id):
        pipeline = self.get_pipeline(pipeline_id)[0]
        executor_endpoint_url = None
        if pipeline[Pipeline.xai_task_status] == TaskStatus.running:
            task_sheet = self.get_task_sheet(
                [pipeline[Pipeline.xai_task_sheet_id]])[0]
            task_ticket = pipeline[Pipeline.xai_task_ticket]

            task_executor_id = task_sheet[TaskSheet.xai_service_executor_id]

            executor_endpoint_url = self.__get_url_from_executor_id__(
                task_executor_id)

        if pipeline[Pipeline.evaluation_task_status] == TaskStatus.running:
            task_sheet = self.get_task_sheet(
                [pipeline[Pipeline.evaluation_task_sheet_id]])[0]
            task_ticket = pipeline[Pipeline.evaluation_task_ticket]

            task_executor_id = task_sheet[TaskSheet.evaluation_service_executor_id]

            executor_endpoint_url = self.__get_url_from_executor_id__(
                task_executor_id)

        if executor_endpoint_url != None:
            requests.post(
                executor_endpoint_url + '/task',
                data={
                    'act': 'stop',
                    TaskInfo.task_ticket: task_ticket
                }
            )

        return self.get_pipeline(pipeline_id)[0]

    def get_task_presentation(self, task_ticket):
        task = self.task_publisher.mondb.find_one(Mongo.task_col, {
            TaskInfo.task_ticket: task_ticket
        })
        executor_endpoint_url = task[TaskInfo.executor_endpoint_url]
        response = requests.get(
            executor_endpoint_url +
            '/task_result_present',
            params={
                TaskInfo.task_ticket: task_ticket,
            }
        )

        pre = json.loads(response.content.decode('utf-8'))

        for sample_name, fs in pre['local'].items():
            for f in fs:
                f['address'] = executor_endpoint_url + f['address']

        for f in pre['global']:
            f['address'] = executor_endpoint_url + f['address']

        return pre

    def delete_pipeline(self, pipeline_id):
        # self.pipeline_tb.remove(Query().pipeline_id == pipeline_id)
        self.task_publisher.mondb.delete_one(Mongo.pipeline_col, {
            Pipeline.pipeline_id: pipeline_id
        })

    def delete_task_sheet(self, task_sheet_id):
        self.task_publisher.mondb.delete_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: task_sheet_id
        })

    def check_task_sheet_status(self, task_sheet_id):
        pass

    def check_task_status(self, task_ticket: str):
        pass

    def stop_task(self, task_ticket: str):
        pass
