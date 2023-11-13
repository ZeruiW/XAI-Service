from xai_sdk.xai_sdk.xai_sdk import TaskPublisherClient
import json

sdk = TaskPublisherClient(base_url="http://127.0.0.1:5006")

# Activate Publisher
#sdk.activate_publisher("http://127.0.0.1:5006")

# Register Services
#sdk.register_service_from_config()

#Get Registered services Info
#sdk.get_registered_services()

#Create and Run Task Sheets
#sdk.create_and_run_task_sheet_from_config()

#Get Task sheets Info
#sdk.fetch_task_sheet_info()

#Create and run pipelines paralelly
sdk.create_and_run_pipeline_from_config()


# # Register services
# sdk.register(executor_endpoint_url="http://127.0.0.1:5009/azure_blob", executor_type="db", 
#              executor_info={"exp_name": "db"})

# sdk.register(executor_endpoint_url="http://127.0.0.1:5001/resnet50", executor_type="model", 
#              executor_info={"exp_name": "resnet50"})

# sdk.register(executor_endpoint_url="http://127.0.0.1:5003/xai/pt_cam", executor_type="xai", 
#              executor_info={"exp_name": "grad-cam"})

# sdk.register(executor_endpoint_url="http://127.0.0.1:5004/evaluation", executor_type="evaluation", 
#              executor_info={"exp_name": "eval"})

# # Get List of Registered Executors
# sdk.get_registered_executor_info()



# # Create Task Sheet
# xai_payload = {
#     "task_type": "xai",
#     "model_service_executor_id": "XSQE091Q9C",
#     "db_service_executor_id": "SR2N17QLPX",
#     "xai_service_executor_id": "BSTEVWAH7X",
#     "task_parameters": json.dumps({
#                 "method_name": "grad-cam",
#                 "data_set_name": "imagenet1000",
#                 "data_set_group_name": "g0",
#                 "model_name": "resnet50",
#                 "executor_config": {
#                     "use_pytorch_multiprocess": True
#                 }
#     }),
#     "task_sheet_name": 'xai1'
# }

# xai_task_sheet_id = sdk.create_task_sheet(xai_payload, task_type = "XAI")

# # Run Task from Task Sheet
# xai_task_ticket_id = sdk.run_task_sheet(xai_task_sheet_id, task_type = "XAI")

# #sdk.poll_task_status(xai_task_ticket_id)

# eval_payload = {
#     "task_type": "evaluation",
#     "model_service_executor_id": "XSQE091Q9C",
#     "db_service_executor_id": "SR2N17QLPX",
#     "xai_service_executor_id": "BSTEVWAH7X",
#     "evaluation_service_executor_id": "ICM0RXBK5A",
#     "task_parameters": json.dumps({
#                         "explanation_task_ticket": xai_task_ticket_id
#                     }),
#     "task_sheet_name": 'eval1'
# }

# eval_task_sheet_id = sdk.create_task_sheet(eval_payload, task_type = "Evaluation")

# # Run Task from Task Sheet
# eval_task_ticket_id = sdk.run_task_sheet(eval_task_sheet_id, task_type = "Evaluation")

# #Fetch Task Sheet Info
# sdk.fetch_task_sheet_info()

# # Create pipeline
# pipeline_id = sdk.create_pipeline("pipeline1", "U9BWJUDACKW97VK", "J4WS7QKHE8PGYAB")
# print(f"Created pipeline with ID: {pipeline_id}")

# # Run pipeline
# response_run_pipeline = sdk.run_pipeline(pipeline_id)
# print(f"Running pipeline successfully with the Id: {response_run_pipeline}")


#--------------------Config function calls--------------------------------




















# # Delete pipeline
# response_delete_pipeline = sdk.delete_pipeline("some_pipeline_id")

# # Get all pipelines
# response_get_all_pipelines = sdk.get_all_pipelines()

# # Delete Task sheet
# response_delete_task_sheet = sdk.delete_task_sheet("some_task_sheet_id")

# # GET Task Sheet
# response_get_task_sheet = sdk.get_task_sheet()

# # GET Task Sheet by task_sheet_id
# response_get_task_sheet_by_id = sdk.get_task_sheet_by_task_sheet_id(["list_of_task_sheet_ids"])

# # Get Task info from task_ticket_id or task_sheet_id
# response_get_task = sdk.get_task("some_task_ticket", "some_task_sheet_id")

# # Get Task Result
# response_task_result = sdk.task_result("some_task_ticket")

# # Update Task status
# response_update_task_status = sdk.update_task_status("some_task_ticket", "some_task_status", {"running_info_key": "running_info_value"})

# # Stop task
# response_stop_task = sdk.stop_task("some_task_ticket")

# # Delete task
# response_delete_task = sdk.delete_task("some_task_ticket")
