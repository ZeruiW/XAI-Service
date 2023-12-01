from xai_sdk import TaskPublisherClient

sdk = TaskPublisherClient(base_url="http://publisher_endpoint_url")

# Activate Publisher
#sdk.activate_publisher("http://publisher_endpoint_url")

# Register Services
#sdk.register_service_from_config()

# Get Registered services Info
#sdk.get_registered_services()

# Create and Run Task Sheets
#sdk.create_and_run_task_sheet_from_config()

# Get Task sheets Info
#sdk.fetch_task_sheet_info()

# Create and run pipelines paralelly
#sdk.create_and_run_pipeline_from_config()

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
#sdk.task_result("nyEuJA8KvUnmhtn.6KGCOFN88Q")

# Stop task
#sdk.stop_task("some_task_ticket")

# Delete task
#sdk.delete_task("some_task_ticket")