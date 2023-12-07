import sys
sys.path.append('/Users/harivinayak/Developer/Research_Project/my-sdk/XAI-Service/backend')


#from xai_sdk.xai_sdk import PublisherManager, TaskSheetManager, TaskManager, PipelineManager, ConfigBasedManager

from xai_sdk.xai_sdk.sdk_interface import SDKInterface

base_url = "http://35.185.126.177:5006"

sdk = SDKInterface(base_url)

# # Create instances of each manager
# publisher_manager = PublisherManager(base_url)
# task_sheet_manager = TaskSheetManager(base_url)
# task_manager = TaskManager(base_url)
# pipeline_manager = PipelineManager(base_url)

# # Create an instance of ConfigBasedManager with references to other managers
# config_manager = ConfigBasedManager(base_url, publisher_manager, task_sheet_manager, task_manager, pipeline_manager)

# File-based configuration example
#config_file_path = "sdk_config_dev.yaml"

# Activate Publisher
#publisher_manager.activate_publisher("http://35.185.126.177:5006")
sdk.activate_publisher("http://35.185.126.177:5006")

# Register Services
#config_manager.register_service_from_config(config_file_path)
#sdk.register_service_from_config(config_file_path)

# Get Registered services Info
#publisher_manager.get_registered_services()
#sdk.get_registered_services()

# Create and Run Task Sheets
#config_manager.create_and_run_task_sheet_from_config(config_file_path)
#sdk.create_and_run_task_sheet_from_config(config_file_path)

# Get Task sheets Info
#task_sheet_manager.fetch_task_sheet_info()
#sdk.fetch_task_sheet_info()

yaml_config_string = """
pipelines:
  - name: "pipeline2"
    xai_task_sheet_id: "8IU7NIAVYWJ0D0L"
    evaluation_task_sheet_id: "VKNWMX6I9O2OVHF"
"""

# Create and run pipelines parallely
#config_manager.create_and_run_pipeline_from_config(config_file_path)
sdk.create_and_run_pipeline_from_config(yaml_config_string)

# Get Pipelines Info
#pipeline_manager.get_all_pipelines()

#sdk.get_all_pipelines()

# Delete pipeline
#pipeline_manager.delete_pipeline("some_pipeline_id")

#------------------------------Task Sheet Functions--------------------

# Delete Task sheet
#task_sheet_manager.delete_task_sheet("some_task_sheet_id")

# GET Task Sheet by task_sheet_id
#task_sheet_manager.get_task_sheet_by_task_sheet_id(["some_task_sheet_id"])

#----------------------------- Task functions----------------------

# Get Task Result
#task_manager.task_result("some_task_ticket_id")

# Stop task
#task_manager.stop_task("some_task_ticket")

# Delete task
#task_manager.delete_task("some_task_ticket")
