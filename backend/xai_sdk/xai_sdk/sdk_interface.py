from .xai_sdk import PublisherManager, TaskSheetManager, TaskManager, PipelineManager, ConfigBasedManager

class SDKInterface:
    def __init__(self, base_url):
        self.publisher_manager = PublisherManager(base_url)
        self.task_sheet_manager = TaskSheetManager(base_url)
        self.task_manager = TaskManager(base_url)
        self.pipeline_manager = PipelineManager(base_url)
        self.config_manager = ConfigBasedManager(base_url, self.publisher_manager, self.task_sheet_manager, self.task_manager, self.pipeline_manager)

    # Publisher Manager related functions
    def activate_publisher(self, publisher_endpoint_url):
        return self.publisher_manager.activate_publisher(publisher_endpoint_url)

    def get_registered_executors(self):
        return self.publisher_manager.get_registered_executors()

    def register_executor_endpoint(self, act, executor_endpoint_url, executor_type, executor_info):
        return self.publisher_manager.register_executor_endpoint(act, executor_endpoint_url, executor_type, executor_info)

    def get_registered_services(self):
        return self.publisher_manager.get_registered_services()

    # Task Sheet Manager related functions
    def create_task_sheet(self, payload, task_type="Task"):
        return self.task_sheet_manager.create_task_sheet(payload, task_type)

    def run_task_sheet(self, task_sheet_id, task_type="Task"):
        return self.task_sheet_manager.run_task_sheet(task_sheet_id, task_type)

    def delete_task_sheet(self, task_sheet_id):
        return self.task_sheet_manager.delete_task_sheet(task_sheet_id)

    def get_task_sheet(self):
        return self.task_sheet_manager.get_task_sheet()

    def get_task_sheet_by_task_sheet_id(self, task_sheet_ids=None):
        return self.task_sheet_manager.get_task_sheet_by_task_sheet_id(task_sheet_ids)

    def fetch_task_sheet_info(self):
        return self.task_sheet_manager.fetch_task_sheet_info()

    def get_latest_task_sheet_index(self, task_type):
        return self.task_sheet_manager.get_latest_task_sheet_index(task_type)

    # Task Manager related functions
    def get_task(self, task_ticket=None, task_sheet_id=None):
        return self.task_manager.get_task(task_ticket, task_sheet_id)

    def task_result(self, task_ticket):
        return self.task_manager.task_result(task_ticket)

    def update_task_status(self, task_ticket, task_status, running_info):
        return self.task_manager.update_task_status(task_ticket, task_status, running_info)

    def stop_task(self, task_ticket):
        return self.task_manager.stop_task(task_ticket)

    def delete_task(self, task_ticket):
        return self.task_manager.delete_task(task_ticket)

    # Pipeline Manager related functions
    def create_pipeline(self, pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id):
        return self.pipeline_manager.create_pipeline(pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id)

    def run_pipeline(self, pipeline_id):
        return self.pipeline_manager.run_pipeline(pipeline_id)

    def delete_pipeline(self, pipeline_id):
        return self.pipeline_manager.delete_pipeline(pipeline_id)

    def get_all_pipelines(self):
        return self.pipeline_manager.get_all_pipelines()

    def get_latest_pipeline_index(self, pipelines):
        return self.pipeline_manager.get_latest_pipeline_index(pipelines)


    # ConfigBasedManager related functions
    def register_service_from_config(self, config_source):
        return self.config_manager.register_service_from_config(config_source)

    def create_and_run_task_sheet_from_config(self, config_source):
        return self.config_manager.create_and_run_task_sheet_from_config(config_source)

    def create_and_run_pipeline_from_config(self, config_source):
        return self.config_manager.create_and_run_pipeline_from_config(config_source)
    
    def create_task_sheet_from_config(self, config_source):
        return self.config_manager.create_task_sheet_from_config(config_source)
    
    def run_task_sheet_from_config(self, config_source):
        return self.config_manager.run_task_sheet_from_config(config_source)
    


   
