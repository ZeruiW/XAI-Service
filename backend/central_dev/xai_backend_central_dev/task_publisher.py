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
from xai_backend_central_dev.constant import TaskSheetRunPayload


class TaskPublisher(TaskComponent):

    def __init__(self, publisher_name: str, component_path: str, import_name: str) -> None:

        super().__init__(publisher_name, component_path)
        self.publisher_name = publisher_name
        self.import_name = import_name

        c_db_path = os.path.join(self.db_path, 'central_db.json')
        self.db = TinyDB(c_db_path)
        self.ticket_info_map_tb = self.db.table('ticket_info_map')
        self.executor_registration_tb = self.db.table('executor_registration')

        self.pipeline = TaskPipeline(self)
        # print(self.ticket_info_map_tb.all())
        # print(self.executor_registration_tb.all())

    def __feed_info__(self, task_info: dict):
        task_info[TaskInfo.publisher] = self.publisher_name
        if task_info.get(TaskInfo.time_tail) == None:
            task_info[TaskInfo.time_tail] = str(time.time()).split('.')[1]
        return task_info

    def is_activated(self):
        return self.publisher_endpoint_url != None

    def activate_publisher(self, publisher_endpoint_url: str):
        self.publisher_endpoint_url = publisher_endpoint_url
        self.register_executor_endpoint(
            f"{self.publisher_endpoint_url}/task_publisher/central_executor",
            {
                'executor_name': 'central_task_executor',
            }
        )
        return self.get_executor_registration_info()

    def get_executor_registration_info(self):
        return self.executor_registration_tb.all()

    def gen_task_name(self, task_info: dict):
        task_info = self.__feed_info__(task_info)
        return '#'.join(list(task_info.values()))

    def gen_task_ticket(self, executor_id: str, task_info: dict):
        if not self.is_activated():
            return "central not activated"
        if self.if_executor_registered(executor_id):
            task_info = self.__feed_info__(task_info)
            task_ticket = __get_random_string__(
                15) + '.' + task_info[TaskInfo.time_tail] + '.' + executor_id

            # remove duplicated ticket information
            task_info.pop(TaskInfo.task_ticket, None)

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
            executor_id = executor_ticket_info[ExecutorTicketInfo.executor_id]
            ticket_infos = executor_ticket_info[ExecutorTicketInfo.ticket_infos]
            all_ticket_info_tmp[executor_id] = ticket_infos

        all_ticket_info = all_ticket_info_tmp

        # print(self.ticket_info_map_tb.all())

        if target_ticket == None:
            if with_status:
                for executor_id, ticket_infos in all_ticket_info.items():
                    # TODO: what if unknow executor_id
                    executor_reg_info = self.executor_registration_tb.search(
                        Query().executor_id == executor_id)[0]

                    executor_endpoint_url = executor_reg_info[ExecutorRegInfo.executor_endpoint_url]
                    response = requests.get(
                        executor_endpoint_url + '/task')
                    executor_tasks_status = json.loads(
                        response.content.decode('utf-8'))
                    for executor_task_status in executor_tasks_status:
                        current_task_ticket = executor_task_status[TaskInfo.task_ticket]
                        if all_ticket_info[executor_id].get(current_task_ticket) != None:
                            executor_task_status.pop(
                                TaskInfo.task_ticket, None)
                            all_ticket_info[executor_id][current_task_ticket]['task_status'] = executor_task_status

            formated_all_ticket_info = {}
            for executor_id, ticket_infos in all_ticket_info.items():
                executor_reg_info = self.executor_registration_tb.search(
                    Query().executor_id == executor_id)[0]

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
                    Query().executor_id == find_target_task_ticket_executor_id)[0]
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

    def register_executor_endpoint(self, executor_endpoint_url: str,
                                   executor_info: dict):
        existed_executor_id = None
        all_executor_registration_info = self.executor_registration_tb.all()
        # print(all_executor_registration_info)
        for e_rg_info in all_executor_registration_info:
            if e_rg_info[ExecutorRegInfo.executor_info] == executor_info:
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
                    ExecutorRegInfo.executor_info: executor_info,
                    ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
                })
            return _id
        else:
            return None

    def if_executor_registered(self, executor_id: str):
        return len(self.executor_registration_tb.search(Query().executor_id == executor_id)) > 0


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

        # A pipeline holds an executor
        self.ebp = ExecutorBluePrint(
            'central_pipeline_task_executor', self.import_name,
            component_path=self.component_path,
            url_prefix='/task_publisher/central_executor')

        self.db_path = os.path.join(self.storage_path, 'db')

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        pipeline_db_path = os.path.join(
            self.db_path, 'central_pipeline_db.json')
        self.db = TinyDB(pipeline_db_path)
        self.pipeline_tb = self.db.table('pipeline')
        self.xai_task_sheet_tb = self.db.table('xai_task_sheet')
        self.evaluation_task_sheet_tb = self.db.table('evaluation_task_sheet')

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

    def create_task_sheet(self, task_type, payload: dict):

        task_sheet = {
            TaskSheet.task_type: task_type,
            TaskSheet.model_service_executor_id: payload.get(TaskSheet.model_service_executor_id),
            TaskSheet.db_service_executor_id: payload.get(TaskSheet.db_service_executor_id),
            TaskSheet.xai_service_executor_id: payload.get(TaskSheet.xai_service_executor_id),
            TaskSheet.evaluation_service_executor_id: payload.get(TaskSheet.evaluation_service_executor_id),
            TaskSheet.task_parameters: payload.get(TaskSheet.task_parameters),
        }

        if task_type == TaskType.xai:
            task_sheet_query = self.xai_task_sheet_tb.search(
                Query().fragment(task_sheet))

            if len(task_sheet_query) > 0:
                # duplicated
                return task_sheet_query[0][TaskSheet.task_sheet_id]
            else:
                task_sheet[TaskSheet.task_sheet_id] = __get_random_string_no_low__(
                    15)
                self.xai_task_sheet_tb.insert(task_sheet)
                return task_sheet[TaskSheet.task_sheet_id]
        elif task_type == TaskType.evaluation:
            task_sheet_query = self.evaluation_task_sheet_tb.search(
                Query().fragment(task_sheet))

            if len(task_sheet_query) > 0:
                # duplicated
                return task_sheet_query[0][TaskSheet.task_sheet_id]
            else:
                task_sheet[TaskSheet.task_sheet_id] = __get_random_string_no_low__(
                    15)
                self.evaluation_task_sheet_tb.insert(task_sheet)
                return task_sheet[TaskSheet.task_sheet_id]

    def get_pipeline(self, pipeline_id: str):
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

    def add_task_sheet_to_pipeline(self, pipeline_id: str, task_sheet_id: str):
        pipeline = self.get_pipeline(pipeline_id)[0]
        task_sheet = self.get_task_sheet([task_sheet_id])[0]

        if task_sheet[TaskSheet.task_type] == TaskType.xai:
            if pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty:
                return -1   # xai task already exist
            else:
                pipeline[Pipeline.xai_task_sheet_id] = task_sheet_id
                pipeline[Pipeline.xai_task_sheet_status] = TaskStatus.initialized
        elif task_sheet[TaskSheet.task_type] == TaskType.evaluation:
            if pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty:
                return -2   # evaluation task already exist
            else:
                pipeline[Pipeline.evaluation_task_sheet_id] = task_sheet_id
                pipeline[Pipeline.evaluation_task_sheet_status] = TaskStatus.initialized
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

    def run_pipeline(self, pipeline_id):
        pipeline = self.get_pipeline(pipeline_id)[0]

        # TODO: can not run the pipeline while it is running

        xai_ready = self.__xai_task_ready_for_run__(pipeline=pipeline)
        eval_ready = self.__eval_task_ready_for_run__(pipeline=pipeline)

        if xai_ready or eval_ready:
            pass
        elif xai_ready:
            ticket = self.run_task_with_sheet(
                pipeline[Pipeline.xai_task_sheet_id])
            pipeline[Pipeline.xai_task_sheet_status] = TaskStatus.running
            pipeline[Pipeline.xai_task_ticket] = ticket
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline_id)
        elif eval_ready:
            ticket = self.run_task_with_sheet(
                pipeline[Pipeline.evaluation_task_sheet_id])
            pipeline[Pipeline.evaluation_task_sheet_status] = TaskStatus.running
            pipeline[Pipeline.evaluation_task_ticket] = ticket
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline_id)

        return pipeline

    def duplicate_pipeline(self, pipeline_id):
        src_pipeline = self.get_pipeline(pipeline_id)[0]

        pipeline_id = __get_random_string_no_low__(18)
        pipeline_info = {
            Pipeline.pipeline_id: pipeline_id,
            Pipeline.created_time: time.time(),
            Pipeline.pipeline_name: src_pipeline[Pipeline.pipeline_name] + 'Copied',
            Pipeline.xai_task_sheet_id: src_pipeline[Pipeline.xai_task_sheet_id],
            Pipeline.xai_task_sheet_status: TaskStatus.initialized if src_pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty else TaskStatus.undefined,
            Pipeline.xai_task_ticket: TaskSheet.empty,
            Pipeline.evaluation_task_sheet_id: src_pipeline[Pipeline.evaluation_task_sheet_id],
            Pipeline.evaluation_task_sheet_status: TaskStatus.initialized if src_pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty else TaskStatus.undefined,
            Pipeline.evaluation_task_ticket: TaskSheet.empty,
        }

        self.pipeline_tb.insert(pipeline_info)
        return pipeline_info

    def check_pipeline_status(self, pipeline):
        if pipeline[Pipeline.xai_task_sheet_id] != TaskSheet.empty and pipeline[Pipeline.xai_task_sheet_status] == TaskStatus.running:
            task_ticket = pipeline[Pipeline.xai_task_ticket]
            ticket_info = self.task_publisher.get_ticket_info(
                task_ticket, True)
            task_status = ticket_info['task_status']
            if task_status['status'].lower() == TaskStatus.stopped:
                pipeline[Pipeline.xai_task_sheet_status] = TaskStatus.stopped
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline[Pipeline.pipeline_id])
            return pipeline
        if pipeline[Pipeline.evaluation_task_sheet_id] != TaskSheet.empty and pipeline[Pipeline.evaluation_task_sheet_status] == TaskStatus.running:
            task_ticket = pipeline[Pipeline.evaluation_task_ticket]
            ticket_info = self.task_publisher.get_ticket_info(
                task_ticket, True)
            task_status = ticket_info['task_status']
            if task_status['status'].lower() == TaskStatus.stopped:
                pipeline[Pipeline.evaluation_task_sheet_status] = TaskStatus.stopped
            self.pipeline_tb.update(
                pipeline, Query().pipeline_id == pipeline[Pipeline.pipeline_id])
            return pipeline

    def stop_pipeline(self, pipeline_id):
        pass

    def __get_url_from_executor_id__(self, executor_registration_infos, executor_id):
        for executor_info in executor_registration_infos:
            if executor_info[ExecutorRegInfo.executor_id] == executor_id:
                return executor_info[ExecutorRegInfo.executor_endpoint_url]

    def run_task_with_sheet(self, task_sheet_id):
        task_sheet = self.get_task_sheet([task_sheet_id])[0]

        payload = {}
        for k, v in task_sheet[TaskSheet.task_parameters].items():
            payload[k] = v

        executor_registration_infos = self.task_publisher.get_executor_registration_info()

        payload[TaskSheetRunPayload.db_service_url] = self.__get_url_from_executor_id__(
            executor_registration_infos, task_sheet[TaskSheet.db_service_executor_id])
        payload[TaskSheetRunPayload.model_service_url] = self.__get_url_from_executor_id__(
            executor_registration_infos, task_sheet[TaskSheet.model_service_executor_id])
        payload[TaskSheetRunPayload.xai_service_url] = self.__get_url_from_executor_id__(
            executor_registration_infos, task_sheet[TaskSheet.xai_service_executor_id])

        if task_sheet[TaskSheet.task_type] == TaskType.xai:
            url = payload[TaskSheetRunPayload.xai_service_url]
        elif task_sheet[TaskSheet.task_type] == TaskType.evaluation:
            payload[TaskSheetRunPayload.evaluation_service_url] = self.__get_url_from_executor_id__(
                executor_registration_infos, task_sheet[TaskSheet.evaluation_service_executor_id])
            url = payload[TaskSheetRunPayload.evaluation_service_url]
        else:
            url = ''

        headers = {}

        response = requests.request(
            "POST", url, headers=headers, data=payload)

        print(response.content)
        task_ticket = json.loads(
            response.content.decode('utf-8'))

        return task_ticket[TaskInfo.task_ticket]

    def check_task_sheet_status(self, task_sheet_id):
        pass

    def check_task_status(self, task_ticket: str):
        pass

    def stop_task(self, task_ticket: str):
        pass
