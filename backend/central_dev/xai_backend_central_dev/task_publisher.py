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
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import ExecutorRegInfo
from xai_backend_central_dev.constant import PipelineRun
from xai_backend_central_dev.constant import Mongo

from xai_backend_central_dev.azure_blob_helper import AZ


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

        self.az = AZ()

        # ANCHOR: makeup code, will be removed when stable
        pipeline_runs = self.mondb.find(Mongo.pipeline_run_col, {})
        pipeline_run_count = {}
        for pipeline_run in pipeline_runs:
            if pipeline_run_count.get(pipeline_run[PipelineRun.pipeline_id]) == None:
                pipeline_run_count[pipeline_run[PipelineRun.pipeline_id]] = 0
            pipeline_run_count[pipeline_run[PipelineRun.pipeline_id]] += 1
            if pipeline_run.get(PipelineRun.pipeline_run_name) == None:
                new_name = pipeline_run[PipelineRun.pipeline_name] + '-#' + str(pipeline_run_count.get(
                    pipeline_run[PipelineRun.pipeline_id]))
                self.mondb.update_one(Mongo.pipeline_run_col, {
                    PipelineRun.pipeline_run_ticket: pipeline_run[PipelineRun.pipeline_run_ticket]
                }, {
                    "$set": {
                        PipelineRun.pipeline_run_name: new_name
                    }
                })

        tasks = self.mondb.find(Mongo.task_col, {})
        for task in tasks:
            if task.get(TaskInfo.task_sheet_name) == None:
                task_sheet = self.mondb.find_one(Mongo.task_sheet_col, {
                    TaskSheet.task_sheet_id: task[TaskInfo.task_sheet_id]
                })

                self.mondb.update_one(Mongo.task_col, {
                    TaskInfo.task_ticket: task[TaskInfo.task_ticket]
                }, {
                    "$set": {
                        TaskInfo.task_sheet_name: task_sheet[TaskSheet.task_sheet_name]
                    }
                })

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

    def gen_pipeline_run_ticket(self, pipeline, xai_task_ticket, evaluation_task_ticket):

        pipeline_runs = self.mondb.find(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_id: pipeline[Pipeline.pipeline_id]
        })

        new_pipeline_run_name = pipeline[Pipeline.pipeline_name] + \
            '-#' + str(len(pipeline_runs))

        pipeline_run_ticket_info = {
            PipelineRun.create_at: time.time(),
            PipelineRun.pipeline_run_name: new_pipeline_run_name,
            PipelineRun.pipeline_id: pipeline[Pipeline.pipeline_id],
            PipelineRun.pipeline_name: pipeline[Pipeline.pipeline_name],
            PipelineRun.xai_task_sheet_id: pipeline[Pipeline.xai_task_sheet_id],
            PipelineRun.evaluation_task_sheet_id: pipeline[Pipeline.evaluation_task_sheet_id],
            PipelineRun.xai_task_ticket: xai_task_ticket,
            PipelineRun.evaluation_task_ticket: evaluation_task_ticket,
            PipelineRun.pipeline_run_ticket:  __get_random_string__(
                4) + '.' + __get_random_string_no_low__(
                4) + '.' + pipeline[Pipeline.pipeline_id]
        }

        self.mondb.insert_one(Mongo.pipeline_run_col, pipeline_run_ticket_info)

        return self.mondb.find_one(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_run_ticket: pipeline_run_ticket_info[
                PipelineRun.pipeline_run_ticket]
        })

    def gen_task_ticket(self, executor_id, task_name, task_sheet):
        if not self.is_activated() or not self.if_executor_registered(executor_id):
            return None
        else:
            task_ticket_info = {
                TaskInfo.task_ticket: __get_random_string__(
                    15) + '.' + executor_id,
                TaskInfo.task_type: task_sheet[TaskSheet.task_type],
                TaskInfo.executor_id: executor_id,
                TaskInfo.task_sheet_id: task_sheet[TaskSheet.task_sheet_id],
                TaskInfo.task_status: TaskStatus.initialized,
                TaskInfo.task_name: task_name,
                TaskInfo.task_sheet_name: task_sheet[TaskSheet.task_sheet_name],
                TaskInfo.publisher: self.publisher_name,
                TaskInfo.request_time: time.time(),
                TaskInfo.start_time: TaskInfo.empty,
                TaskInfo.end_time: TaskInfo.empty,
                TaskInfo.task_function_key: task_sheet[TaskSheet.task_function_key],
                TaskInfo.pipeline_id: TaskInfo.empty,
                TaskInfo.pipeline_run_ticket: TaskInfo.empty,
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

            return self.mondb.find_one(Mongo.task_col, {
                TaskInfo.task_ticket: task_ticket_info[TaskInfo.task_ticket]
            })

    def ask_executor_task_actual_status(self, task_ticket, executor_endpoint_url):

        response = requests.get(
            executor_endpoint_url +
            '/task_status',
            params={
                TaskInfo.task_ticket: task_ticket,
            }
        )

        rs = json.loads(response.content.decode('utf-8'))

        return rs[TaskInfo.task_status]

    def get_all_task(self):
        return self.mondb.find(Mongo.task_col, {})

    def get_task_info_by_task_sheet_id(self, task_sheet_id):
        tasks = self.mondb.find(Mongo.task_col, {
            TaskInfo.task_sheet_id: task_sheet_id
        })

        for task in tasks:
            if task[TaskInfo.task_status] == TaskStatus.running:
                current_acutal_status = self.ask_executor_task_actual_status(
                    task[TaskInfo.task_ticket],
                    task[TaskInfo.executor_endpoint_url]
                )

                if current_acutal_status == TaskStatus.not_exist_in_executor_process_holder:
                    # if the executor is shutdown
                    task[TaskInfo.task_status] = TaskStatus.stopped

                    self.mondb.update_one(Mongo.task_col, {
                        TaskInfo.task_ticket: task[TaskInfo.task_ticket]
                    }, {
                        "$set": {
                            TaskInfo.task_status: task[TaskInfo.task_status]
                        }
                    })

        return tasks

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
                                   executor_info: dict):
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
                # ExecutorRegInfo.executor_owner: executor_owner,
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
                    # ExecutorRegInfo.executor_owner: executor_owner,
                    ExecutorRegInfo.executor_register_time: reg_time,
                    ExecutorRegInfo.executor_type: executor_type,
                    ExecutorRegInfo.executor_info: executor_info,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                    ExecutorRegInfo.sys_info: json.loads(
                        resp.content.decode('utf-8'))
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

    def get_provenance(self):
        return {
            'executors': self.mondb.find(Mongo.executor_registration_col, {}),
            'task_sheets': self.mondb.find(Mongo.task_sheet_col, {}),
            'tasks': self.mondb.find(Mongo.task_col, {}),
            'pipelines': self.mondb.find(Mongo.pipeline_col, {}),
            'pipeline_runs': self.mondb.find(Mongo.pipeline_run_col, {}),
        }


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

    def create_pipeline(self, pipeline_name: str, xai_task_sheet_id: str, evaluation_task_sheet_id: str):
        pipeline_id = __get_random_string_no_low__(18)
        pipeline_info = {
            Pipeline.pipeline_id: pipeline_id,
            Pipeline.create_at: time.time(),
            Pipeline.pipeline_name: pipeline_name,
            Pipeline.xai_task_sheet_id: xai_task_sheet_id,
            Pipeline.evaluation_task_sheet_id: evaluation_task_sheet_id,
            # Pipeline.pipeline_owner: pipeline_owner
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
            # TaskSheet.task_sheet_owner: 'Jim',
        }

        task_tb = self.task_publisher.mondb.col(Mongo.task_sheet_col)

        task_sheet[TaskSheet.task_sheet_id] = __get_random_string_no_low__(15)
        task_tb.insert_one(task_sheet)
        return task_sheet[TaskSheet.task_sheet_id]

    def update_task_status(self, task_ticket, task_status, running_info):
        self.task_publisher.mondb.update_one(Mongo.task_col, {
            TaskInfo.task_ticket: task_ticket
        }, {
            "$set": {
                TaskInfo.task_status: task_status,
                TaskInfo.end_time: time.time() if task_status == TaskStatus.finished else '',
                TaskInfo.running_info: running_info
            },
        })

        task = self.task_publisher.mondb.find_one(Mongo.task_col, {
            TaskInfo.task_ticket: task_ticket
        })

        if task[TaskInfo.task_type] == TaskType.xai and\
            task[TaskInfo.pipeline_id] != TaskInfo.empty and\
                task[TaskInfo.pipeline_run_ticket] != TaskInfo.empty and\
        task[TaskInfo.task_status] == TaskStatus.finished:

            pipeline_run = self.task_publisher.mondb.find_one(Mongo.pipeline_run_col, {
                PipelineRun.pipeline_run_ticket: task[TaskInfo.pipeline_run_ticket]
            })

            evaluation_task = self.task_publisher.mondb.find_one(Mongo.task_col, {
                TaskInfo.task_ticket: pipeline_run[PipelineRun.evaluation_task_ticket]
            })

            self.tell_executor_to_run_task(evaluation_task)

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

    def remove_task_sheet_to_pipeline(self, pipeline_id: str, task_sheet_id: str):
        pass

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

            self.task_publisher.az.delete_blobs(
                f'task_execution/result/{task_ticket}')

    def __run_pipeline_with_pipeline__(self, pipeline):
        xai_task_sheet_id = pipeline[Pipeline.xai_task_sheet_id]
        evaluation_task_sheet_id = pipeline[Pipeline.evaluation_task_sheet_id]

        xai_task_sheet = self.task_publisher.mondb.find_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: xai_task_sheet_id
        })

        evaluation_task_sheet = self.task_publisher.mondb.find_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: evaluation_task_sheet_id
        })

        xai_task_under_this_pipeline = self.task_publisher.mondb.find(Mongo.task_col, {
            TaskInfo.task_sheet_id: xai_task_sheet_id,
            TaskInfo.pipeline_id: pipeline[Pipeline.pipeline_id]
        })

        # gen xai task
        xai_task = self.task_publisher.gen_task_ticket(
            xai_task_sheet[TaskSheet.xai_service_executor_id],
            pipeline[Pipeline.pipeline_name] + '_xai' +
            '-#' + str(len(xai_task_under_this_pipeline)),
            xai_task_sheet)

        # fill explanation_task_ticket if missing
        evaluation_task_sheet[TaskInfo.task_parameters]['explanation_task_ticket'] = xai_task[TaskInfo.task_ticket]

        evaluation_task_under_this_pipeline = self.task_publisher.mondb.find(Mongo.task_col, {
            TaskInfo.task_sheet_id: evaluation_task_sheet_id,
            TaskInfo.pipeline_id: pipeline[Pipeline.pipeline_id]
        })
        # gen eval task
        evaluation_task = self.task_publisher.gen_task_ticket(
            evaluation_task_sheet[TaskSheet.evaluation_service_executor_id],
            pipeline[Pipeline.pipeline_name] + '_evaluation' +
            '-#' + str(len(evaluation_task_under_this_pipeline)),
            evaluation_task_sheet)

        # gen pipeline run
        pipeline_run = self.task_publisher.gen_pipeline_run_ticket(
            pipeline,
            xai_task[TaskInfo.task_ticket],
            evaluation_task[TaskInfo.task_ticket])

        # update xai task & eval task
        self.task_publisher.mondb.update_many(Mongo.task_col, {
            TaskInfo.task_ticket: {
                "$in": [xai_task[TaskInfo.task_ticket], evaluation_task[TaskInfo.task_ticket]]
            }
        }, {
            "$set": {
                TaskInfo.pipeline_id: pipeline[Pipeline.pipeline_id],
                TaskInfo.pipeline_run_ticket: pipeline_run[PipelineRun.pipeline_run_ticket]
            }
        })

        # run xai task first
        self.tell_executor_to_run_task(xai_task)

        return pipeline

    def run_pipeline(self, pipeline_id):
        pipeline = self.task_publisher.mondb.find_one(Mongo.pipeline_col, {
            Pipeline.pipeline_id: pipeline_id
        })
        return self.__run_pipeline_with_pipeline__(pipeline)

    def get_pipeline_run(self, pipeline_id):
        pipeline_runs = self.task_publisher.mondb.find(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_id: pipeline_id
        })

        for pipeline_run in pipeline_runs:
            tasks = self.task_publisher.mondb.find(Mongo.task_col, {
                TaskInfo.task_ticket: {
                    "$in": [
                        pipeline_run[PipelineRun.xai_task_ticket],
                        pipeline_run[PipelineRun.evaluation_task_ticket],
                    ]
                }
            })

            for task in tasks:
                if task[TaskInfo.task_type] == TaskType.xai:
                    pipeline_run[PipelineRun.xai_task] = task

                if task[TaskInfo.task_type] == TaskType.evaluation:
                    pipeline_run[PipelineRun.evaluation_task] = task

                if task[TaskInfo.task_status] == TaskStatus.running:
                    current_acutal_status = self.task_publisher.ask_executor_task_actual_status(
                        task[TaskInfo.task_ticket],
                        task[TaskInfo.executor_endpoint_url]
                    )

                    if current_acutal_status == TaskStatus.not_exist_in_executor_process_holder:
                        # if the executor is shutdown
                        current_acutal_status = TaskStatus.stopped

                    if current_acutal_status != task[TaskInfo.task_status]:
                        self.task_publisher.mondb.update_one(Mongo.task_col, {
                            TaskInfo.task_ticket: task[TaskInfo.task_ticket]
                        }, {
                            "$set": {
                                TaskInfo.task_status: current_acutal_status
                            }
                        })

        return pipeline_runs

    def run_task_sheet_directly(self, task_sheet_id):
        task_sheet = self.get_task_sheet([task_sheet_id])[0]

        tasks_under_this_task_sheet = self.task_publisher.mondb.find(Mongo.task_col, {
            TaskInfo.task_sheet_id: task_sheet_id
        })

        task_name = task_sheet[TaskSheet.task_sheet_name] + f"-#{len(tasks_under_this_task_sheet)}"

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
        pass

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

    def stop_pipeline_run(self, pipeline_run_ticket):
        pipeline_run = self.task_publisher.mondb.find_one(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_run_ticket: pipeline_run_ticket
        })

        tasks = self.task_publisher.mondb.find(Mongo.task_col, {
            TaskInfo.task_ticket: {
                "$in": [
                    pipeline_run[PipelineRun.xai_task_ticket],
                    pipeline_run[PipelineRun.evaluation_task_ticket],
                ]
            }
        })

        for task in tasks:
            if task[TaskInfo.task_status] == TaskStatus.running:
                self.stop_a_task(task[TaskInfo.task_ticket])

    def get_task_presentation(self, task_ticket):
        blobs = self.task_publisher.az.get_blobs(
            'task_execution', f'result/{task_ticket}')

        pre = {
            'global': [],
            'local': {},
        }

        for blob in blobs:
            blob_name = blob['name']
            ext = blob_name.split('.')[-1]
            file_name = blob_name.replace('global/', '').replace('local/', '')
            p = {
                'address': blob['address'],
                'content': 'todo',
                'file_name': file_name,
                'file_type': 'img' if ext.lower() in ['png', 'jpeg'] else 'npy',
            }
            if blob_name.startswith('global'):
                pre['global'].append(p)
            if blob_name.startswith('local'):
                sample_name = blob_name.replace('local/', '').split('/')[0]
                if pre['local'].get(sample_name) == None:
                    pre['local'][sample_name] = []
                pre['local'][sample_name].append(p)

        return pre

    def delete_pipeline(self, pipeline_id):

        pipeline_runs = self.task_publisher.mondb.find(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_id: pipeline_id
        })

        for pipeline_run in pipeline_runs:
            self.delete_pipeline_run(
                pipeline_run[PipelineRun.pipeline_run_ticket])

        self.task_publisher.mondb.delete_one(Mongo.pipeline_col, {
            Pipeline.pipeline_id: pipeline_id
        })

    def delete_pipeline_run(self, pipeline_run_ticket):
        pipeline_run = self.task_publisher.mondb.find_one(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_run_ticket: pipeline_run_ticket
        })

        self.delete_task(pipeline_run[PipelineRun.xai_task_ticket])
        self.delete_task(pipeline_run[PipelineRun.evaluation_task_ticket])

        self.task_publisher.mondb.delete_one(Mongo.pipeline_run_col, {
            PipelineRun.pipeline_run_ticket: pipeline_run_ticket
        })

    def delete_task_sheet(self, task_sheet_id):

        tasks = self.task_publisher.mondb.find(Mongo.task_col, {
            TaskSheet.task_sheet_id: task_sheet_id
        })

        for task in tasks:
            self.delete_task(task[TaskInfo.task_ticket])

        self.task_publisher.mondb.delete_one(Mongo.task_sheet_col, {
            TaskSheet.task_sheet_id: task_sheet_id
        })

    def check_task_sheet_status(self, task_sheet_id):
        pass

    def check_task_status(self, task_ticket: str):
        pass

    def stop_task(self, task_ticket: str):
        pass
