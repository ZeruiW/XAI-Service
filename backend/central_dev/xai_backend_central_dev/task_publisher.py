import time
import os
import json
import requests
from tinydb import TinyDB, Query

from xai_backend_central_dev.task_manager import TaskComponent, __get_random_string__, __get_random_string_no_low__

from xai_backend_central_dev.flask_manager import ExecutorBluePrint
from xai_backend_central_dev.constant import Pipeline
from xai_backend_central_dev.constant import TaskStatus
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import TaskType
from xai_backend_central_dev.constant import ExecutorTicketInfo
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import ExecutorRegInfo

from xai_backend_central_dev.pipeline_db_helper import PipelineDB
from xai_backend_central_dev.pipeline_task_func import run_pipeline_tasks


class TaskPublisher(TaskComponent):

    def __init__(self, publisher_name: str, component_path: str, import_name: str, context_path: str) -> None:

        super().__init__(publisher_name, component_path, context_path=context_path)
        self.publisher_name = publisher_name
        self.import_name = import_name

        c_db_path = os.path.join(self.db_path, 'central_db.json')
        self.db = TinyDB(c_db_path)
        self.ticket_info_map_tb = self.db.table('ticket_info_map')
        self.executor_registration_tb = self.db.table('executor_registration')
        self.central_info_tb = self.db.table('central_info')

        self.pipeline = TaskPipeline(self)
        # print(self.ticket_info_map_tb.all())
        # print(self.executor_registration_tb.all())

        # recover activation
        central_info = self.central_info_tb.all()
        if len(central_info) == 1:
            self.publisher_endpoint_url = central_info[0]['publisher_endpoint_url']

    def __feed_info__(self, task_info: dict):
        task_info[TaskInfo.publisher] = self.publisher_name
        if task_info.get(TaskInfo.time_tail) == None:
            task_info[TaskInfo.time_tail] = str(time.time()).split('.')[1]
        return task_info

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
            return self.executor_registration_tb.all()
        else:
            query = self.executor_registration_tb.search(
                Query().executor_id == executor_id)
            if len(query) == 0:
                return None
            else:
                return query[0]

    def remove_task_ticket(self, executor_id, task_ticket):
        executor_ticket_info = self.ticket_info_map_tb.search(
            Query().executor_id == executor_id)

        if len(executor_ticket_info) != 0:
            executor_ticket_info[0][ExecutorTicketInfo.ticket_infos].pop(
                task_ticket, None)
            self.ticket_info_map_tb.update(
                executor_ticket_info[0], Query().executor_id == executor_id)

    def gen_task_ticket(self, executor_id, task_name, task_sheet_id):
        if not self.is_activated():
            return "central not activated"
        if self.if_executor_registered(executor_id):
            task_ticket_gen_info = {
                'executor_id': executor_id,
                'task_sheet_id': task_sheet_id,
                'task_name': task_name,
            }
            task_ticket_gen_info = self.__feed_info__(task_ticket_gen_info)
            task_ticket = __get_random_string__(
                15) + '.' + task_ticket_gen_info[TaskInfo.time_tail] + '.' + executor_id

            # remove duplicated ticket information
            task_ticket_gen_info.pop(TaskInfo.task_ticket, None)

            executor_ticket_info = self.ticket_info_map_tb.search(
                Query().executor_id == executor_id)

            if len(executor_ticket_info) == 0:
                self.ticket_info_map_tb.insert({
                    ExecutorTicketInfo.executor_id: executor_id,
                    ExecutorTicketInfo.ticket_infos: {}
                })

            executor_ticket_info = self.ticket_info_map_tb.search(
                Query().executor_id == executor_id)[0]

            executor_ticket_info[ExecutorTicketInfo.ticket_infos][task_ticket] = dict(
                **task_ticket_gen_info,
                request_time=time.time()
            )

            self.ticket_info_map_tb.update(
                executor_ticket_info, Query().executor_id == executor_id)

            return task_ticket
        else:
            return "executor not register"

    def get_ticket_info(self, target_ticket: str, with_status: bool = False):
        all_ticket_info = self.ticket_info_map_tb.all()

        all_ticket_info_tmp = {}
        for executor_ticket_info in all_ticket_info:
            executor_id = executor_ticket_info[ExecutorTicketInfo.executor_id]
            ticket_infos = executor_ticket_info[ExecutorTicketInfo.ticket_infos]
            all_ticket_info_tmp[executor_id] = ticket_infos

        all_ticket_info = all_ticket_info_tmp

        # print(self.ticket_info_map_tb.all())

        if target_ticket == None:
            if with_status:
                for executor_id, ticket_infos in all_ticket_info.items():
                    # ANCHOR: what if unknow executor_id
                    executor_reg_info = self.executor_registration_tb.search(
                        Query().executor_id == executor_id)

                    if len(executor_reg_info) == 0:
                        continue
                    else:
                        executor_reg_info = executor_reg_info[0]

                    executor_endpoint_url = executor_reg_info[ExecutorRegInfo.executor_endpoint_url]
                    try:
                        response = requests.get(
                            executor_endpoint_url + '/task')
                        executor_tasks_status = json.loads(
                            response.content.decode('utf-8'))
                    except:
                        if executor_tasks_status == None:
                            executor_tasks_status = []

                    for executor_task_status in executor_tasks_status:
                        current_task_ticket = executor_task_status.get(
                            TaskInfo.task_ticket)
                        if current_task_ticket != None and all_ticket_info[executor_id].get(current_task_ticket) != None:
                            executor_task_status.pop(
                                TaskInfo.task_ticket, None)
                            all_ticket_info[executor_id][current_task_ticket]['task_status'] = executor_task_status

            formated_all_ticket_info = {}
            for executor_id, ticket_infos in all_ticket_info.items():
                executor_reg_info = self.executor_registration_tb.search(
                    Query().executor_id == executor_id)

                if len(executor_reg_info) == 0:
                    continue
                else:
                    executor_reg_info = executor_reg_info[0]

                formated_all_ticket_info[executor_id] = dict(
                    executor=executor_reg_info,
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

            if find_target_task_ticket_executor_id != None and find_target_task_ticket_info != None:
                executor_reg_info = self.executor_registration_tb.search(
                    Query().executor_id == find_target_task_ticket_executor_id)

                if len(executor_reg_info) == 0:
                    return None
                else:
                    executor_reg_info = executor_reg_info[0]

                if with_status:
                    executor_endpoint_url = executor_reg_info[ExecutorRegInfo.executor_endpoint_url]
                    response = requests.get(
                        executor_endpoint_url + '/task',
                        params={
                            TaskInfo.task_ticket: find_target_task_ticket,
                        })
                    executor_task_status = json.loads(
                        response.content.decode('utf-8'))

                    # remove duplicated ticket information
                    executor_task_status.pop(TaskInfo.task_ticket, None)
                    find_target_task_ticket_info['task_status'] = executor_task_status

                find_target_task_ticket_info['executor_registeration_info'] = executor_reg_info
                find_target_task_ticket_info[TaskInfo.task_ticket] = find_target_task_ticket
                return find_target_task_ticket_info
            else:
                return

    def register_executor_endpoint(self,
                                   executor_type: str,
                                   executor_endpoint_url: str,
                                   executor_info: dict):
        existed_executor_id = None
        all_executor_registration_info = self.executor_registration_tb.all()
        # print(all_executor_registration_info)
        for e_rg_info in all_executor_registration_info:
            if e_rg_info[ExecutorRegInfo.executor_info] == executor_info and e_rg_info[ExecutorRegInfo.executor_type] == executor_type:
                existed_executor_id = e_rg_info[ExecutorRegInfo.executor_id]
                break

        _id = None
        if existed_executor_id != None:
            _id = existed_executor_id
        else:
            _id = __get_random_string_no_low__(10)

        # send reg info to executor service
        resp = requests.post(
            executor_endpoint_url + '/executor',
            data={
                'act': 'reg',
                ExecutorRegInfo.executor_id: _id,
                ExecutorRegInfo.executor_type: executor_type,
                ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                ExecutorRegInfo.executor_info: json.dumps(executor_info),
                ExecutorRegInfo.publisher_endpoint_url: self.publisher_endpoint_url
            }
        )

        if resp.status_code == 200:
            if existed_executor_id != None and _id == existed_executor_id:
                self.executor_registration_tb.update({
                    ExecutorRegInfo.executor_id: _id,
                    ExecutorRegInfo.executor_info: executor_info,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                }, Query().executor_id == _id)
            else:
                self.executor_registration_tb.insert({
                    ExecutorRegInfo.executor_id: _id,
                    ExecutorRegInfo.executor_type: executor_type,
                    ExecutorRegInfo.executor_info: executor_info,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                })
            return _id
        else:
            return None

    def reset_all_data(self):
        self.ticket_info_map_tb.truncate()
        self.pipeline.pipeline_tb.truncate()
        self.pipeline.xai_task_sheet_tb.truncate()
        self.pipeline.evaluation_task_sheet_tb.truncate()
        self.pipeline.prediction_task_sheet_tb.truncate()

        exe_reg_infos = self.get_executor_registration_info()
        for exe_reg_info in exe_reg_infos:
            try:
                requests.get(
                    exe_reg_info[ExecutorRegInfo.executor_endpoint_url] + '/reset'
                )
            except Exception:
                pass

        self.executor_registration_tb.truncate()

    def if_executor_registered(self, executor_id: str):
        return len(self.executor_registration_tb.search(Query().executor_id == executor_id)) > 0

    def update_executor_endpoint(self, executor_id,
                                 executor_endpoint_url: str,
                                 executor_info: dict):
        executor_reg_info = self.get_executor_registration_info(executor_id)
        if executor_info != None:
            resp = requests.post(
                executor_endpoint_url + '/executor',
                data={
                    'act': 'update',
                    ExecutorRegInfo.executor_id: executor_id,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                    ExecutorRegInfo.executor_info: json.dumps(executor_info),
                    ExecutorRegInfo.publisher_endpoint_url: self.publisher_endpoint_url
                }
            )

            if resp.status_code == 200:
                executor_reg_info[ExecutorRegInfo.executor_info] = executor_info
                executor_reg_info[ExecutorRegInfo.executor_endpoint_url] = executor_endpoint_url
                self.executor_registration_tb.update(
                    executor_reg_info, Query().executor_id == executor_id)
                return executor_id
            else:
                return None

    def delete_executor_endpoint(self, executor_id):
        self.executor_registration_tb.remove(
            Query().executor_id == executor_id)


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
        self.xai_task_sheet_tb = self.db.xai_task_sheet_tb
        self.evaluation_task_sheet_tb = self.db.evaluation_task_sheet_tb

        # TODO: predictionn task
        self.prediction_task_sheet_tb = self.db.prediction_task_sheet_tb

    def create_pipeline(self, pipeline_name: str):
        pipeline_id = __get_random_string_no_low__(18)
        pipeline_info = {
            Pipeline.pipeline_id: pipeline_id,
            Pipeline.created_time: time.time(),
            Pipeline.pipeline_name: pipeline_name,
            Pipeline.xai_task_sheet_id: TaskSheet.empty,
            Pipeline.xai_task_sheet_status: TaskStatus.undefined,
            Pipeline.xai_task_ticket: TaskSheet.empty,
            Pipeline.evaluation_task_sheet_id: TaskSheet.empty,
            Pipeline.evaluation_task_sheet_status: TaskStatus.undefined,
            Pipeline.evaluation_task_ticket: TaskSheet.empty,
        }

        self.pipeline_tb.insert(pipeline_info)
        return pipeline_info

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

        if task_type == TaskType.xai:
            task_tb = self.xai_task_sheet_tb
        elif task_type == TaskType.evaluation:
            task_tb = self.evaluation_task_sheet_tb
        else:
            task_tb = self.prediction_task_sheet_tb

        task_sheet_query = task_tb.search(
            Query().fragment(task_sheet))

        if len(task_sheet_query) > 0:
            # duplicated
            return task_sheet_query[0][TaskSheet.task_sheet_id]
        else:
            task_sheet[TaskSheet.task_sheet_id] = \
                __get_random_string_no_low__(15)

            task_tb.insert(task_sheet)
            return task_sheet[TaskSheet.task_sheet_id]

    def update_pipeline_task_status(self, task_ticket, task_status):
        pipelines = self.get_pipeline()
        find = False
        task_type = None
        for pipeline in pipelines:
            if task_ticket == pipeline[Pipeline.xai_task_ticket]:
                pipeline[Pipeline.xai_task_sheet_status] = task_status
                find = True
                task_type = TaskType.xai
            if task_ticket == pipeline[Pipeline.evaluation_task_ticket]:
                pipeline[Pipeline.evaluation_task_sheet_status] = task_status
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
                        and pipeline[Pipeline.xai_task_sheet_status] == TaskStatus.finished:
                    self.__run_pipeline_with_pipeline__(pipeline)

                break

    def get_pipeline(self, pipeline_id: str = None):
        if pipeline_id == None:
            all_pipeline = self.pipeline_tb.all()
            for pipeline in all_pipeline:
                self.check_pipeline_status(pipeline)
            return self.pipeline_tb.all()
        else:
            pipeline = self.pipeline_tb.search(
                Query().pipeline_id == pipeline_id)[0]
            self.check_pipeline_status(pipeline)
            return self.pipeline_tb.search(Query().pipeline_id == pipeline_id)

    def get_task_sheet(self, task_sheet_ids):
        if task_sheet_ids == None:
            return [
                *self.xai_task_sheet_tb.all(),
                *self.evaluation_task_sheet_tb.all(),
            ]

        def tf(v, *l):
            return v in [*l]
        return [
            *self.xai_task_sheet_tb.search(Query().task_sheet_id.test(tf, *task_sheet_ids)),
            *self.evaluation_task_sheet_tb.search(
                Query().task_sheet_id.test(tf, *task_sheet_ids)),
        ]

    def tell_executor_about_the_task(self, task_executor_id, task_name, task_sheet):
        # request a ticket from central here
        task_ticket = self.task_publisher.gen_task_ticket(
            executor_id=task_executor_id, task_name=task_name, task_sheet_id=task_sheet[TaskSheet.task_sheet_id])

        executor_reg_info = self.task_publisher.get_executor_registration_info(
            executor_id=task_executor_id)

        # add services url into the parameters
        if task_sheet[TaskSheet.db_service_executor_id] != TaskSheet.empty:
            db_executor_reg_info = self.task_publisher.get_executor_registration_info(
                executor_id=task_sheet[TaskSheet.db_service_executor_id])
            if type(db_executor_reg_info) is not list:
                task_sheet[TaskSheet.task_parameters][TaskInfo.db_service_url] = db_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

        if task_sheet[TaskSheet.model_service_executor_id] != TaskSheet.empty:
            model_executor_reg_info = self.task_publisher.get_executor_registration_info(
                executor_id=task_sheet[TaskSheet.model_service_executor_id])
            if type(model_executor_reg_info) is not list:
                task_sheet[TaskSheet.task_parameters][TaskInfo.model_service_url] = model_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

        if task_sheet[TaskSheet.xai_service_executor_id] != TaskSheet.empty:
            xai_executor_reg_info = self.task_publisher.get_executor_registration_info(
                executor_id=task_sheet[TaskSheet.xai_service_executor_id])
            if type(xai_executor_reg_info) is not list:
                task_sheet[TaskSheet.task_parameters][TaskInfo.xai_service_url] = xai_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

        if task_sheet[TaskSheet.evaluation_service_executor_id] != TaskSheet.empty:
            evaluation_executor_reg_info = self.task_publisher.get_executor_registration_info(
                executor_id=task_sheet[TaskSheet.evaluation_service_executor_id])
            if type(evaluation_executor_reg_info) is not list:
                task_sheet[TaskSheet.task_parameters][TaskInfo.evaluation_service_url] = evaluation_executor_reg_info[ExecutorRegInfo.executor_endpoint_url]

        if task_sheet[TaskSheet.task_type] == TaskType.evaluation:
            explanation_task_ticket = task_sheet[TaskSheet.task_parameters]['explanation_task_ticket']
            xai_task_ticket_info = self.task_publisher.get_ticket_info(
                explanation_task_ticket, with_status=True)
            task_sheet[TaskSheet.task_parameters]['explanation_task_parameters'] = \
                xai_task_ticket_info[TaskInfo.task_status][TaskSheet.task_parameters]

        # tell executor about the task
        resp = requests.post(
            executor_reg_info[ExecutorRegInfo.executor_endpoint_url] + '/task',
            data={
                'act': 'create',
                TaskInfo.task_ticket: task_ticket,
                TaskInfo.task_name: task_name,
                TaskSheet.task_function_key: task_sheet[TaskSheet.task_function_key],
                TaskSheet.task_parameters: json.dumps(task_sheet[TaskSheet.task_parameters]),
            }
        )

        if resp.status_code != 200:
            self.task_publisher.remove_task_ticket(
                task_executor_id, task_ticket)
            return None
        else:
            return task_ticket

    def add_task_to_pipeline(self, pipeline_id: str, task_name: str, task_sheet_id: str):
        pipeline = self.get_pipeline(pipeline_id)[0]

        task_sheet = self.get_task_sheet([task_sheet_id])[0]
        task_type = task_sheet[TaskSheet.task_type]

        if task_type == TaskType.xai:
            task_sheet_id_key = Pipeline.xai_task_sheet_id
            task_sheet_status_key = Pipeline.xai_task_sheet_status
            task_task_ticket_key = Pipeline.xai_task_ticket
            task_executor_id = task_sheet[TaskSheet.xai_service_executor_id]

        elif task_type == TaskType.evaluation:
            task_sheet_id_key = Pipeline.evaluation_task_sheet_id
            task_sheet_status_key = Pipeline.evaluation_task_sheet_status
            task_task_ticket_key = Pipeline.evaluation_task_ticket
            task_executor_id = task_sheet[TaskSheet.evaluation_service_executor_id]
        else:
            # the prediction task does not involve in XAI pipeline
            pass

        if pipeline[task_sheet_id_key] != TaskSheet.empty:
            return -1   # xai task already exist
        else:
            required_task_ticket = self.tell_executor_about_the_task(
                task_executor_id, task_name, task_sheet)
            if required_task_ticket != None:
                pipeline[task_sheet_id_key] = task_sheet_id
                pipeline[task_sheet_status_key] = TaskStatus.initialized
                pipeline[task_task_ticket_key] = required_task_ticket

        self.pipeline_tb.update(pipeline, Query().pipeline_id == pipeline_id)
        return 1

    def remove_task_sheet_to_pipeline(self, pipeline_id: str, task_sheet_id: str):
        pass

    def __xai_task_ready_for_run__(self, pipeline):
        return pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty and \
            pipeline[Pipeline.xai_task_sheet_status] == TaskStatus.initialized

    def __eval_task_ready_for_run__(self, pipeline):
        return pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty and \
            pipeline[Pipeline.evaluation_task_sheet_status] == TaskStatus.initialized

    def __get_url_from_executor_id__(self, executor_registration_infos, executor_id):
        for executor_info in executor_registration_infos:
            if executor_info[ExecutorRegInfo.executor_id] == executor_id:
                return executor_info[ExecutorRegInfo.executor_endpoint_url]

    def run_task_with_sheet(self, task_ticket, executor_endpoint_url):

        payload = {
            'act': 'run',
            'task_ticket': task_ticket
        }

        response = requests.request(
            "POST", f"{executor_endpoint_url}/task", headers={}, data=payload)

        task_ticket = json.loads(
            response.content.decode('utf-8'))

        return task_ticket[TaskInfo.task_ticket]

    def __run_pipeline_with_pipeline__(self, pipeline):
        pipeline_id = pipeline[Pipeline.pipeline_id]
        pipeline_status = self.get_pipeline_status(pipeline)

        if TaskStatus.initialized in pipeline_status:
            xai_ready = self.__xai_task_ready_for_run__(pipeline=pipeline)
            eval_ready = self.__eval_task_ready_for_run__(pipeline=pipeline)

            executor_registration_infos = self.task_publisher.get_executor_registration_info()

            if xai_ready:
                xai_task_sheet = self.get_task_sheet(
                    [pipeline[Pipeline.xai_task_sheet_id]])[0]
                executor_task_ticket = pipeline[Pipeline.xai_task_ticket]
                executor_id = xai_task_sheet[TaskSheet.xai_service_executor_id]
                executor_endpoint_url = self.__get_url_from_executor_id__(
                    executor_registration_infos, executor_id)
                task_status_key = Pipeline.xai_task_sheet_status
            elif eval_ready:
                eval_task_sheet = self.get_task_sheet(
                    [pipeline[Pipeline.evaluation_task_sheet_id]])[0]
                executor_task_ticket = pipeline[Pipeline.evaluation_task_ticket]
                executor_id = eval_task_sheet[TaskSheet.evaluation_service_executor_id]
                executor_endpoint_url = self.__get_url_from_executor_id__(
                    executor_registration_infos, executor_id)
                task_status_key = Pipeline.evaluation_task_sheet_status

            if xai_ready or eval_ready:
                self.run_task_with_sheet(
                    executor_task_ticket, executor_endpoint_url)
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

        required_task_ticket = self.tell_executor_about_the_task(
            task_executor_id, task_name, task_sheet)

        if required_task_ticket != None:
            executor_registration_infos = self.task_publisher.get_executor_registration_info()
            executor_endpoint_url = self.__get_url_from_executor_id__(
                executor_registration_infos, task_executor_id)
            return self.run_task_with_sheet(
                required_task_ticket, executor_endpoint_url)
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
            new_xai_task_ticket = self.tell_executor_about_the_task(
                src_executor_id, src_task_name + ' Copied', src_task_sheet)

        if has_evaluation_task_sheet:
            src_task_sheet = self.get_task_sheet(
                [src_pipeline[Pipeline.evaluation_task_sheet_id]])[0]
            src_task_info = self.task_publisher.get_ticket_info(
                src_pipeline[Pipeline.evaluation_task_ticket])
            src_task_name = src_task_info[TaskInfo.task_name]
            src_executor_id = src_task_info['executor_id']
            new_evaluation_task_ticket = self.tell_executor_about_the_task(
                src_executor_id, src_task_name + ' Copied', src_task_sheet)

        pipeline_info = {
            Pipeline.pipeline_id: pipeline_id,
            Pipeline.created_time: time.time(),
            Pipeline.pipeline_name: src_pipeline[Pipeline.pipeline_name] + ' Copied',
            Pipeline.xai_task_sheet_id: src_pipeline[Pipeline.xai_task_sheet_id],
            Pipeline.xai_task_sheet_status: TaskStatus.initialized if has_xai_task_sheet else TaskStatus.undefined,
            Pipeline.xai_task_ticket: new_xai_task_ticket if has_xai_task_sheet else TaskSheet.empty,
            Pipeline.evaluation_task_sheet_id: src_pipeline[Pipeline.evaluation_task_sheet_id],
            Pipeline.evaluation_task_sheet_status: TaskStatus.initialized if has_evaluation_task_sheet else TaskStatus.undefined,
            Pipeline.evaluation_task_ticket: new_evaluation_task_ticket if has_evaluation_task_sheet else TaskSheet.empty,
        }

        self.pipeline_tb.insert(pipeline_info)
        return pipeline_info

    def get_pipeline_status(self, pipeline):
        return (pipeline[Pipeline.xai_task_sheet_status], pipeline[Pipeline.evaluation_task_sheet_status])

    def check_pipeline_status(self, pipeline):
        if pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty:
            task_ticket = pipeline[Pipeline.xai_task_ticket]
            ticket_info = self.task_publisher.get_ticket_info(
                task_ticket, True)
            task_status = ticket_info[TaskInfo.task_status]
            if task_status[TaskInfo.task_status] != pipeline[Pipeline.xai_task_sheet_status]:
                pipeline[Pipeline.xai_task_sheet_status] = task_status[TaskInfo.task_status]
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline[Pipeline.pipeline_id])
            return pipeline
        if pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty:
            task_ticket = pipeline[Pipeline.evaluation_task_ticket]
            ticket_info = self.task_publisher.get_ticket_info(
                task_ticket, True)
            task_status = ticket_info[TaskInfo.task_status]
            if task_status[TaskInfo.task_status] != pipeline[Pipeline.evaluation_task_sheet_status]:
                pipeline[Pipeline.evaluation_task_sheet_status] = task_status[TaskInfo.task_status]
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline[Pipeline.pipeline_id])
            return pipeline

    def stop_a_task(self, task_ticket):
        ticket_info = self.task_publisher.get_ticket_info(task_ticket)
        executor_endpoint_url = ticket_info['executor_registeration_info'][ExecutorRegInfo.executor_endpoint_url]
        requests.post(
            executor_endpoint_url + '/task',
            data={
                'act': 'stop',
                TaskInfo.task_ticket: task_ticket
            }
        )

    def stop_pipeline(self, pipeline_id):
        pipeline = self.get_pipeline(pipeline_id)[0]
        executor_endpoint_url = None
        if pipeline[Pipeline.xai_task_sheet_status] == TaskStatus.running:
            task_sheet = self.get_task_sheet(
                [pipeline[Pipeline.xai_task_sheet_id]])[0]
            task_ticket = pipeline[Pipeline.xai_task_ticket]

            task_executor_id = task_sheet[TaskSheet.xai_service_executor_id]
            executor_registration_infos = self.task_publisher.get_executor_registration_info()

            executor_endpoint_url = self.__get_url_from_executor_id__(
                executor_registration_infos, task_executor_id)

        if pipeline[Pipeline.evaluation_task_sheet_status] == TaskStatus.running:
            task_sheet = self.get_task_sheet(
                [pipeline[Pipeline.evaluation_task_sheet_id]])[0]
            task_ticket = pipeline[Pipeline.evaluation_task_ticket]

            task_executor_id = task_sheet[TaskSheet.evaluation_service_executor_id]
            executor_registration_infos = self.task_publisher.get_executor_registration_info()

            executor_endpoint_url = self.__get_url_from_executor_id__(
                executor_registration_infos, task_executor_id)

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
        ticket_info = self.task_publisher.get_ticket_info(task_ticket)
        # print(ticket_info)
        executor_reg_info = ticket_info['executor_registeration_info']
        response = requests.get(
            executor_reg_info[ExecutorRegInfo.executor_endpoint_url] +
            '/task_result_present',
            params={
                TaskInfo.task_ticket: task_ticket,
            }
        )

        pre = json.loads(response.content.decode('utf-8'))

        for f in pre['local']:
            f['address'] = executor_reg_info[ExecutorRegInfo.executor_endpoint_url] + f['address']

        for f in pre['global']:
            f['address'] = executor_reg_info[ExecutorRegInfo.executor_endpoint_url] + f['address']

        return pre

    def check_task_sheet_status(self, task_sheet_id):
        pass

    def check_task_status(self, task_ticket: str):
        pass

    def stop_task(self, task_ticket: str):
        pass
