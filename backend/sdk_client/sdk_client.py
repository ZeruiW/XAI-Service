import sys
sys.path.append('/Users/harivinayak/Developer/Research_Project/my-sdk/XAI-Service/backend')

from xai_sdk.xai_sdk.sdk_interface import SDKInterface

sdk = SDKInterface(base_url = "http://35.185.126.177:5006")

# File-based configuration example
config_file_path = "sdk_config_dev.yaml"

# String-based configuration example
yaml_config_string = """
pipelines:
  - name: "pipeline2"
    xai_task_sheet_id: "8IU7NIAVYWJ0D0L"
    evaluation_task_sheet_id: "VKNWMX6I9O2OVHF"
"""

# Activate Publisher
sdk.activate_publisher("http://35.185.126.177:5006")

# Register Service
#sdk.register_service_from_config(config_file_path)

# Get Registered services Info
#sdk.get_registered_services()

# Create and Run Task Sheets
#sdk.create_and_run_task_sheet_from_config(config_file_path)

# Get Task sheets Info
#sdk.fetch_task_sheet_info()

# Create and run pipelines parallely
#sdk.create_and_run_pipeline_from_config(yaml_config_string)

# Get Pipelines Info
#sdk.get_all_pipelines()

# Delete pipeline
#sdk.delete_pipeline("some_pipeline_id")

#------------------------------Task Sheet Functions--------------------

# Delete Task sheet
#sdk.delete_task_sheet("some_task_sheet_id")

# GET Task Sheet by task_sheet_id
#sdk.get_task_sheet_by_task_sheet_id(["some_task_sheet_id"])

#----------------------------- Task functions----------------------

# Get Task Result
#sdk.task_result("some_task_ticket_id")

# Stop task
#sdk.stop_task("some_task_ticket")

# Delete task
#sdk.delete_task("some_task_ticket")
